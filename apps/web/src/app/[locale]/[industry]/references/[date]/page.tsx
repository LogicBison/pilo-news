import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { EmptyState } from "@/components/Notices";
import { ReferenceTable } from "@/components/ReferenceTable";
import { getIndustry, getReference } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { formatDay, localePath, resolveLocale, t } from "@/lib/i18n";
import { pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string; date: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry, date } = await params;
  const resolved = resolveLocale(locale);
  const result = await getReference(industry, date, resolved);
  if (!result.ok) {
    return { title: t(resolved, "reference.notFound"), robots: { index: false, follow: false } };
  }
  const issue = result.data;
  const metadata = pageMetadata({
    title: `${issue.title} · ${issue.issue_date}`,
    description: issue.standfirst,
    path: `/${industry}/references/${issue.issue_date}`,
    locale: resolved,
  });
  return resolved === "es" ? { ...metadata, robots: { index: false, follow: true } } : metadata;
}

export default async function ReferencePage({ params }: Params) {
  const { locale, industry, date } = await params;
  const resolved = resolveLocale(locale);
  const [result, industryResult] = await Promise.all([
    getReference(industry, date, resolved),
    getIndustry(industry, resolved),
  ]);
  if (!result.ok) {
    if (result.status === 404) notFound();
    return (
      <EmptyState
        locale={resolved}
        title={t(resolved, "states.degraded")}
        body={t(resolved, "states.degradedBody")}
      />
    );
  }
  const issue = result.data;
  const channel = industryResult.ok ? industryResult.data : fallbackIndustry(industry);
  const archiveHref = localePath(resolved, `/${industry}/references`);

  return (
    <article className="mx-auto max-w-4xl">
      <Link
        href={localePath(resolved, `/${industry}`)}
        className="text-sm font-semibold text-[var(--sn-muted)] hover:text-[var(--sn-accent)]"
      >
        ← {t(resolved, "reference.backToChannel", { industry: channel.name })}
      </Link>
      <header className="mt-4">
        <p className="sn-eyebrow">{t(resolved, "reference.eyebrow")}</p>
        <h1 className="mt-2 text-3xl font-extrabold leading-tight tracking-tight text-[var(--sn-text)] md:text-4xl">
          {issue.title}
        </h1>
        <p className="mt-3 max-w-[65ch] text-base leading-relaxed text-[var(--sn-muted)]">
          {issue.standfirst}
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-[var(--sn-muted)]">
          <span className="sn-chip">
            {t(resolved, "reference.issueDate")}: {formatDay(`${issue.issue_date}T12:00:00Z`, resolved)}
          </span>
          <span className="sn-chip">
            {t(resolved, "reference.scope")}: {issue.scope}
          </span>
          {issue.reviewer ? (
            <span className="sn-chip">
              {t(resolved, "reference.reviewer")}: {issue.reviewer}
            </span>
          ) : null}
          <span className="sn-chip">
            {t(resolved, "reference.rows", { n: issue.items.length })}
          </span>
        </div>
        {resolved === "es" ? (
          <p className="mt-4 border-l-2 border-[var(--sn-accent)] pl-3 text-sm text-[var(--sn-muted)]">
            {t(resolved, "reference.englishOnly")}
          </p>
        ) : null}
      </header>

      <ReferenceTable issue={issue} locale={resolved} />

      {issue.sources.length > 0 ? (
        <section aria-labelledby="reference-sources-heading" className="mt-8">
          <h2 id="reference-sources-heading" className="text-sm font-semibold text-[var(--sn-text)]">
            {t(resolved, "reference.sources")}
          </h2>
          <ul className="mt-2 flex flex-wrap gap-x-5 gap-y-2 text-sm text-[var(--sn-muted)]">
            {issue.sources.map((source) => (
              <li key={source.url}>
                <a href={source.url} target="_blank" rel="noopener noreferrer" className="underline">
                  {source.name}
                </a>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <footer className="mt-8 border-t border-[var(--sn-border)] pt-4 text-xs text-[var(--sn-muted)]">
        <p>
          {t(resolved, "reference.sourceVersion")}: {issue.source_version ?? "-"}
        </p>
        <p className="mt-1">
          <Link href={archiveHref} className="font-semibold underline">
            {t(resolved, "reference.allIssues")}
          </Link>
        </p>
      </footer>
    </article>
  );
}
