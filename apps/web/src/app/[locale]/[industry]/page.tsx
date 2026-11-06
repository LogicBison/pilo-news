import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { DeskBrief } from "@/components/DeskBrief";
import { AssetOffer } from "@/components/AssetOffer";
import { BriefSignup } from "@/components/BriefSignup";
import { Hero, StoryColumns } from "@/components/Hero";
import { JsonLd } from "@/components/JsonLd";
import { LeadForm } from "@/components/LeadForm";
import { EmptyState, FallbackNotice } from "@/components/Notices";
import { ProofStrip } from "@/components/ProofStrip";
import { SkinScene } from "@/components/SkinScene";
import { TrustBlock } from "@/components/TrustBlock";
import { StickyCta } from "@/components/Cta";
import { TopicRail } from "@/components/TopicRail";
import { getBundle, getIndustry } from "@/lib/api";
import { assetFor } from "@/lib/assets";
import { localePath, resolveLocale, t } from "@/lib/i18n";
import { offersOf } from "@/lib/offers";
import { resolveSkin } from "@/lib/skins";
import { itemListJsonLd, pageMetadata } from "@/lib/seo";

type Params = { params: Promise<{ locale: string; industry: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getIndustry(industry, resolved);
  const name = result.ok ? result.data.name : industry;
  return pageMetadata({
    title: t(resolved, "home.title", { industry: name }),
    description: result.ok
      ? result.data.tagline
      : t(resolved, "meta.defaultDescription"),
    path: `/${industry}`,
    locale: resolved,
  });
}

export default async function ChannelHome({ params }: Params) {
  const { locale, industry } = await params;
  const resolved = resolveLocale(locale);
  const result = await getBundle(industry, resolved);
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
  const bundle = result.data;
  const channel = bundle.industry;
  const homePath = localePath(resolved, `/${industry}`);
  const offers = offersOf(channel);
  const asset = offers.asset && channel.cta.asset ? assetFor(channel.cta.asset) : undefined;

  return (
    <>
      <JsonLd json={itemListJsonLd(channel, bundle.items)} />
      {bundle.fallback && resolved === "es" ? (
        <div className="mb-6">
          <FallbackNotice locale={resolved} href={`/${industry}`} />
        </div>
      ) : null}
      {bundle.items.length === 0 ? (
        <EmptyState locale={resolved} />
      ) : (
        <>
          <Hero bundle={bundle} locale={resolved} industry={channel} />
          <ProofStrip bundle={bundle} locale={resolved} />
          <SkinScene skin={resolveSkin(channel.slug, channel.theme.layout)} channel={channel} locale={resolved} />
          <div className="mt-8 grid gap-5 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
            <DeskBrief brief={bundle.ai_summary} locale={resolved} />
            <TopicRail
              topics={bundle.topics}
              industry={industry}
              locale={resolved}
              title={t(resolved, "home.topics")}
            />
          </div>
          <StoryColumns bundle={bundle} locale={resolved} industry={industry} />
          {bundle.sources.length > 0 ? (
            <section aria-labelledby="sources-heading" className="sn-editorial-block mt-10">
              <h2 id="sources-heading" className="sn-eyebrow">
                {t(resolved, "home.sources")}
              </h2>
              <ul className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm text-[var(--sn-muted)]">
                {bundle.sources.map((source) => (
                  <li key={source.name}>
                    <a href={source.url} rel="noopener noreferrer" target="_blank" className="hover:underline">
                      {source.name}
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </>
      )}
      {asset ? (
        <AssetOffer
          industry={industry}
          locale={resolved}
          asset={asset.slug}
          title={t(resolved, asset.titleKey)}
          body={t(resolved, asset.bodyKey)}
          sourcePage={localePath(resolved, `/${industry}`)}
        />
      ) : null}
      {offers.consultation ? (
        <section className="sn-convert" aria-labelledby="convert-heading">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="sn-kicker" aria-hidden="true" />
              <p className="sn-eyebrow">{t(resolved, "convert.eyebrow")}</p>
            </div>
            <h2 id="convert-heading" className="sn-section-title mt-2 text-[var(--sn-text)]">
              {t(resolved, "convert.title")}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-[var(--sn-muted)]">
              {t(resolved, "convert.body")}
            </p>
          </div>
          <div className="sn-convert-grid">
            <TrustBlock locale={resolved} />
            <LeadForm
              industry={industry}
              industryName={channel.name}
              locale={resolved}
              kind={channel.cta.kind ?? "consultation"}
              placement="home"
              sourcePage={homePath}
              qualify={channel.cta.qualify}
            />
          </div>
        </section>
      ) : null}
      {offers.brief ? (
        <BriefSignup
          industry={industry}
          locale={resolved}
          placement="brief-home"
          sourcePage={homePath}
        />
      ) : null}
      {offers.consultation ? <StickyCta industry={industry} locale={resolved} /> : null}
      <p className="mt-6 text-center text-xs text-[var(--sn-muted)]">
        <Link href={localePath(resolved, `/${industry}/about`)} className="hover:underline">
          {t(resolved, "nav.about")}
        </Link>
      </p>
    </>
  );
}
