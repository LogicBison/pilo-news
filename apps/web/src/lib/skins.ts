export type SkinKey =
  | "chambers"
  | "terminal"
  | "sanctuary"
  | "campus"
  | "network"
  | "sentinel"
  | "lab"
  | "forge"
  | "grid"
  | "market";

export type HeroVariant = "split" | "ledger" | "poster" | "ribbon";
export type RuleStyle = "double" | "hairline" | "dotted" | "dashed" | "none" | "accent";
export type EyebrowStyle = "serif" | "mono" | "numbered" | "soft";
export type CtaPanel = "sidebar" | "banner" | "inset" | "corner" | "open";
export type ListLayout = "grid3" | "grid2" | "stack" | "magazine";
export type BarLayout = "split" | "center";

export interface Skin {
  key: SkinKey;
  /** Human name, used in docs and dev tools. */
  label: string;
  hero: HeroVariant;
  /** Public path to the generated motif SVG. */
  motif: string;
  /** Public path to the generated illustration band SVG (fallback art). */
  scene: string;
  /** Photography: 1600px and 800px crops. */
  photo: string;
  photoSmall: string;
  /** Attribution line when the licence requires it (CC BY / BY-SA). */
  credit?: { label: string; href: string };
  /** Corner language; overrides the channel theme radius. */
  radius: string;
  rule: RuleStyle;
  eyebrow: EyebrowStyle;
  cta: CtaPanel;
  /** Favourites strip: static grid or scroll-snap rail. */
  rail: "static" | "scroll";
  /** Coverage grid rhythm. */
  list: ListLayout;
  /** App bar arrangement. */
  bar: BarLayout;
  /** Operator reference sites this skin draws on. */
  references: string[];
}

const CHAMBERS: Skin = {
  key: "chambers",
  label: "Chambers",
  hero: "split",
  motif: "/skins/legal/motif.svg",
  scene: "/skins/legal/scene.svg",
  photo: "/photos/legal/band.jpg",
  photoSmall: "/photos/legal/band-800.jpg",
  radius: "6px",
  rule: "double",
  eyebrow: "serif",
  cta: "sidebar",
  rail: "static",
    list: "magazine",
    bar: "split",
  references: ["ellevest", "nerdwallet"],
};

const TERMINAL: Skin = {
  key: "terminal",
  label: "Terminal",
  hero: "ledger",
  motif: "/skins/financial/motif.svg",
  scene: "/skins/financial/scene.svg",
  photo: "/photos/financial/band.jpg",
  photoSmall: "/photos/financial/band-800.jpg",
  credit: { label: "Photo: Arild Vågen · CC BY-SA 4.0", href: "https://commons.wikimedia.org/wiki/File:New_York_Stock_Exchange_August_2017_02.jpg" },
  radius: "4px",
  rule: "hairline",
  eyebrow: "mono",
  cta: "banner",
  rail: "scroll",
    list: "grid2",
    bar: "split",
  references: ["databox", "nerdwallet"],
};

const SANCTUARY: Skin = {
  key: "sanctuary",
  label: "Sanctuary",
  hero: "split",
  motif: "/skins/behavioral-health/motif.svg",
  scene: "/skins/behavioral-health/scene.svg",
  photo: "/photos/behavioral-health/band.jpg",
  photoSmall: "/photos/behavioral-health/band-800.jpg",
  radius: "18px",
  rule: "none",
  eyebrow: "soft",
  cta: "open",
  rail: "static",
    list: "magazine",
    bar: "center",
  references: ["ellevest", "charitywater"],
};

const CAMPUS: Skin = {
  key: "campus",
  label: "Campus",
  hero: "ribbon",
  motif: "/skins/education/motif.svg",
  scene: "/skins/education/scene.svg",
  photo: "/photos/education/band.jpg",
  photoSmall: "/photos/education/band-800.jpg",
  radius: "10px",
  rule: "dotted",
  eyebrow: "numbered",
  cta: "corner",
  rail: "static",
    list: "grid2",
    bar: "center",
  references: ["hubspot", "databox"],
};

const NETWORK: Skin = {
  key: "network",
  label: "Network",
  hero: "poster",
  motif: "/skins/logistics/motif.svg",
  scene: "/skins/logistics/scene.svg",
  photo: "/photos/logistics/band.jpg",
  photoSmall: "/photos/logistics/band-800.jpg",
  radius: "8px",
  rule: "dashed",
  eyebrow: "mono",
  cta: "banner",
  rail: "scroll",
    list: "grid2",
    bar: "split",
  references: ["basecamp", "calendly"],
};

const SENTINEL: Skin = {
  key: "sentinel",
  label: "Sentinel",
  hero: "ledger",
  motif: "/skins/cybersecurity/motif.svg",
  scene: "/skins/cybersecurity/scene.svg",
  photo: "/photos/cybersecurity/band.jpg",
  photoSmall: "/photos/cybersecurity/band-800.jpg",
  credit: { label: "Photo: BalticServers.com · CC BY-SA 3.0", href: "https://commons.wikimedia.org/wiki/File:BalticServers_data_center.jpg" },
  radius: "2px",
  rule: "accent",
  eyebrow: "mono",
  cta: "sidebar",
  rail: "static",
    list: "grid2",
    bar: "split",
  references: ["semrush", "userpilot"],
};

const LAB: Skin = {
  key: "lab",
  label: "Lab",
  hero: "ribbon",
  motif: "/skins/stem-cell/motif.svg",
  scene: "/skins/stem-cell/scene.svg",
  photo: "/photos/stem-cell/band.jpg",
  photoSmall: "/photos/stem-cell/band-800.jpg",
  credit: { label: "Photo: Gannu03 · CC BY-SA 4.0", href: "https://commons.wikimedia.org/wiki/File:Disposable_Pipette_Tips_in_Laboratory_Tip_Boxes.jpg" },
  radius: "14px",
  rule: "hairline",
  eyebrow: "serif",
  cta: "inset",
  rail: "static",
    list: "magazine",
    bar: "center",
  references: ["ellevest", "typeform"],
};


const FORGE: Skin = {
  key: "forge",
  label: "Forge",
  hero: "poster",
  motif: "/skins/manufacturing/motif.svg",
  scene: "/skins/manufacturing/scene.svg",
  photo: "/photos/manufacturing/band.jpg",
  photoSmall: "/photos/manufacturing/band-800.jpg",
  credit: {
    label: "Photo: Marek Ślusarczyk · CC BY 3.0",
    href: "https://commons.wikimedia.org/wiki/File:002_Production_line_-_car_assembly_line_in_General_Motors_Manufacturing_Poland_-_Gliwice,_Poland.jpg",
  },
  radius: "3px",
  rule: "hairline",
  eyebrow: "mono",
  cta: "banner",
  rail: "scroll",
  list: "grid2",
  bar: "split",
  references: ["leadpages", "hubspot"],
};

const GRID: Skin = {
  key: "grid",
  label: "Grid",
  hero: "ledger",
  motif: "/skins/energy/motif.svg",
  scene: "/skins/energy/scene.svg",
  photo: "/photos/energy/band.jpg",
  photoSmall: "/photos/energy/band-800.jpg",
  credit: {
    label: "Photo: Kkiefuik · CC BY 4.0",
    href: "https://commons.wikimedia.org/wiki/File:Transmission_Lines_at_Sunset.jpg",
  },
  radius: "5px",
  rule: "accent",
  eyebrow: "mono",
  cta: "sidebar",
  rail: "static",
  list: "grid2",
  bar: "split",
  references: ["databox", "semrush"],
};

const MARKET: Skin = {
  key: "market",
  label: "Market",
  hero: "split",
  motif: "/skins/retail/motif.svg",
  scene: "/skins/retail/scene.svg",
  photo: "/photos/retail/band.jpg",
  photoSmall: "/photos/retail/band-800.jpg",
  credit: {
    label: "Photo: Arkke · CC BY-SA 4.0",
    href: "https://commons.wikimedia.org/wiki/File:Coffee_in_K-citymarket_J%C3%A4rvenp%C3%A4%C3%A4.jpg",
  },
  radius: "12px",
  rule: "dotted",
  eyebrow: "serif",
  cta: "inset",
  rail: "scroll",
  list: "magazine",
  bar: "center",
  references: ["hubspot", "ellevest"],
};

export const SKINS: Record<string, Skin> = {
  legal: CHAMBERS,
  financial: TERMINAL,
  "behavioral-health": SANCTUARY,
  education: CAMPUS,
  logistics: NETWORK,
  cybersecurity: SENTINEL,
  "stem-cell": LAB,
  manufacturing: FORGE,
  energy: GRID,
  retail: MARKET,
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
