import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { CtaCard } from "@/components/CtaCard";
import { LeadForm } from "@/components/LeadForm";
import { getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  const name = result.ok ? result.data.name : industry;
  return pageMetadata({
    title: t(resolved, "about.title", { industry: name }),
    description: t(resolved, "about.description", { industry: name }),
    path: `/${industry}/about`,
    locale: resolved,
  });
}

export default async function AboutPage({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  if (!result.ok && result.status === 404) notFound();
  const channel = result.ok ? result.data : fallbackIndustry(industry);
  const name = channel.name;

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <article className="space-y-5">
        <h1 className="text-3xl font-semibold text-[var(--sn-text)]">
          {t(resolved, "about.title", { industry: name })}
        </h1>
        <p className="text-base leading-relaxed text-[var(--sn-muted)]">
          {t(resolved, "about.body1", { industry: name })}
        </p>
        <p className="text-base leading-relaxed text-[var(--sn-muted)]">
          {t(resolved, "about.body2", { industry: name })}
        </p>
        <section aria-labelledby="how-heading" className="rounded-[var(--sn-radius)] border border-[var(--sn-border)] p-5">
          <h2 id="how-heading" className="text-xl font-semibold text-[var(--sn-text)]">
            {t(resolved, "about.howTitle")}
          </h2>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-[var(--sn-muted)]">
            <li>{t(resolved, "about.how1")}</li>
            <li>{t(resolved, "about.how2")}</li>
            <li>{t(resolved, "about.how3")}</li>
          </ul>
        </section>
        <p className="text-sm text-[var(--sn-muted)]">
          <a href={localePath(resolved, `/${industry}/contact`)} className="font-semibold underline">
            {t(resolved, "about.contact")}
          </a>
        </p>
        <div className="pt-4">
          <LeadForm
            industry={industry}
            industryName={name}
            locale={resolved}
            kind={channel.cta.kind ?? "consultation"}
            placement="about"
            sourcePage={localePath(resolved, `/${industry}/about`)}
          />
        </div>
      </article>
      <CtaCard industry={channel} locale={resolved} placement="about" />
    </div>
  );
}
