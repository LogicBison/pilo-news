import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { resolveLocale, t } from "@/lib/i18n";
import { pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  return pageMetadata({
    title: t(resolved, "legal.termsTitle"),
    description: t(resolved, "legal.termsTitle"),
    path: `/${industry}/terms`,
    locale: resolved,
  });
}

export default async function TermsPage({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  if (!result.ok && result.status === 404) notFound();
  const channel = result.ok ? result.data : fallbackIndustry(industry);
  return (
    <article className="mx-auto max-w-3xl">
      <h1 className="text-3xl font-semibold text-[var(--sn-text)]">{t(resolved, "legal.termsTitle")}</h1>
      <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(resolved, "legal.lastUpdated")}</p>
      <p className="mt-5 text-base leading-relaxed text-[var(--sn-muted)]">{t(resolved, "legal.termsBody")}</p>
      <p className="mt-5 text-sm text-[var(--sn-muted)]">{channel.disclaimer}</p>
    </article>
  );
}
