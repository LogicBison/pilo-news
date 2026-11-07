import { notFound } from "next/navigation";
import type { CSSProperties, ReactNode } from "react";

import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { DegradedNotice } from "@/components/Notices";
import { getIndustry } from "@/lib/api";
import { fallbackIndustry } from "@/lib/fallback";
import { isLocale, localePath, t } from "@/lib/i18n";
import { channelBase } from "@/lib/url";
import { resolveSkin } from "@/lib/skins";
import { themeStyle } from "@/lib/theme";

export default async function IndustryLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string; industry: string }>;
}) {
  const { locale, industry } = await params;
  if (!isLocale(locale)) notFound();
  const result = await getIndustry(industry, locale);
  if (!result.ok && result.status === 404) notFound();
  const base = await channelBase(industry);
  const home = localePath(locale, base || "/");
  const feedHref = home === "/" ? "/feed.xml" : `${home}/feed.xml`;
  const channel = result.ok ? result.data : fallbackIndustry(industry);
  const degraded = !result.ok;
  const skin = resolveSkin(channel.slug, channel.theme.layout);

  return (
    <div
      lang={locale}
      data-layout={channel.theme.layout}
      data-skin={skin.key}
      data-hero={skin.hero}
      data-list={skin.list}
      data-bar={skin.bar}
      style={{
        ...themeStyle(channel.theme),
        "--sn-radius": skin.radius,
        fontFamily: "var(--sn-font-body)",
      } as CSSProperties}
      className="min-h-screen bg-[var(--sn-bg)] text-[var(--sn-text)]"
    >
      <link
        rel="alternate"
        type="application/rss+xml"
        title={`${channel.name} — System News`}
        href={feedHref}
      />
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded focus:bg-[var(--sn-primary)] focus:px-4 focus:py-2 focus:text-white"
      >
        {t(locale, "common.skipToContent")}
      </a>
      <Header industry={channel} locale={locale} />
      <main id="main" className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        {degraded ? (
          <div className="mb-6">
            <DegradedNotice locale={locale} retryHref={home} />
          </div>
        ) : null}
        {children}
      </main>
      <Footer industry={channel} locale={locale} />
    </div>
  );
}
