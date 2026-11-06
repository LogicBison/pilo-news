/**
 * Gated reference assets (offer S3). Only assets with an owner and a publishing
 * date ship here; an asset that does not exist yet is a waitlist, not a promise.
 *
 * Copy lives in `messages/{locale}.json` under `asset.<slug>.title|body`; this
 * registry resolves the slug a channel names in `cta.asset` (channel config).
 */
export interface AssetDefinition {
  slug: string;
  titleKey: string;
  bodyKey: string;
  /** Waitlist until the first issue exists. */
  waitlist: boolean;
}

export const ASSETS: AssetDefinition[] = [
  {
    slug: "legal-regulatory-calendar",
    titleKey: "asset.legal-regulatory-calendar.title",
    bodyKey: "asset.legal-regulatory-calendar.body",
    waitlist: true,
  },
  {
    slug: "cybersecurity-kev-digest",
    titleKey: "asset.cybersecurity-kev-digest.title",
    bodyKey: "asset.cybersecurity-kev-digest.body",
    waitlist: true,
  },
];

export function assetFor(slug: string): AssetDefinition | undefined {
  return ASSETS.find((asset) => asset.slug === slug);
}
