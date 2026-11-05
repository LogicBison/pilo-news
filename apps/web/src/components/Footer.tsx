import Link from "next/link";

import type { Industry } from "@/lib/api";
import { localePath, t, type Locale } from "@/lib/i18n";

export function Footer({ industry, locale }: { industry: Industry; locale: Locale }) {
  return (
    <footer className="mt-16 border-t border-[var(--sn-border)] bg-[var(--sn-surface)]">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--sn-muted)]">
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
        <nav aria-label={t(locale, "nav.menu")} className="grid grid-cols-2 gap-2 text-sm">
          <Link href={localePath(locale, `/${industry.slug}/about`)} className="hover:underline">
            {t(locale, "nav.about")}
          </Link>
          <Link href={localePath(locale, `/${industry.slug}/contact`)} className="hover:underline">
            {t(locale, "nav.contact")}
          </Link>
          <Link href={localePath(locale, `/${industry.slug}/privacy`)} className="hover:underline">
            {t(locale, "footer.privacy")}
          </Link>
          <Link href={localePath(locale, `/${industry.slug}/terms`)} className="hover:underline">
            {t(locale, "footer.terms")}
          </Link>
          <Link href="/sitemap.xml" className="hover:underline">
            {t(locale, "footer.sitemap")}
          </Link>
          <Link href={localePath(locale, `/${industry.slug}/search`)} className="hover:underline">
            {t(locale, "nav.search")}
          </Link>
        </nav>
      </div>
    </footer>
  );
}
