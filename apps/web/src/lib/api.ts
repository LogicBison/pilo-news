import type { Locale } from "@/lib/i18n";

export interface Meta {
  request_id: string;
  locale: Locale | string;
  language: "en" | "es" | string;
  fallback: boolean;
  generated_at: string;
  next_cursor: string | null;
  total?: number;
}

export interface Topic {
  slug: string;
  label: string;
  weight?: number;
  count?: number;
}

export interface Source {
  name: string;
  url: string;
  language: string;
}

export interface ArticleCard {
  id: string;
  title: string;
  summary: string | null;
  excerpt: string | null;
  url: string;
  publisher: string;
  published_at: string;
  topics: Topic[];
  language: string;
  verification: string;
  corroboration: number;
}

export interface ArticleDetail extends ArticleCard {
  related: ArticleCard[];
}

export interface IndustryTheme {
  primary: string;
  accent: string;
  bg: string;
  surface: string;
  text: string;
  muted: string;
  border: string;
  radius: string;
  font_heading: string;
  font_body: string;
  layout: "editorial" | "professional" | "academic";
}

export interface CtaQualificationOption {
  value: string;
  label: Record<string, string>;
}

export interface CtaQualification {
  label?: Record<string, string>;
  required?: boolean;
  options?: CtaQualificationOption[];
}

export interface CtaConfig {
  kind?: "consultation" | "brief";
  /** Gated reference asset slug this channel offers (R16: comes from channel config). */
  asset?: string;
  headline?: Record<string, string>;
  body?: Record<string, string>;
  label?: Record<string, string>;
  secondary_label?: Record<string, string>;
  qualify?: CtaQualification;
}

export interface Industry {
  slug: string;
  name: string;
  code: string;
  tagline: string;
  locales: string[];
  theme: IndustryTheme;
  theme_summary: { primary: string; accent: string; layout: string };
  disclaimer: string;
  disclaimers: Record<string, string>;
  cta: CtaConfig;
  timezone: string;
}

export interface IndustrySummary {
  slug: string;
  name: string;
  code: string;
  locales: string[];
  theme_summary: { primary: string; accent: string; layout: string };
}

export interface BundleIndustry extends Industry {
  slug: string;
}

export interface BundleData {
  generated_at: string;
  language: "en" | "es";
  fallback: boolean;
  total: number;
  splash: ArticleCard[];
  columns: { title: string | null; items: ArticleCard[] }[];
  items: ArticleCard[];
  topics: Topic[];
  sources: Source[];
  featured: { lead: ArticleCard | null; favorites: ArticleCard[] };
  ai_summary: string | null;
  retention_max_age_days: number;
  industry: BundleIndustry;
}

export interface SplashData {
  lead: ArticleCard | null;
  favorites: ArticleCard[];
}

export type ApiResult<T> =
  | { ok: true; data: T; meta: Meta }
  | { ok: false; status: number; reason: string };

const API_BASE = process.env.API_INTERNAL_URL ?? "http://api:8080";

function apiPath(path: string): string {
  return `${API_BASE.replace(/\/$/, "")}/v1${path}`;
}

const isDev = process.env.NODE_ENV !== "production";

async function apiGet<T>(path: string, revalidate = 60): Promise<ApiResult<T>> {
  try {
    const response = await fetch(apiPath(path), {
      headers: { accept: "application/json" },
      ...(isDev ? { cache: "no-store" as const } : { next: { revalidate } }),
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) {
      return { ok: false, status: response.status, reason: `api-status-${response.status}` };
    }
    const body = (await response.json()) as { data: T; meta: Meta };
    return { ok: true, data: body.data, meta: body.meta };
  } catch {
    return { ok: false, status: 0, reason: "api-unavailable" };
  }
}

export function getIndustries(locale: Locale): Promise<ApiResult<IndustrySummary[]>> {
  return apiGet<IndustrySummary[]>(`/industries?locale=${locale}`, 300);
}

export function getIndustry(slug: string, locale: Locale): Promise<ApiResult<Industry>> {
  return apiGet<Industry>(`/industries/${encodeURIComponent(slug)}?locale=${locale}`, 300);
}

export function getBundle(slug: string, locale: Locale): Promise<ApiResult<BundleData>> {
  return apiGet<BundleData>(
    `/news/bundle?industry=${encodeURIComponent(slug)}&locale=${locale}`,
    60,
  );
}

export function getArticle(
  slug: string,
  id: string,
  locale: Locale,
): Promise<ApiResult<ArticleDetail>> {
  return apiGet<ArticleDetail>(
    `/news/${encodeURIComponent(id)}?industry=${encodeURIComponent(slug)}&locale=${locale}`,
    120,
  );
}

export function getSplash(slug: string, locale: Locale): Promise<ApiResult<SplashData>> {
  return apiGet<SplashData>(
    `/news/splash?industry=${encodeURIComponent(slug)}&locale=${locale}`,
    60,
  );
}

export function getNews(
  slug: string,
  locale: Locale,
  options: { q?: string; topic?: string; limit?: number } = {},
): Promise<ApiResult<ArticleCard[]>> {
  const params = new URLSearchParams({ industry: slug, locale });
  if (options.q) params.set("q", options.q);
  if (options.topic) params.set("topic", options.topic);
  if (options.limit) params.set("limit", String(options.limit));
  return apiGet<ArticleCard[]>(`/news?${params.toString()}`, 60);
}

export function getTopics(slug: string, locale: Locale): Promise<ApiResult<Topic[]>> {
  return apiGet<Topic[]>(
    `/topics?industry=${encodeURIComponent(slug)}&locale=${locale}`,
    120,
  );
}

export function getSources(slug: string, locale: Locale): Promise<ApiResult<Source[]>> {
  return apiGet<Source[]>(
    `/sources?industry=${encodeURIComponent(slug)}&locale=${locale}`,
    300,
  );
}
