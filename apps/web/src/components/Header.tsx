import Link from "next/link";

import type { Industry } from "@/lib/api";
import { localePath, t, type Locale } from "@/lib/i18n";
import { channelBase } from "@/lib/url";
import { resolveSkin } from "@/lib/skins";

import { LocaleSwitch } from "./LocaleSwitch";
import { SkinEmblem } from "./SkinEmblem";

interface HeaderProps {
  industry: Industry;
  locale: Locale;
}

export async function Header({ industry, locale }: HeaderProps) {
  const base = await channelBase(industry.slug);
  const home = localePath(locale, base || "/");
  const skin = resolveSkin(industry.slug, industry.theme.layout);
  const nav = [
    { href: home, label: t(locale, "nav.home") },
    { href: localePath(locale, `${base}/about`), label: t(locale, "nav.about") },
    { href: localePath(locale, `${base}/search`), label: t(locale, "nav.search") },
    { href: localePath(locale, `${base}/contact`), label: t(locale, "nav.contact") },
  ];
  return (
    <header className="sn-appbar">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-3 px-4 py-3 sm:px-6">
        <Link href={home} className="flex items-center gap-3" aria-label={t(locale, "brand.name")}>
          <span className="sn-brandmark" aria-hidden="true">
            <SkinEmblem skin={skin} />
          </span>
          <span className="flex flex-col leading-tight">
            <span className="text-[0.68rem] font-bold uppercase tracking-[0.18em] text-[var(--sn-muted)]">
              {t(locale, "brand.name")}
            </span>
            <span className="text-base font-bold text-[var(--sn-text)] sm:text-lg">
              {industry.name}
            </span>
          </span>
        </Link>
        <nav
          aria-label={t(locale, "nav.menu")}
          className="order-3 flex w-full flex-wrap items-center gap-1 border-t border-[var(--sn-border)] pt-2 sm:order-2 sm:w-auto sm:border-0 sm:pt-0"
        >
          {nav.map((item) => (
            <Link key={item.href} href={item.href} className="sn-nav-link">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="order-2 ml-auto sm:order-3">
          <LocaleSwitch locale={locale} />
        </div>
      </div>
    </header>
  );
}
