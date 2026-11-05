export type SkinKey =
  | "chambers"
  | "terminal"
  | "sanctuary"
  | "campus"
  | "network"
  | "sentinel"
  | "lab";

export type HeroVariant = "split" | "ledger" | "poster" | "ribbon";
export type RuleStyle = "double" | "hairline" | "dotted" | "dashed" | "none" | "accent";
export type EyebrowStyle = "serif" | "mono" | "numbered" | "soft";
export type CtaPanel = "sidebar" | "banner" | "inset" | "corner";

export interface Skin {
  key: SkinKey;
  /** Human name, used in docs and dev tools. */
  label: string;
  hero: HeroVariant;
  /** Public path to the generated motif SVG. */
  motif: string;
  /** Corner language; overrides the channel theme radius. */
  radius: string;
  rule: RuleStyle;
  eyebrow: EyebrowStyle;
  cta: CtaPanel;
  /** Favourites strip: static grid or scroll-snap rail. */
  rail: "static" | "scroll";
  /** Operator reference sites this skin draws on. */
  references: string[];
}

const CHAMBERS: Skin = {
  key: "chambers",
  label: "Chambers",
  hero: "split",
  motif: "/skins/legal/motif.svg",
  radius: "6px",
  rule: "double",
  eyebrow: "serif",
  cta: "sidebar",
  rail: "static",
  references: ["ellevest", "nerdwallet"],
};

const TERMINAL: Skin = {
  key: "terminal",
  label: "Terminal",
  hero: "ledger",
  motif: "/skins/financial/motif.svg",
  radius: "4px",
  rule: "hairline",
  eyebrow: "mono",
  cta: "banner",
  rail: "scroll",
  references: ["databox", "nerdwallet"],
};

const SANCTUARY: Skin = {
  key: "sanctuary",
  label: "Sanctuary",
  hero: "split",
  motif: "/skins/behavioral-health/motif.svg",
  radius: "18px",
  rule: "none",
  eyebrow: "soft",
  cta: "inset",
  rail: "static",
  references: ["ellevest", "charitywater"],
};

const CAMPUS: Skin = {
  key: "campus",
  label: "Campus",
  hero: "ribbon",
  motif: "/skins/education/motif.svg",
  radius: "10px",
  rule: "dotted",
  eyebrow: "numbered",
  cta: "corner",
  rail: "static",
  references: ["hubspot", "databox"],
};

const NETWORK: Skin = {
  key: "network",
  label: "Network",
  hero: "poster",
  motif: "/skins/logistics/motif.svg",
  radius: "8px",
  rule: "dashed",
  eyebrow: "mono",
  cta: "banner",
  rail: "scroll",
  references: ["basecamp", "calendly"],
};

const SENTINEL: Skin = {
  key: "sentinel",
  label: "Sentinel",
  hero: "ledger",
  motif: "/skins/cybersecurity/motif.svg",
  radius: "2px",
  rule: "accent",
  eyebrow: "mono",
  cta: "sidebar",
  rail: "static",
  references: ["semrush", "userpilot"],
};

const LAB: Skin = {
  key: "lab",
  label: "Lab",
  hero: "ribbon",
  motif: "/skins/stem-cell/motif.svg",
  radius: "14px",
  rule: "hairline",
  eyebrow: "serif",
  cta: "inset",
  rail: "static",
  references: ["ellevest", "typeform"],
};

export const SKINS: Record<string, Skin> = {
  legal: CHAMBERS,
  financial: TERMINAL,
  "behavioral-health": SANCTUARY,
  education: CAMPUS,
  logistics: NETWORK,
  cybersecurity: SENTINEL,
  "stem-cell": LAB,
};

const LAYOUT_FALLBACK: Record<string, Skin> = {
  editorial: CHAMBERS,
  professional: TERMINAL,
  academic: CAMPUS,
};

/**
 * Resolve the skin for a channel. Unknown slugs (a channel created from a
 * profile with no skin entry) fall back to the layout variant, so a new
 * industry is styled but never identical to an existing one by accident.
 */
export function resolveSkin(slug: string, layout?: string): Skin {
  return SKINS[slug] ?? LAYOUT_FALLBACK[layout ?? ""] ?? CHAMBERS;
}
