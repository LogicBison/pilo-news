import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { BriefSignup } from "@/components/BriefSignup";
import { EmptyState } from "@/components/Notices";
import { getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { offersOf } from "@/lib/offers";
import { pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  const name = result.ok ? result.data.name : industry;
  return pageMetadata({
    title: `${t(resolved, "briefs.title")} · ${name}`,
    description: t(resolved, "briefs.intro"),
    path: `/${industry}/briefs`,
    locale: resolved,
  });
}

export default async function BriefsPage({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  if (!result.ok && result.status === 404) notFound();
  const channel = result.ok ? result.data : fallbackIndustry(industry);
  const sourcePage = localePath(resolved, `/${industry}/briefs`);
  const offers = offersOf(channel);

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <div>
        <h1 className="text-3xl font-semibold text-[var(--sn-text)]">{t(resolved, "briefs.title")}</h1>
        <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(resolved, "briefs.intro")}</p>
        <p className="mt-1 text-sm font-medium text-[var(--sn-text)]">{t(resolved, "briefs.cadence")}</p>

        <div className="mt-6">
          <EmptyState
            locale={resolved}
            title={t(resolved, "briefs.empty")}
            body={t(resolved, "briefs.emptyBody")}
          />
        </div>
      </div>
      <div>
        {offers.brief ? (
          <BriefSignup
            industry={industry}
            locale={resolved}
            placement="brief-archive"
            sourcePage={sourcePage}
          />
        ) : null}
        <p className="mt-4 text-xs text-[var(--sn-muted)]">{channel.name}</p>
      </div>
    </div>
  );
}
