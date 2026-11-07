import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { BriefSignup } from "@/components/BriefSignup";
import { LeadForm } from "@/components/LeadForm";
import { TrustBlock } from "@/components/TrustBlock";
import { getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { channelBase } from "@/lib/url";
import { offersOf } from "@/lib/offers";
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
    industry,
  });
}

export default async function AboutPage({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const base = await channelBase(industry);
  const result = await getIndustry(industry, resolved);
  if (!result.ok && result.status === 404) notFound();
  const channel = result.ok ? result.data : fallbackIndustry(industry);
  const name = channel.name;
  const offers = offersOf(channel);

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
      <article className="space-y-5">
        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--sn-text)]">
          {t(resolved, "about.title", { industry: name })}
        </h1>
        <p className="max-w-[65ch] text-base leading-relaxed text-[var(--sn-muted)]">
          {t(resolved, "about.body1", { industry: name })}
        </p>
        <p className="max-w-[65ch] text-base leading-relaxed text-[var(--sn-muted)]">
          {t(resolved, "about.body2", { industry: name })}
        </p>
        <section aria-labelledby="how-heading" className="sn-editorial-block">
          <h2 id="how-heading" className="text-xl font-semibold text-[var(--sn-text)]">
            {t(resolved, "about.howTitle")}
          </h2>
          <ul className="mt-3 max-w-[65ch] list-disc space-y-2 pl-5 text-sm text-[var(--sn-muted)]">
            <li>{t(resolved, "about.how1")}</li>
            <li>{t(resolved, "about.how2")}</li>
            <li>{t(resolved, "about.how3")}</li>
          </ul>
        </section>
        <p className="text-sm text-[var(--sn-muted)]">
          <a href={localePath(resolved, `${base}/contact`)} className="font-semibold underline">
            {t(resolved, "about.contact")}
          </a>
        </p>
        {offers.consultation ? (
          <div className="sn-lead-standalone pt-4">
            <LeadForm
              base={base}
              industry={industry}
              industryName={name}
              locale={resolved}
              kind={channel.cta.kind ?? "consultation"}
              placement="about"
              sourcePage={localePath(resolved, `${base}/about`)}
              qualify={channel.cta.qualify}
            />
          </div>
        ) : null}
        {offers.brief ? (
          <BriefSignup
            industry={industry}
            locale={resolved}
            placement="brief-about"
            sourcePage={localePath(resolved, `${base}/about`)}
          />
        ) : null}
      </article>
      <aside className="sn-search-aside h-fit lg:sticky lg:top-24">
        <TrustBlock locale={resolved} />
      </aside>
    </div>
  );
}
