import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { CtaCard } from "@/components/CtaCard";
import { StickyCta } from "@/components/Cta";
import { JsonLd } from "@/components/JsonLd";
import { LeadForm } from "@/components/LeadForm";
import { EmptyState, FallbackNotice } from "@/components/Notices";
import { StoryCard } from "@/components/StoryCard";
import { getArticle, getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { formatDate, localePath, resolveLocale, t } from "@/lib/i18n";
import { absoluteUrl, newsArticleJsonLd, pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string; id: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry, id } = await params;
  const resolved = resolveLocale(locale);
  const result = await getArticle(industry, id, resolved);
  if (!result.ok) {
    return { title: t(resolved, "article.notFound"), robots: { index: false, follow: false } };
  }
  const article = result.data;
  return pageMetadata({
    title: article.title,
    description: article.summary ?? article.excerpt ?? article.title,
    path: `/${industry}/article/${id}`,
    locale: resolved,
  });
}

export default async function ArticlePage({ params }: Params) {
  const { locale, industry, id } = await params;
  const resolved = resolveLocale(locale);
  const [articleResult, industryResult] = await Promise.all([
    getArticle(industry, id, resolved),
    getIndustry(industry, resolved),
  ]);
  if (!articleResult.ok) {
    if (articleResult.status === 404) notFound();
    return (
      <EmptyState
        locale={resolved}
        title={t(resolved, "states.degraded")}
        body={t(resolved, "states.degradedBody")}
      />
    );
  }
  const article = articleResult.data;
  const channel = industryResult.ok ? industryResult.data : fallbackIndustry(industry);
  const pagePath = localePath(resolved, `/${industry}/article/${id}`);

  return (
    <>
      <JsonLd json={newsArticleJsonLd(channel, article, absoluteUrl(pagePath))} />
      {articleResult.meta.fallback && resolved === "es" ? (
        <div className="mb-6">
          <FallbackNotice locale={resolved} href={`/${industry}/article/${id}`} />
        </div>
      ) : null}
      <article className="mx-auto max-w-3xl">
        <Link
          href={localePath(resolved, `/${industry}`)}
          className="text-sm font-semibold text-[var(--sn-muted)] hover:text-[var(--sn-accent)]"
        >
          ← {t(resolved, "article.backToChannel", { industry: channel.name })}
        </Link>
        <header className="mt-4">
          <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--sn-muted)]">
            <span>{article.publisher}</span>
            <span aria-hidden="true">·</span>
            <time dateTime={article.published_at}>
              {t(resolved, "article.published")} {formatDate(article.published_at, resolved)}
            </time>
            {article.corroboration > 1 ? <span>· {article.corroboration} sources</span> : null}
          </div>
          <h1 className="mt-3 text-3xl font-extrabold leading-tight tracking-tight text-[var(--sn-text)] md:text-4xl">
            {article.title}
          </h1>
          <div className="mt-3 flex flex-wrap gap-2">
            {article.topics.map((topic) => (
              <span
                key={topic.slug}
                className="sn-chip"
              >
                {topic.label}
              </span>
            ))}
          </div>
        </header>

        <div className="sn-card sn-card-surface mt-6 p-6">
          <p className="sn-eyebrow">
            {article.summary ? t(resolved, "article.aiSummary") : t(resolved, "article.excerptLabel")}
          </p>
          <p className="mt-2 text-base leading-relaxed text-[var(--sn-text)]">
            {article.summary ?? article.excerpt ?? t(resolved, "article.summaryUnavailable")}
          </p>
          {!article.summary ? (
            <p className="mt-2 text-xs text-[var(--sn-muted)]">
              {t(resolved, "article.summaryUnavailable")}
            </p>
          ) : null}
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="sn-btn"
          >
            {t(resolved, "article.readAtPublisher")} ↗
          </a>
          <p className="max-w-md text-xs text-[var(--sn-muted)]">{t(resolved, "article.attribution")}</p>
        </div>

        <div className="mt-8">
          <CtaCard
            industry={channel}
            locale={resolved}
            placement="article"
            articleId={article.id}
            compact
          />
        </div>

        {article.related.length > 0 ? (
          <section aria-labelledby="related-heading" className="mt-10">
            <h2 id="related-heading" className="text-xl font-semibold text-[var(--sn-text)]">
              {t(resolved, "article.related")}
            </h2>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              {article.related.map((related) => (
                <StoryCard key={related.id} article={related} industry={industry} locale={resolved} />
              ))}
            </div>
          </section>
        ) : null}

        <div className="mt-10">
          <LeadForm
            industry={industry}
            industryName={channel.name}
            locale={resolved}
            kind="consultation"
            placement="article-end"
            articleId={article.id}
            sourcePage={pagePath}
          />
        </div>
      </article>
      <StickyCta industry={industry} locale={resolved} articleId={article.id} />
    </>
  );
}
