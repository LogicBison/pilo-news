import { NextResponse, type NextRequest } from "next/server";

const SUPPORTED = ["en", "es"] as const;
type Locale = (typeof SUPPORTED)[number];

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

function withLocaleHeader(request: NextRequest, locale: Locale): Headers {
  const headers = new Headers(request.headers);
  headers.set("x-sn-locale", locale);
  return headers;
}

export function middleware(request: NextRequest): NextResponse {
  const { pathname, search } = request.nextUrl;

  if (pathname === "/en" || pathname.startsWith("/en/")) {
    const url = request.nextUrl.clone();
    url.pathname = pathname.replace(/^\/en/, "") || "/";
    return withSecurity(NextResponse.redirect(url, 308));
  }

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
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml|skins/|photos/|api/).*)"],
};
