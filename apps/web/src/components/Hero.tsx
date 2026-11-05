import Link from "next/link";

import type { BundleData } from "@/lib/api";
import { formatDate, localePath, t, type Locale } from "@/lib/i18n";

import { CtaCard } from "./CtaCard";
import { StoryCard } from "./StoryCard";

export function Hero({
  bundle,
  locale,
  industry,
}: {
  bundle: BundleData;
  locale: Locale;
  industry: BundleData["industry"];
}) {
  const lead = bundle.featured.lead;
  const favorites = bundle.featured.favorites;
  if (!lead && bundle.items.length === 0) {
    return null;
  }
  if (!lead) return null;
  return (
    <section aria-labelledby="hero-heading" className="sn-hero">
      <div className="sn-card sn-hero-surface sn-hero-card overflow-hidden p-6 md:p-9">
        <div className="flex flex-wrap items-center gap-3">
          <span className="sn-eyebrow">{t(locale, "home.featured")}</span>
          <span className="sn-chip">
            <time dateTime={lead.published_at}>{formatDate(lead.published_at, locale)}</time>
          </span>
          <span className="sn-chip">{lead.publisher}</span>
        </div>
        <h1
          id="hero-heading"
          className="mt-4 text-3xl font-extrabold leading-[1.1] tracking-tight text-[var(--sn-text)] md:text-[2.7rem]"
        >
          <Link
            href={localePath(locale, `/${industry.slug}/article/${lead.id}`)}
            className="transition-colors hover:text-[var(--sn-primary)]"
          >
            {lead.title}
          </Link>
        </h1>
        {lead.summary ?? lead.excerpt ? (
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-[var(--sn-muted)]">
            {lead.summary ?? lead.excerpt}
          </p>
        ) : null}
        <div className="mt-6 flex flex-wrap items-center gap-2">
          {lead.topics.map((topic) => (
            <span key={topic.slug} className="sn-chip">
              {topic.label}
            </span>
          ))}
        </div>
        {favorites.length > 0 ? (
          <ul className="sn-rail mt-7 grid gap-2 border-t border-[var(--sn-border)] pt-5 sm:grid-cols-3">
            {favorites.map((item) => (
              <li key={item.id}>
                <Link
                  href={localePath(locale, `/${industry.slug}/article/${item.id}`)}
                  className="block rounded-[calc(var(--sn-radius)+2px)] p-3 transition-colors hover:bg-[color-mix(in_srgb,var(--sn-primary)_7%,var(--sn-bg))]"
                >
                  <p className="text-sm font-semibold leading-snug text-[var(--sn-text)]">
                    {item.title}
                  </p>
                  <p className="mt-1 text-xs text-[var(--sn-muted)]">{item.publisher}</p>
                </Link>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
      <CtaCard industry={industry} locale={locale} placement="hero" />
    </section>
  );
}

export function StoryColumns({
  bundle,
  locale,
  industry,
}: {
  bundle: BundleData;
  locale: Locale;
  industry: string;
}) {
  const populated = bundle.columns.filter((column) => column.items.length > 0);
  if (populated.length === 0) return null;
  return (
    <section aria-labelledby="latest-heading" className="mt-12">
      <div className="flex items-end justify-between gap-4">
        <h2
          id="latest-heading"
          className="text-2xl font-extrabold tracking-tight text-[var(--sn-text)]"
        >
          {t(locale, "home.latest")}
        </h2>
        <span aria-hidden="true" className="sn-rule" />
      </div>
      <div className="sn-columns mt-5">
        {populated.map((column, index) => (
          <div key={index} className="flex flex-col gap-5">
            {column.items.map((article) => (
              <StoryCard key={article.id} article={article} industry={industry} locale={locale} />
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}
