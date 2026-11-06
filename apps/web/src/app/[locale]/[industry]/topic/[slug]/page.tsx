import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { BriefSignup } from "@/components/BriefSignup";
import { CtaCard } from "@/components/CtaCard";
import { EmptyState } from "@/components/Notices";
import { StoryCard } from "@/components/StoryCard";
import { getIndustry, getNews, getTopics } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { offersOf } from "@/lib/offers";
import { pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string; slug: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry, slug } = await params;
  const resolved = resolveLocale(locale);
  const [channelResult, topicResult] = await Promise.all([
    getIndustry(industry, resolved),
    getTopics(industry, resolved),
  ]);
  const name = channelResult.ok ? channelResult.data.name : industry;
  const label = topicResult.ok
    ? (topicResult.data.find((topic) => topic.slug === slug)?.label ?? slug)
    : slug;
  return pageMetadata({
    title: t(resolved, "topic.title", { topic: label, industry: name }),
    description: t(resolved, "topic.intro"),
    path: `/${industry}/topic/${slug}`,
    locale: resolved,
  });
}

export default async function TopicPage({ params }: Params) {
  const { locale, industry, slug } = await params;
  const resolved = resolveLocale(locale);
  const [channelResult, topicResult, newsResult] = await Promise.all([
    getIndustry(industry, resolved),
    getTopics(industry, resolved),
    getNews(industry, resolved, { topic: slug, limit: 50 }),
  ]);
  if (!channelResult.ok && channelResult.status === 404) notFound();
  const channel = channelResult.ok ? channelResult.data : fallbackIndustry(industry);
  const offers = offersOf(channel);
  const topic = topicResult.ok ? topicResult.data.find((item) => item.slug === slug) : undefined;
  if (topicResult.ok && !topic) notFound();
  const articles = newsResult.ok ? newsResult.data : [];
  const label = topic?.label ?? slug;
  const sourcePage = localePath(resolved, `/${industry}/topic/${slug}`);

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <div>
        <p className="sn-eyebrow">{t(resolved, "home.topics")}</p>
        <h1 className="mt-1 text-3xl font-semibold text-[var(--sn-text)]">
          {t(resolved, "topic.title", { topic: label, industry: channel.name })}
        </h1>
        <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(resolved, "topic.intro")}</p>

        {articles.length === 0 ? (
          <div className="mt-6">
            <EmptyState
              locale={resolved}
              title={t(resolved, "topic.empty")}
              body={t(resolved, "topic.emptyBody")}
            />
          </div>
        ) : (
          <div className="mt-6 grid gap-5 md:grid-cols-2">
            <h2 className="sr-only">{t(resolved, "topic.listTitle")}</h2>
            {articles.map((article) => (
              <StoryCard key={article.id} article={article} industry={industry} locale={resolved} />
            ))}
          </div>
        )}
      </div>
      <div>
        {offers.consultation ? (
          <CtaCard industry={channel} locale={resolved} placement="topic" compact />
        ) : null}
        {offers.brief ? (
          <div className="mt-6">
            <BriefSignup
              industry={industry}
              locale={resolved}
              placement="brief-topic"
              sourcePage={sourcePage}
            />
          </div>
        ) : null}
      </div>
    </div>
  );
}
