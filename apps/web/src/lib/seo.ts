import type { Metadata } from "next";

import type { ArticleDetail, ArticleCard, Industry } from "@/lib/api";
import { localePath, type Locale } from "@/lib/i18n";

export const SITE_URL = (process.env.APP_BASE_URL ?? "http://localhost:3000").replace(/\/$/, "");

export function absoluteUrl(path: string): string {
  return `${SITE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export function languageAlternates(path: string): Record<string, string> {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return {
    en: absoluteUrl(clean),
    es: absoluteUrl(`/es${clean}`),
    "x-default": absoluteUrl(clean),
  };
}

export function pageMetadata(options: {
  title: string;
  description: string;
  path: string;
  locale: Locale;
}): Metadata {
  const canonical = absoluteUrl(localePath(options.locale, options.path));
  return {
    title: options.title,
    description: options.description,
    alternates: {
      canonical,
      languages: languageAlternates(options.path),
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
