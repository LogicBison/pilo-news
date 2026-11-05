import Link from "next/link";

import type { Industry } from "@/lib/api";
import { localePath, t, type Locale } from "@/lib/i18n";

import { LocaleSwitch } from "./LocaleSwitch";

interface HeaderProps {
  industry: Industry;
  locale: Locale;
}

export function Header({ industry, locale }: HeaderProps) {
  const home = localePath(locale, `/${industry.slug}`);
  return (
    <header className="border-b border-[var(--sn-border)] bg-[var(--sn-surface)]">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-4 py-4 sm:px-6">
        <Link href={home} className="flex flex-col leading-tight" aria-label={t(locale, "brand.name")}>
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--sn-muted)]">
            {t(locale, "brand.name")}
          </span>
          <span className="text-lg font-semibold text-[var(--sn-text)]">{industry.name}</span>
        </Link>
        <nav
          aria-label={t(locale, "nav.menu")}
          className="order-3 flex w-full flex-wrap items-center gap-x-5 gap-y-2 text-sm font-medium sm:order-2 sm:w-auto"
        >
          <Link href={home} className="hover:text-[var(--sn-accent)]">
            {t(locale, "nav.home")}
          </Link>
          <Link
            href={localePath(locale, `/${industry.slug}/about`)}
            className="hover:text-[var(--sn-accent)]"
          >
            {t(locale, "nav.about")}
          </Link>
          <Link
            href={localePath(locale, `/${industry.slug}/search`)}
            className="hover:text-[var(--sn-accent)]"
          >
            {t(locale, "nav.search")}
          </Link>
          <Link
            href={localePath(locale, `/${industry.slug}/contact`)}
            className="hover:text-[var(--sn-accent)]"
          >
            {t(locale, "nav.contact")}
          </Link>
        </nav>
        <div className="order-2 ml-auto sm:order-3">
          <LocaleSwitch locale={locale} />
        </div>
      </div>
    </header>
  );
}
