/**
 * Request-scoped URL helpers. Every canonical URL, feed link and internal link
 * goes through this module so a channel served from a subdomain never emits a
 * `/<slug>` prefix and an apex/path deployment keeps working unchanged.
 */

import { headers } from "next/headers";

import { CHANNEL_HEADER, channelDomain, channelFromHost, originFor, splitHost } from "@/lib/hosts";
import { localePath, type Locale } from "@/lib/i18n";

/** Deployment origin used when the request host is not scoped to a domain. */
export const SITE_URL = (process.env.APP_BASE_URL ?? "http://localhost:3000").replace(/\/$/, "");

export interface RequestSite {
  /** Absolute origin without a trailing slash, e.g. `https://stem-cell.heraldfox.com`. */
  origin: string;
  /** Host without the port. */
  host: string;
  /** `https` or `http`, from the proxy hint. */
  scheme: string;
  /** Port from the request host, or null. */
  port: string | null;
  /** Channel slug this host serves, or null on a shared/apex host. */
  channel: string | null;
}

export async function requestSite(): Promise<RequestSite> {
  const requestHeaders = await headers();
  const rawHost = requestHeaders.get("host") ?? requestHeaders.get("x-forwarded-host") ?? "";
  const { host, port } = splitHost(rawHost);
  const domain = channelDomain();
  const proxyChannel = requestHeaders.get(CHANNEL_HEADER);
  const channel = proxyChannel && proxyChannel !== "-" ? proxyChannel : channelFromHost(host, domain);
  const forwarded = requestHeaders.get("x-forwarded-proto");

  // Domain-scoped deployments build absolute URLs from the request host, so a
  // channel subdomain is canonical for itself. Path deployments keep using
  // APP_BASE_URL, which is what the e2e suite and dev stack rely on.
  const origin = domain && host ? originFor(rawHost, forwarded) : SITE_URL;
  const scheme = origin.slice(0, origin.indexOf("://"));

  return { origin, host, scheme, port, channel };
}

/**
 * Canonical origin for a channel: its own subdomain when a channel domain is
 * configured, the current origin otherwise. This is what canonical tags, Open
 * Graph URLs and structured data point at — never the apex compat copy.
 */
export async function channelOrigin(industry: string): Promise<string> {
  const site = await requestSite();
  const domain = channelDomain();
  if (!domain || !site.host) return site.origin;
  const port = site.port ? `:${site.port}` : "";
  return `${site.scheme}://${industry}.${domain}${port}`;
}

/**
 * Link base for the host the request actually arrived on: `""` on the channel's
 * own subdomain, `"/stem-cell"` on the apex and in path mode. Navigation stays
 * on the current host; only the canonical moves.
 */
export async function channelBase(industry: string): Promise<string> {
  const { channel } = await requestSite();
  return channel === industry ? "" : `/${industry}`;
}

/** Locale-aware path to a page inside a channel. */
export async function channelPath(locale: Locale, industry: string, path = ""): Promise<string> {
  const base = await channelBase(industry);
  const tail = path && path !== "/" ? (path.startsWith("/") ? path : `/${path}`) : "";
  return localePath(locale, `${base}${tail}` || "/");
}

export async function absoluteUrl(path: string): Promise<string> {
  const { origin } = await requestSite();
  return `${origin}${path.startsWith("/") ? path : `/${path}`}`;
}
