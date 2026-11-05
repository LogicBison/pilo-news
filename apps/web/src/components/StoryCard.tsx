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
      className={`sn-card sn-card-interactive group flex h-full flex-col gap-3 p-5 ${
        featured ? "md:p-6" : ""
      }`}
    >
      <div className="flex flex-wrap items-center gap-2 text-xs font-medium text-[var(--sn-muted)]">
        <span className="sn-chip">{article.publisher}</span>
        <time dateTime={article.published_at}>
          {formatDate(article.published_at, locale)}
        </time>
        {article.corroboration > 1 ? (
          <span className="sn-chip">
            {article.corroboration} {t(locale, "article.sources")}
          </span>
        ) : null}
      </div>
      <h3
        className={`font-bold leading-snug tracking-tight text-[var(--sn-text)] ${
          featured ? "text-2xl md:text-3xl" : "text-lg"
        }`}
      >
        <Link
          href={href}
          className="transition-colors group-hover:text-[var(--sn-primary)] focus-visible:underline"
        >
          {article.title}
        </Link>
      </h3>
      {body ? <p className="text-sm leading-relaxed text-[var(--sn-muted)]">{body}</p> : null}
      <div className="mt-auto flex flex-wrap items-center gap-2 pt-2">
        {article.topics.slice(0, 3).map((topic) => (
          <span key={topic.slug} className="sn-chip">
            {topic.label}
          </span>
        ))}
        <Link
          href={href}
          className="ml-auto text-sm font-bold text-[var(--sn-primary)] transition-colors hover:text-[var(--sn-accent)]"
          aria-label={`${t(locale, "common.readMore")}: ${article.title}`}
        >
          {t(locale, "common.readMore")} →
        </Link>
      </div>
    </article>
  );
}
