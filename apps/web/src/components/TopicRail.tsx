import Link from "next/link";

import type { Topic } from "@/lib/api";
import { localePath } from "@/lib/i18n";

export function TopicRail({
  topics,
  industry,
  locale,
  title,
}: {
  topics: Topic[];
  industry: string;
  locale: string;
  title: string;
}) {
  if (topics.length === 0) return null;
  return (
    <section aria-labelledby="topics-heading" className="rounded-[var(--sn-radius)] border border-[var(--sn-border)] p-5">
      <h2 id="topics-heading" className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--sn-muted)]">
        {title}
      </h2>
      <ul className="mt-3 flex flex-wrap gap-2">
        {topics.map((topic) => (
          <li key={topic.slug}>
            <Link
              href={localePath(locale as "en" | "es", `/${industry}/search?topic=${topic.slug}`)}
              className="inline-flex items-center gap-2 rounded-full border border-[var(--sn-border)] px-3 py-1.5 text-sm text-[var(--sn-text)] hover:border-[var(--sn-primary)]"
            >
              {topic.label}
              {typeof topic.count === "number" ? (
                <span className="text-xs text-[var(--sn-muted)]">{topic.count}</span>
              ) : null}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
