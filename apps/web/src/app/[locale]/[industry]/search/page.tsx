import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { CtaCard } from "@/components/CtaCard";
import { LeadForm } from "@/components/LeadForm";
import { EmptyState } from "@/components/Notices";
import { SearchBox } from "@/components/SearchBox";
import { StoryCard } from "@/components/StoryCard";
import { getIndustry, getNews } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { pageMetadata } from "@/lib/seo";

type Params = {
  params: Promise<{ locale: string; industry: string }>;
  searchParams: Promise<{ q?: string; topic?: string }>;
};

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  const name = result.ok ? result.data.name : industry;
  return pageMetadata({
    title: t(resolved, "search.title", { industry: name }),
    description: t(resolved, "search.description", { industry: name }),
    path: `/${industry}/search`,
    locale: resolved,
  });
}

export default async function SearchPage({ params, searchParams }: Params) {
  const { locale, industry } = await params;
  const { q, topic } = await searchParams;
  const resolved = resolveLocale(locale);
  const industryResult = await getIndustry(industry, resolved);
  if (!industryResult.ok && industryResult.status === 404) notFound();
  const channel = industryResult.ok ? industryResult.data : fallbackIndustry(industry);
  const query = (q ?? "").trim();
  const validQuery = query.length >= 3 && query.length <= 64;
  const result =
    validQuery || topic
      ? await getNews(industry, resolved, { q: validQuery ? query : undefined, topic })
      : null;
  const articles = result?.ok ? result.data : [];

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <div>
        <h1 className="text-3xl font-semibold text-[var(--sn-text)]">
          {t(resolved, "search.title", { industry: channel.name })}
        </h1>
        <p className="mt-2 text-sm text-[var(--sn-muted)]">
          {t(resolved, "search.description", { industry: channel.name })}
        </p>
        <div className="mt-5">
          <SearchBox industry={industry} locale={resolved} initialQuery={query} />
        </div>

        {result && !result.ok ? (
          <div className="mt-6">
            <EmptyState locale={resolved} title={t(resolved, "states.degraded")} body={t(resolved, "states.degradedBody")} />
          </div>
        ) : null}

        {result?.ok && validQuery ? (
          <p className="mt-6 text-sm font-medium text-[var(--sn-muted)]" aria-live="polite">
            {t(resolved, "search.results", { count: articles.length, query })}
          </p>
        ) : null}

        {result?.ok && articles.length === 0 ? (
          <div className="mt-6">
            <EmptyState
              locale={resolved}
              title={t(resolved, "search.empty")}
              body={t(resolved, "search.emptyBody")}
            />
          </div>
        ) : null}

        {articles.length > 0 ? (
          <div className="mt-5 grid gap-5 md:grid-cols-2">
            {articles.map((article) => (
              <StoryCard key={article.id} article={article} industry={industry} locale={resolved} />
            ))}
          </div>
        ) : null}

        <div className="mt-10">
          <LeadForm
            industry={industry}
            industryName={channel.name}
            locale={resolved}
            kind={channel.cta.kind ?? "consultation"}
            placement="search"
            sourcePage={localePath(resolved, `/${industry}/search`)}
          />
        </div>
      </div>
      <CtaCard industry={channel} locale={resolved} placement="search" compact />
    </div>
  );
}
