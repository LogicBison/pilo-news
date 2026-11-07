import type { Metadata } from "next";

import type { ArticleDetail, ArticleCard, Industry } from "@/lib/api";
import { stripChannel } from "@/lib/hosts";
import { localePath, type Locale } from "@/lib/i18n";
import { channelOrigin, requestSite } from "@/lib/url";

export { absoluteUrl } from "@/lib/url";

export interface PageMetadataOptions {
  title: string;
  description: string;
  /** Channel-relative path including the slug, e.g. `/stem-cell/about`. */
  path: string;
  locale: Locale;
  /** Channel slug. When given, canonicals point at the channel's own host. */
  industry?: string;
  /**
   * Skip the root layout's `%s | <brand>` template. The lobby owns the whole
   * title because it is the network's front door, not a page of a desk.
   */
  absoluteTitle?: boolean;
}

/** Canonical path for the current host: no `/<slug>` prefix on a subdomain. */
function canonicalPath(path: string, industry: string | undefined): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  if (!industry) return clean;
  const stripped = stripChannel(clean, industry);
  return stripped === "/" ? "/" : stripped.replace(/\/$/, "");
}

export async function pageMetadata(options: PageMetadataOptions): Promise<Metadata> {
  const origin = options.industry
    ? await channelOrigin(options.industry)
    : (await requestSite()).origin;
  const path = canonicalPath(options.path, options.industry);
  const en = `${origin}${localePath("en", path)}`;
  const es = `${origin}${localePath("es", path)}`;
  const canonical = options.locale === "es" ? es : en;
  return {
    title: options.absoluteTitle ? { absolute: options.title } : options.title,
    description: options.description,
    alternates: {
      canonical,
      languages: { en, es, "x-default": en },
    },
    openGraph: {
      title: options.title,
      description: options.description,
      url: canonical,
      siteName: "System News",
      locale: options.locale === "es" ? "es_ES" : "en_US",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: options.title,
      description: options.description,
    },
  };
}

export function itemListJsonLd(industry: Industry, items: ArticleCard[]): string {
  return JSON.stringify({
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `${industry.name} - System News`,
    itemListElement: items.slice(0, 10).map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      url: item.url,
      name: item.title,
    })),
  });
}

export function newsArticleJsonLd(
  industry: Industry,
  article: ArticleDetail,
  pageUrl: string,
): string {
  return JSON.stringify({
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.title,
    datePublished: article.published_at,
    url: pageUrl,
    mainEntityOfPage: pageUrl,
    articleSection: industry.name,
    inLanguage: article.language,
    publisher: {
      "@type": "Organization",
      name: article.publisher,
    },
    isBasedOn: article.url,
  });
}
