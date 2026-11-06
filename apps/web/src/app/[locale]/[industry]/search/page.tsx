import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { LeadForm } from "@/components/LeadForm";
import { EmptyState } from "@/components/Notices";
import { SearchBox } from "@/components/SearchBox";
import { StoryCard } from "@/components/StoryCard";
import { TrustBlock } from "@/components/TrustBlock";
import { BriefSignup } from "@/components/BriefSignup";
import { getIndustry, getNews } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { offersOf } from "@/lib/offers";
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
  const offers = offersOf(channel);
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
            <h2 className="sr-only">{t(resolved, "search.listTitle")}</h2>
            {articles.map((article) => (
              <StoryCard key={article.id} article={article} industry={industry} locale={resolved} />
            ))}
          </div>
        ) : null}

        {offers.consultation ? (
          <div className="sn-lead-standalone mt-10">
            <LeadForm
              industry={industry}
              industryName={channel.name}
              locale={resolved}
              kind={channel.cta.kind ?? "consultation"}
              placement="search"
              sourcePage={localePath(resolved, `/${industry}/search`)}
              qualify={channel.cta.qualify}
            />
          </div>
        ) : null}
        {offers.brief ? (
          <BriefSignup
            industry={industry}
            locale={resolved}
            placement="brief-search"
            sourcePage={localePath(resolved, `/${industry}/search`)}
          />
        ) : null}
      </div>
      <aside className="sn-search-aside h-fit lg:sticky lg:top-24">
        <TrustBlock locale={resolved} />
      </aside>
    </div>
  );
}
