/**
 * Host → channel resolution, shared by the edge middleware and the Node
 * runtime (canonical URLs, sitemaps, feeds). Pure functions only: this module
 * is imported from middleware, so it must not touch `next/headers` or Node APIs.
 *
 * Two deployment shapes are supported by the same tree:
 *
 *   path mode (dev)      http://localhost:3000/stem-cell
 *   channel mode (prod)  https://stem-cell.heraldfox.com
 *
 * Channel mode is opt-in: it activates when `SN_CHANNEL_DOMAIN` is set, or when
 * the reverse proxy forwards `X-SN-Channel`. Path mode stays the default so a
 * dev stack and the existing URL surface keep working untouched.
 */

/** Request header carrying the channel slug resolved by the reverse proxy. */
export const CHANNEL_HEADER = "x-sn-channel";

/** Proxy value meaning "this host is the apex/app host, not a channel". */
export const APEX_MARKER = "-";

/**
 * Subdomains the platform owns. They are never treated as channel slugs so the
 * admin console and the apex site keep a single, stable origin.
 */
export const RESERVED_SUBDOMAINS: readonly string[] = [
  "www",
  "admin",
  "api",
  // Apex routes: a channel may never take one of these slugs, or the static
  // segment would shadow the desk (or the reverse).
  "services",
  "pricing",
  "privacy",
  "terms",
  "app",
  "assets",
  "cdn",
  "static",
  "mail",
  "smtp",
  "status",
  "docs",
];

/** `host:port` → host without the port, lowercased. Handles `[::1]:3000`. */
export function splitHost(value: string | null | undefined): {
  host: string;
  port: string | null;
} {
  const raw = (value ?? "").trim().toLowerCase();
  if (!raw) return { host: "", port: null };
  if (raw.startsWith("[")) {
    const end = raw.indexOf("]");
    if (end === -1) return { host: raw, port: null };
    const host = raw.slice(1, end);
    const port = raw.slice(end + 1).replace(/^:/, "");
    return { host, port: port || null };
  }
  const at = raw.lastIndexOf(":");
  if (at === -1) return { host: raw, port: null };
  return { host: raw.slice(0, at), port: raw.slice(at + 1) || null };
}

/**
 * Channel domain from the environment, normalized (`heraldfox.com`).
 *
 * Resolution order:
 *   1. `SN_CHANNEL_DOMAIN` — explicit, also what dev sets to `localhost` so
 *      `http://stem-cell.localhost:43991` works without an edge proxy.
 *   2. `APP_DOMAIN` when `APP_ENV=prd` — production is subdomain-based by
 *      definition, so a single variable drives the edge, the app and nginx.
 *   3. empty — path mode (`/<slug>` URLs).
 */
export function channelDomain(): string {
  const explicit = normalizeDomain(process.env.SN_CHANNEL_DOMAIN);
  if (explicit) return explicit;
  if ((process.env.APP_ENV ?? "").toLowerCase() === "prd") {
    return normalizeDomain(process.env.APP_DOMAIN);
  }
  return "";
}

function normalizeDomain(value: string | undefined): string {
  return (value ?? "")
    .trim()
    .toLowerCase()
    .replace(/^\w+:\/\//, "")
    .replace(/\/.*$/, "")
    .replace(/^\.+/, "")
    .replace(/\.+$/, "")
    .replace(/:\d+$/, "");
}

/** `stem-cell.heraldfox.com` + `heraldfox.com` → `stem-cell`, else null. */
export function channelFromHost(host: string, domain: string): string | null {
  if (!host || !domain) return null;
  const suffix = `.${domain}`;
  if (!host.endsWith(suffix)) return null;
  const label = host.slice(0, -suffix.length);
  // Single-label subdomains only: `a.b.example.com` is not a channel.
  if (!label || label.includes(".")) return null;
  if (RESERVED_SUBDOMAINS.includes(label)) return null;
  return label;
}

/** True when this host is the apex (or www) host of the channel domain. */
export function isApexHost(host: string, domain: string): boolean {
  if (!host || !domain) return false;
  return host === domain || host === `www.${domain}`;
}

/**
 * Absolute origin for a request, given the proxy's protocol hint.
 * Falls back to https in production, http otherwise.
 */
export function originFor(rawHost: string, forwardedProto: string | null): string {
  const scheme =
    forwardedProto?.split(",")[0]?.trim() ||
    (process.env.NODE_ENV === "production" ? "https" : "http");
  return `${scheme}://${rawHost}`;
}

/** Drop a leading `/<channel>` segment so links keep one canonical shape. */
export function stripChannel(pathname: string, channel: string): string {
  if (pathname === `/${channel}`) return "/";
  if (pathname.startsWith(`/${channel}/`)) return pathname.slice(channel.length + 1);
  return pathname;
}
