import Link from "next/link";

import type { Industry } from "@/lib/api";
import { SkinEmblem } from "./SkinEmblem";
import { localePath, t, type Locale } from "@/lib/i18n";
import { channelBase } from "@/lib/url";
import { resolveSkin } from "@/lib/skins";

export async function Footer({ industry, locale }: { industry: Industry; locale: Locale }) {
  const base = await channelBase(industry.slug);
  const skin = resolveSkin(industry.slug, industry.theme.layout);
  return (
    <footer className="sn-footer mt-16">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-3">
        <div>
          <p className="sn-eyebrow flex items-center gap-2">
            <SkinEmblem skin={skin} className="h-4 w-4" />
            {t(locale, "brand.name")}
          </p>
          <p className="mt-2 max-w-sm text-sm text-[var(--sn-muted)]">
            {t(locale, "footer.copyright")}
          </p>
        </div>
        <div>
          <p className="text-sm font-semibold text-[var(--sn-text)]">
            {t(locale, "footer.disclaimer")}
          </p>
          <p className="mt-2 max-w-md text-sm text-[var(--sn-muted)]">{industry.disclaimer}</p>
        </div>
        <nav aria-label={t(locale, "nav.footer")} className="grid grid-cols-2 gap-2 text-sm">
          <Link href={localePath(locale, `${base}/about`)} className="sn-link-quiet">
            {t(locale, "nav.about")}
          </Link>
          <Link href={localePath(locale, `${base}/contact`)} className="sn-link-quiet">
            {t(locale, "nav.contact")}
          </Link>
          <Link href={localePath(locale, `${base}/privacy`)} className="sn-link-quiet">
            {t(locale, "footer.privacy")}
          </Link>
          <Link href={localePath(locale, `${base}/terms`)} className="sn-link-quiet">
            {t(locale, "footer.terms")}
          </Link>
          <Link href="/sitemap.xml" className="sn-link-quiet">
            {t(locale, "footer.sitemap")}
          </Link>
          <Link href={localePath(locale, `${base}/search`)} className="sn-link-quiet">
            {t(locale, "nav.search")}
          </Link>
          <a
            href={localePath(locale, `${base}/feed.xml`)}
            type="application/rss+xml"
            className="sn-link-quiet"
          >
            {t(locale, "footer.rss")}
          </a>
        </nav>
      </div>
    </footer>
  );
}
