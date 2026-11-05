import Link from "next/link";

import type { ArticleCard } from "@/lib/api";
import { formatDate, localePath, t, type Locale } from "@/lib/i18n";

interface StoryCardProps {
  article: ArticleCard;
  industry: string;
  locale: Locale;
  featured?: boolean;
}

export function StoryCard({ article, industry, locale, featured = false }: StoryCardProps) {
  const href = localePath(locale, `/${industry}/article/${article.id}`);
  const body = article.summary ?? article.excerpt;
  return (
    <article
      className={`group flex h-full flex-col gap-3 rounded-[var(--sn-radius)] border border-[var(--sn-border)] bg-[var(--sn-bg)] p-5 ${
        featured ? "md:p-6" : ""
      }`}
    >
      <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--sn-muted)]">
        <span>{article.publisher}</span>
        <span aria-hidden="true">·</span>
        <time dateTime={article.published_at}>
          {formatDate(article.published_at, locale)}
        </time>
        {article.corroboration > 1 ? (
          <span className="rounded-full bg-[var(--sn-surface)] px-2 py-0.5 font-medium">
            {article.corroboration} {t(locale, "article.sources")}
          </span>
        ) : null}
      </div>
      <h3
        className={`font-semibold leading-snug text-[var(--sn-text)] ${
          featured ? "text-2xl md:text-3xl" : "text-lg"
        }`}
      >
        <Link href={href} className="hover:text-[var(--sn-accent)] focus-visible:underline">
          {article.title}
        </Link>
      </h3>
      {body ? <p className="text-sm leading-relaxed text-[var(--sn-muted)]">{body}</p> : null}
      <div className="mt-auto flex flex-wrap items-center gap-2 pt-2">
        {article.topics.slice(0, 3).map((topic) => (
          <span
            key={topic.slug}
            className="rounded-full border border-[var(--sn-border)] px-2.5 py-1 text-xs font-medium text-[var(--sn-muted)]"
          >
            {topic.label}
          </span>
        ))}
        <Link
          href={href}
          className="ml-auto text-sm font-semibold text-[var(--sn-primary)] hover:text-[var(--sn-accent)]"
          aria-label={`${t(locale, "common.readMore")}: ${article.title}`}
        >
          {t(locale, "common.readMore")} →
        </Link>
      </div>
    </article>
  );
}
