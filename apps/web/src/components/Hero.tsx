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
    <section aria-labelledby="hero-heading" className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <div className="rounded-[var(--sn-radius)] border border-[var(--sn-border)] bg-[var(--sn-surface)] p-6 md:p-8">
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium uppercase tracking-[0.14em] text-[var(--sn-muted)]">
          <span>{t(locale, "home.featured")}</span>
          <span aria-hidden="true">·</span>
          <time dateTime={lead.published_at}>{formatDate(lead.published_at, locale)}</time>
        </div>
        <h1 id="hero-heading" className="mt-3 text-3xl font-semibold leading-tight text-[var(--sn-text)] md:text-4xl">
          <Link href={localePath(locale, `/${industry.slug}/article/${lead.id}`)} className="hover:text-[var(--sn-accent)]">
            {lead.title}
          </Link>
        </h1>
        {lead.summary ?? lead.excerpt ? (
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-[var(--sn-muted)]">
            {lead.summary ?? lead.excerpt}
          </p>
        ) : null}
        <div className="mt-5 flex flex-wrap items-center gap-2">
          {lead.topics.map((topic) => (
            <span key={topic.slug} className="rounded-full border border-[var(--sn-border)] px-2.5 py-1 text-xs text-[var(--sn-muted)]">
              {topic.label}
            </span>
          ))}
          <span className="text-xs text-[var(--sn-muted)]">{lead.publisher}</span>
        </div>
        {favorites.length > 0 ? (
          <ul className="mt-6 grid gap-3 border-t border-[var(--sn-border)] pt-5 sm:grid-cols-3">
            {favorites.map((item) => (
              <li key={item.id}>
                <Link href={localePath(locale, `/${industry.slug}/article/${item.id}`)} className="text-sm font-medium hover:text-[var(--sn-accent)]">
                  {item.title}
                </Link>
                <p className="mt-1 text-xs text-[var(--sn-muted)]">{item.publisher}</p>
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
    <section aria-labelledby="latest-heading" className="mt-10">
      <h2 id="latest-heading" className="text-2xl font-semibold text-[var(--sn-text)]">
        {t(locale, "home.latest")}
      </h2>
      <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
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
