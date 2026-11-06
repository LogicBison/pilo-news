import type { Locale } from "@/lib/i18n";

/**
 * Gated reference assets (offer S3). Only assets with an owner and a publishing
 * date ship here; an asset that does not exist yet is a waitlist, not a promise.
 */
export interface AssetDefinition {
  slug: string;
  title: Record<Locale, string>;
  body: Record<Locale, string>;
  /** Waitlist until the first issue exists. */
  waitlist: boolean;
}

export const ASSETS: AssetDefinition[] = [
  {
    slug: "legal-regulatory-calendar",
    waitlist: true,
    title: {
      en: "Legal regulatory calendar",
      es: "Calendario regulatorio legal",
    },
    body: {
      en: "A dated list of the filings, comment windows, and compliance deadlines that apply to law firms and in-house teams. Quarterly, plain language, free. We email it when the first issue is ready.",
      es: "Una lista con fechas de presentaciones, plazos de comentarios y vencimientos de cumplimiento para despachos y equipos internos. Trimestral, en lenguaje claro, gratis. Te lo enviamos cuando esté lista la primera edición.",
    },
  },
];

export function assetFor(slug: string): AssetDefinition | undefined {
  return ASSETS.find((asset) => asset.slug === slug);
}
