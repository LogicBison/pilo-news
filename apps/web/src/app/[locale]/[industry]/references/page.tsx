import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { EmptyState } from "@/components/Notices";
import { getIndustry, getReferences } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { formatDay, localePath, resolveLocale, t } from "@/lib/i18n";
import { channelBase } from "@/lib/url";
import { pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  const name = result.ok ? result.data.name : industry;
  return pageMetadata({
    title: `${t(resolved, "reference.title")} · ${name}`,
    description: t(resolved, "reference.intro", { industry: name }),
    path: `/${industry}/references`,
    locale: resolved,
    industry,
  });
}

export default async function ReferencesPage({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const base = await channelBase(industry);
  const [industryResult, references] = await Promise.all([
    getIndustry(industry, resolved),
    getReferences(industry, resolved),
  ]);
  if (!industryResult.ok && industryResult.status === 404) notFound();
  const channel = industryResult.ok ? industryResult.data : fallbackIndustry(industry);

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        href={localePath(resolved, `${base}`)}
        className="text-sm font-semibold text-[var(--sn-muted)] hover:text-[var(--sn-accent)]"
      >
        ← {t(resolved, "reference.backToChannel", { industry: channel.name })}
      </Link>
      <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-[var(--sn-text)]">
        {t(resolved, "reference.title")}
      </h1>
      <p className="mt-2 max-w-[65ch] text-sm leading-relaxed text-[var(--sn-muted)]">
        {t(resolved, "reference.intro", { industry: channel.name })}
      </p>

      {!references.ok ? (
        <div className="mt-6">
          <EmptyState
            locale={resolved}
            title={t(resolved, "states.degraded")}
            body={t(resolved, "states.degradedBody")}
          />
        </div>
      ) : references.data.length === 0 ? (
        <div className="mt-6">
          <EmptyState
            locale={resolved}
            title={t(resolved, "reference.empty")}
            body={t(resolved, "reference.emptyBody")}
          />
        </div>
      ) : (
        <ul className="mt-6 border-t border-[var(--sn-border)]">
          {references.data.map((issue) => (
            <li key={issue.issue_date} className="border-b border-[var(--sn-border)] py-4">
              <Link
                href={localePath(resolved, `${base}/references/${issue.issue_date}`)}
                className="group flex flex-wrap items-baseline gap-3"
              >
                <span className="text-sm font-semibold tabular-nums text-[var(--sn-text)]">
                  {formatDay(`${issue.issue_date}T12:00:00Z`, resolved)}
                </span>
                <span className="font-semibold text-[var(--sn-text)] group-hover:text-[var(--sn-accent)]">
                  {issue.title}
                </span>
                <span className="sn-chip">{issue.scope}</span>
                <span className="ml-auto text-xs text-[var(--sn-muted)]">
                  {t(resolved, "reference.rows", { n: issue.row_count })}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
