import type { Industry } from "@/lib/api";
import { DEFAULT_THEME } from "@/lib/theme";

const DISCLAIMERS: Record<string, string> = {
  legal: "News, not legal advice. Attorney advertising. No outcome is guaranteed.",
  financial: "News, not investment advice. Investing involves risk.",
  "behavioral-health": "News, not medical advice. If this is an emergency, call 911.",
  education: "Program details and outcomes vary; verify with the institution.",
  logistics: "Rates and timelines vary by lane and season.",
};

export function fallbackIndustry(slug: string, tagline = "Industry news for professionals."): Industry {
  const name = slug
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
  return {
    slug,
    name,
    code: slug.toUpperCase(),
    tagline,
    locales: ["en", "es"],
    theme: DEFAULT_THEME,
    theme_summary: { primary: DEFAULT_THEME.primary, accent: DEFAULT_THEME.accent, layout: "editorial" },
    disclaimer: DISCLAIMERS[slug] ?? "News, not professional advice.",
    disclaimers: { en: DISCLAIMERS[slug] ?? "News, not professional advice." },
    cta: {
      kind: "consultation",
      headline: { en: "Talk to a vetted professional", es: "Hable con un profesional verificado" },
      body: {
        en: "Tell us what you need. We route qualified requests to an independent partner.",
        es: "Cuéntenos qué necesita. Canalizamos solicitudes calificadas a un socio independiente.",
      },
      label: { en: "Request a consultation", es: "Solicitar una consulta" },
    },
    timezone: "America/El_Salvador",
  };
}
