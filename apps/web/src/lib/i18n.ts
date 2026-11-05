import en from "@/messages/en.json";
import es from "@/messages/es.json";

export type Locale = "en" | "es";
export const LOCALES: readonly Locale[] = ["en", "es"];
export const DEFAULT_LOCALE: Locale = "en";

const CATALOGS: Record<Locale, unknown> = { en, es };

export function isLocale(value: string | undefined): value is Locale {
  return value === "en" || value === "es";
}

export function resolveLocale(value: string | undefined): Locale {
  return isLocale(value) ? value : DEFAULT_LOCALE;
}

export function t(locale: Locale, key: string, values?: Record<string, string | number>): string {
  const segments = key.split(".");
  let node: unknown = CATALOGS[locale];
  for (const segment of segments) {
    if (typeof node !== "object" || node === null) {
      node = undefined;
      break;
    }
    node = (node as Record<string, unknown>)[segment];
  }
  let text = typeof node === "string" ? node : key;
  if (values) {
    for (const [name, value] of Object.entries(values)) {
      text = text.replaceAll(`{${name}}`, String(value));
    }
  }
  return text;
}

export function formatDate(value: string, locale: Locale, timeZone = "America/El_Salvador"): string {
  const intlLocale = locale === "es" ? "es-ES" : "en-US";
  try {
    return new Intl.DateTimeFormat(intlLocale, {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone,
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function localePath(locale: Locale, path: string): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return locale === "es" ? `/es${clean === "/" ? "" : clean}` : clean;
}

export function stripLocale(pathname: string): { locale: Locale; path: string } {
  if (pathname === "/es" || pathname.startsWith("/es/")) {
    return { locale: "es", path: pathname.slice(3) || "/" };
  }
  return { locale: "en", path: pathname };
}
