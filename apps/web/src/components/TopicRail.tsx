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
    <section aria-labelledby="topics-heading" className="sn-editorial-block">
      <h2 id="topics-heading" className="sn-eyebrow">
        {title}
      </h2>
      <ul className="mt-3 flex flex-wrap gap-2">
        {topics.map((topic) => (
          <li key={topic.slug}>
            <Link
              href={localePath(locale as "en" | "es", `/${industry}/search?topic=${topic.slug}`)}
              className="sn-chip sn-chip-link px-3 py-1.5"
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
