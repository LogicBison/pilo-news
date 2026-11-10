import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";

import { DevelopedBy } from "@/components/DevelopedBy";
import { t, type Locale } from "@/lib/i18n";

import "./lobby.css";

export const DESK_EMAIL = process.env.CONTACT_TO ?? "news@heraldfox.com";

/** `""` for the lobby root, `"/services"` for the services page, `"/bot"` for
 *  the crawler page the user agent advertises. */
export type LobbyPath = "" | "/services" | "/bot";

function localized(locale: Locale, path: LobbyPath): string {
  const suffix = locale === "es" ? "/es" : "";
  return `${suffix}${path}` || "/";
}

/**
 * EN ⇄ ES on the same page, both locales on the apex.
 *
 * Plain anchors, not <Link>: the root layout renders `<html lang>` from the
 * request header, and a client-side navigation keeps the layout mounted, so the
 * document would keep the previous language. A full load is correct here and
 * costs nothing on two pages.
 */
function LanguageSwitch({ locale, path }: { locale: Locale; path: LobbyPath }) {
  return (
    <div className="lb-lang" role="group" aria-label={t(locale, "lobby.a11y.languageSwitch")}>
      <a href={localized("en", path)} hrefLang="en" aria-current={locale === "en" ? "true" : undefined}>
        EN
      </a>
      <a href={localized("es", path)} hrefLang="es" aria-current={locale === "es" ? "true" : undefined}>
        ES
      </a>
    </div>
  );
}

/** The lobby's own root for the current locale: `/` or `/es`, never the
 *  current page — otherwise `#directory` points at a section that only exists
 *  on the lobby and the click does nothing. */
function lobbyRoot(locale: Locale): string {
  return locale === "es" ? "/es" : "/";
}

export function Masthead({ locale, path }: { locale: Locale; path: LobbyPath }) {
  const root = lobbyRoot(locale);
  const servicesHref = localized(locale, "/services");
  return (
    <header className="lb-mast">
      <div className="lb-mast-inner">
        <Link href={root} className="lb-brand" aria-label={t(locale, "lobby.brand.name")}>
          <Image
            src="/brand/heraldfox-emblem.png"
            alt=""
            aria-hidden="true"
            width={32}
            height={32}
            loading="eager"
            className="lb-brand-emblem"
          />
          {t(locale, "lobby.brand.name")}
          <span className="lb-brand-small">{t(locale, "lobby.brand.tagline")}</span>
        </Link>
        <nav className="lb-nav" aria-label={t(locale, "lobby.nav.desks")}>
          <a href={`${root}#directory`}>{t(locale, "lobby.nav.desks")}</a>
          <Link href={servicesHref}>{t(locale, "lobby.nav.services")}</Link>
          <a href={`${root}#questions`}>{t(locale, "lobby.spine.questions")}</a>
          <a href={`${root}#contact`}>{t(locale, "lobby.nav.contact")}</a>
        </nav>
        <LanguageSwitch locale={locale} path={path} />
      </div>
    </header>
  );
}

const SECTIONS = [
  { id: "directory", key: "lobby.spine.directory", numeral: "01" },
  { id: "offers", key: "lobby.spine.offers", numeral: "02" },
  { id: "method", key: "lobby.spine.method", numeral: "03" },
  { id: "services", key: "lobby.spine.services", numeral: "04" },
  { id: "process", key: "lobby.spine.process", numeral: "05" },
  { id: "questions", key: "lobby.spine.questions", numeral: "06" },
  { id: "contact", key: "lobby.nav.contact", numeral: "07" },
] as const;

/**
 * The wayfinding spine: the page's section index, as signage. On the services
 * and legal pages those sections are not on the page, so the links resolve
 * against the lobby root.
 */
export function Rail({ locale }: { locale: Locale }) {
  const root = lobbyRoot(locale);
  return (
    <nav className="lb-rail" aria-label={t(locale, "lobby.spine.directory")}>
      <span className="lb-rail-line" aria-hidden="true" />
      {SECTIONS.map((section) => (
        <a key={section.id} href={`${root}#${section.id}`}>
          {section.numeral} {t(locale, section.key)}
        </a>
      ))}
    </nav>
  );
}

export function SectionHead({
  numeral,
  eyebrow,
  title,
  id,
}: {
  numeral: string;
  eyebrow: string;
  title: string;
  id: string;
}) {
  return (
    <div className="lb-section-head">
      <span className="lb-numeral" aria-hidden="true">
        {numeral}
      </span>
      <div>
        <p className="lb-eyebrow">{eyebrow}</p>
        <h2 className="lb-h2" id={id}>
          {title}
        </h2>
      </div>
      <span className="lb-rule" aria-hidden="true" />
    </div>
  );
}

export function LobbyFooter({
  locale,
  desks,
}: {
  locale: Locale;
  desks: { slug: string; name: string; href: string }[];
}) {
  const root = lobbyRoot(locale);
  return (
    <footer className="lb-foot">
      <div className="lb-foot-grid">
        <div>
          <p className="lb-brand">
            <Image
              src="/brand/heraldfox-emblem.png"
              alt=""
              aria-hidden="true"
              width={24}
              height={24}
              loading="eager"
              className="lb-brand-emblem"
            />
            {t(locale, "lobby.brand.name")}
          </p>
          <p className="lb-body" style={{ maxWidth: "34ch" }}>
            {desks.length === 0
              ? t(locale, "lobby.footer.blurbFallback")
              : t(locale, "lobby.footer.blurb", {
                  brand: t(locale, "lobby.brand.name"),
                  desks: String(desks.length),
                })}
          </p>
        </div>
        <div>
          <h2>{t(locale, "lobby.footer.desksTitle")}</h2>
          <ul>
            {desks.map((desk) => (
              <li key={desk.slug}>
                <a href={desk.href}>{desk.name}</a>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h2>{t(locale, "lobby.footer.companyTitle")}</h2>
          <ul>
            <li>
              <Link href={localized(locale, "/services")}>{t(locale, "lobby.nav.services")}</Link>
            </li>
            <li>
              <a href={`${root}#contact`}>{t(locale, "lobby.nav.contact")}</a>
            </li>
            <li>
              <a href={`${root}#offers`}>{t(locale, "lobby.spine.offers")}</a>
            </li>
            <li>
              <Link href={`${locale === "es" ? "/es" : ""}/privacy`}>
                {t(locale, "footer.privacy")}
              </Link>
            </li>
            <li>
              <Link href={`${locale === "es" ? "/es" : ""}/terms`}>{t(locale, "footer.terms")}</Link>
            </li>
          </ul>
        </div>
        <div>
          <h2>{t(locale, "lobby.footer.followTitle")}</h2>
          <ul>
            <li>
              <a href={`mailto:${DESK_EMAIL}`}>{DESK_EMAIL}</a>
            </li>
            <li>
              <Link href={localized(locale, "/services")}>{t(locale, "lobby.nav.cta")}</Link>
            </li>
          </ul>
        </div>
      </div>
      <div className="lb-foot-legal">
        <span>{t(locale, "lobby.footer.legal")}</span>
        <DevelopedBy locale={locale} />
        <span>
          © {new Date().getFullYear()} {t(locale, "lobby.brand.name")}
        </span>
      </div>
    </footer>
  );
}

/** The page frame: skip link, masthead, spine, main, footer. */
export function LobbyShell({
  locale,
  path,
  desks,
  children,
}: {
  locale: Locale;
  path: LobbyPath;
  desks: { slug: string; name: string; href: string }[];
  children: ReactNode;
}) {
  return (
    <div className="lb-root" data-lobby="">
      <a href={`${lobbyRoot(locale)}#directory`} className="lb-skip">
        {t(locale, "lobby.a11y.skipLink")}
      </a>
      <Masthead locale={locale} path={path} />
      <div className="lb-shell">
        <Rail locale={locale} />
        <main className="lb-main" id="main">
          {children}
        </main>
      </div>
      <div className="lb-shell">
        <div aria-hidden="true" />
        <LobbyFooter locale={locale} desks={desks} />
      </div>
    </div>
  );
}
