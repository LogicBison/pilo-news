import type { Topic } from "@/lib/api";
import { localePath } from "@/lib/i18n";
import { channelBase } from "@/lib/url";

import { ChipLink } from "./ui/chip";

export async function TopicRail({
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
  const base = await channelBase(industry);
  return (
    <section aria-labelledby="topics-heading" className="sn-editorial-block">
      <h2 id="topics-heading" className="sn-eyebrow">
        {title}
      </h2>
      <ul className="mt-3 flex flex-wrap gap-2">
        {topics.map((topic) => (
          <li key={topic.slug}>
            <ChipLink
              href={localePath(locale as "en" | "es", `${base}/search?topic=${topic.slug}`)}
              className="px-3 py-1.5"
            >
              {topic.label}
              {typeof topic.count === "number" ? (
                <span className="text-xs text-[var(--sn-muted)]">{topic.count}</span>
              ) : null}
            </ChipLink>
          </li>
        ))}
      </ul>
    </section>
  );
}
