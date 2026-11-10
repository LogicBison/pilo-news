import { NextResponse, type NextRequest } from "next/server";

import {
  APEX_MARKER,
  CHANNEL_HEADER,
  channelDomain,
  channelFromHost,
  splitHost,
} from "@/lib/hosts";

const SUPPORTED = ["en", "es"] as const;
type Locale = (typeof SUPPORTED)[number];

/** One origin for the console; channel subdomains never serve `/admin`. */
const ADMIN_PREFIXES = ["/admin", "/es/admin"];

function negotiate(request: NextRequest): Locale {
  const cookie = request.cookies.get("sn_locale")?.value;
  if (cookie === "en" || cookie === "es") return cookie;
  const header = request.headers.get("accept-language") ?? "";
  const candidates = header
    .split(",")
    .map((part, index) => {
      const [tag, ...params] = part.trim().split(";");
      const q = params
        .map((param) => param.trim())
        .find((param) => param.startsWith("q="));
      const quality = q ? Number.parseFloat(q.slice(2)) : 1;
      const base = (tag ?? "").toLowerCase().split("-")[0];
      return { base, quality: Number.isNaN(quality) ? 0 : quality, index };
    })
    .filter((item) => SUPPORTED.includes(item.base as Locale))
    .sort((a, b) => b.quality - a.quality || a.index - b.index);
  const best = candidates[0]?.base;
  return best === "es" ? "es" : "en";
}

function withSecurity(response: NextResponse): NextResponse {
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  const scriptSrc =
    process.env.NODE_ENV === "production"
      ? "'self' 'unsafe-inline'"
      : "'self' 'unsafe-inline' 'unsafe-eval'";
  response.headers.set(
    "Content-Security-Policy",
    `default-src 'self'; script-src ${scriptSrc}; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`,
  );
  if (process.env.APP_ENV === "prd") {
    response.headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
  }
  return response;
}

function withLocaleHeader(request: NextRequest, locale: Locale, channel?: string): Headers {
  const headers = new Headers(request.headers);
  headers.set("x-sn-locale", locale);
  if (channel) {
    // Downstream pages read this to build subdomain-clean links.
    headers.set(CHANNEL_HEADER, channel);
  }
  return headers;
}

/** Absolute origin of a sibling host, keeping the current port in dev. */
function siblingOrigin(request: NextRequest, hostname: string): string {
  const { port } = splitHost(request.headers.get("host"));
  const scheme =
    request.headers.get("x-forwarded-proto")?.split(",")[0]?.trim() ||
    (process.env.NODE_ENV === "production" ? "https" : "http");
  return `${scheme}://${hostname}${port ? `:${port}` : ""}`;
}

function hostLabel(request: NextRequest): string {
  return splitHost(request.headers.get("host")).host;
}

/**
 * Which channel this host serves. The reverse proxy may pre-resolve it with
 * `X-SN-Channel`; otherwise the host is matched against `SN_CHANNEL_DOMAIN`.
 */
function channelOf(request: NextRequest, domain: string): string | null {
  const proxy = request.headers.get(CHANNEL_HEADER);
  if (proxy) return proxy === APEX_MARKER ? null : proxy;
  return channelFromHost(hostLabel(request), domain);
}

function redirectTo(request: NextRequest, origin: string, pathname: string, search: string) {
  const target = new URL(pathname, origin);
  target.search = search;
  return withSecurity(NextResponse.redirect(target, 308));
}

function channelRequest(
  request: NextRequest,
  channel: string,
  pathname: string,
  search: string,
): NextResponse {
  const domain = channelDomain();

  // The console lives on the apex host only, so auth cookies and CSRF state
  // have exactly one origin.
  if (ADMIN_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`))) {
    if (domain) {
      return redirectTo(request, siblingOrigin(request, domain), pathname, search);
    }
  }

  // Accept absolute links that still carry the channel prefix and collapse them
  // to the canonical short form.
  if (pathname === `/${channel}` || pathname.startsWith(`/${channel}/`)) {
    const stripped = pathname === `/${channel}` ? "/" : pathname.slice(channel.length + 1);
    return redirectTo(request, siblingOrigin(request, hostLabel(request)), stripped, search);
  }

  if (pathname === "/es" || pathname.startsWith("/es/")) {
    const rest = pathname.slice(3);
    const url = request.nextUrl.clone();
    url.pathname = `/es/${channel}${rest}`;
    return withSecurity(
      NextResponse.rewrite(url, { request: { headers: withLocaleHeader(request, "es", channel) } }),
    );
  }

  const locale = negotiate(request);
  if (locale === "es") {
    const url = request.nextUrl.clone();
    url.pathname = `/es${pathname}`;
    url.search = search;
    return withSecurity(NextResponse.redirect(url, 302));
  }

  const url = request.nextUrl.clone();
  url.pathname = `/en/${channel}${pathname === "/" ? "" : pathname}`;
  return withSecurity(
    NextResponse.rewrite(url, { request: { headers: withLocaleHeader(request, "en", channel) } }),
  );
}

export function middleware(request: NextRequest): NextResponse {
  const { pathname, search } = request.nextUrl;
  const domain = channelDomain();
  const channel = channelOf(request, domain);

  // `/en/...` is never a canonical URL in either mode.
  if (pathname === "/en" || pathname.startsWith("/en/")) {
    const url = request.nextUrl.clone();
    url.pathname = pathname.replace(/^\/en/, "") || "/";
    url.search = search;
    return withSecurity(NextResponse.redirect(url, 308));
  }

  if (channel) return channelRequest(request, channel, pathname, search);

  if (pathname === "/") {
    // Handled by app/page.tsx (Node runtime) so SN_DEFAULT_INDUSTRY is read at
    // request time instead of being inlined into the edge bundle at build time.
    return withSecurity(NextResponse.next());
  }

  if (pathname === "/es" || pathname.startsWith("/es/")) {
    const response = NextResponse.next({
      request: { headers: withLocaleHeader(request, "es") },
    });
    return withSecurity(response);
  }

  const locale = negotiate(request);
  if (locale === "es") {
    const url = request.nextUrl.clone();
    url.pathname = `/es${pathname}`;
    url.search = search;
    return withSecurity(NextResponse.redirect(url, 302));
  }

  const url = request.nextUrl.clone();
  url.pathname = `/en${pathname}`;
  const response = NextResponse.rewrite(url, {
    request: { headers: withLocaleHeader(request, "en") },
  });
  return withSecurity(response);
}

export const config = {
  // Static assets are excluded so the locale rewrite never turns them into a
  // /en/<path> 404: `brand/` carries the apex logo, `icon.png` and
  // `apple-icon.png` are App Router metadata routes.
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|icon\\.png|apple-icon\\.png|robots.txt|sitemap.xml|skins/|photos/|brand/|api/).*)",
  ],
};
