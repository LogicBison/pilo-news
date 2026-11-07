import type { Metadata } from "next";

import { t, type Locale } from "@/lib/i18n";
import { deskViews } from "@/lib/lobby";
import { pageMetadata } from "@/lib/seo";

import {
  DirectoryBoard,
  DirectoryUnavailable,
  FinalDoors,
  Hero,
  LobbyFaq,
  MethodSteps,
  OfferCards,
  ProcessSteps,
  ServiceBand,
} from "./sections";
import { ServiceForm } from "./ServiceForm";
import { LobbyShell, SectionHead } from "./shell";

/**
 * The lobby's contact form: the same fields, endpoint and consent as every
 * channel contact page, with no industry attached — a message from the apex
 * belongs to the network, not to a desk.
 */
export function ContactSection({ locale }: { locale: Locale }) {
  const privacyHref = locale === "es" ? "/es/privacy" : "/privacy";
  return (
    <section className="lb-section" id="contact" aria-labelledby="contact-title">
      <SectionHead
        id="contact-title"
        numeral="07"
        eyebrow={t(locale, "lobby.contact.eyebrow")}
        title={t(locale, "lobby.contact.title")}
      />
      <div className="lb-form-wrap">
        <p className="lb-body">{t(locale, "lobby.contact.intro")}</p>
        <ServiceForm
          locale={locale}
          sourcePage={locale === "es" ? "/es" : "/"}
          privacyHref={privacyHref}
          submitLabel={t(locale, "lobby.contact.submit")}
          placement="lobby-contact"
        />
      </div>
    </section>
  );
}

export function lobbyMetadata(locale: Locale): Promise<Metadata> {
  return pageMetadata({
    title: t(locale, "lobby.meta.title"),
    description: t(locale, "lobby.meta.description"),
    path: "/",
    locale,
    absoluteTitle: true,
  });
}

export function servicesMetadata(locale: Locale): Promise<Metadata> {
  return pageMetadata({
    title: t(locale, "lobby.servicesMeta.title"),
    description: t(locale, "lobby.servicesMeta.description"),
    path: "/services",
    locale,
    absoluteTitle: true,
  });
}

function footerDesks(desks: { slug: string; name: string; href: string }[]) {
  return desks.map((desk) => ({ slug: desk.slug, name: desk.name, href: desk.href }));
}

export async function LobbyPage({ locale }: { locale: Locale }) {
  const { ok, desks } = await deskViews(locale);

  if (!ok) {
    return (
      <LobbyShell locale={locale} path="" desks={[]}>
        <div style={{ paddingTop: "64px" }}>
          <DirectoryUnavailable locale={locale} />
        </div>
        <LobbyFaq locale={locale} />
      </LobbyShell>
    );
  }

  return (
    <LobbyShell locale={locale} path="" desks={footerDesks(desks)}>
      <Hero desks={desks} locale={locale} />
      <DirectoryBoard desks={desks} locale={locale} />
      <OfferCards desks={desks} locale={locale} />
      <MethodSteps locale={locale} />
      <ServiceBand locale={locale} count={desks.length} />
      <ProcessSteps locale={locale} />
      <LobbyFaq locale={locale} />
      <ContactSection locale={locale} />
      <FinalDoors locale={locale} desks={desks} />
    </LobbyShell>
  );
}

export async function ServicesPage({ locale }: { locale: Locale }) {
  const { ok, desks } = await deskViews(locale);
  const privacyHref = locale === "es" ? "/es/privacy" : "/privacy";
  const sourcePage = locale === "es" ? "/es/services" : "/services";

  return (
    <LobbyShell locale={locale} path="/services" desks={footerDesks(desks)}>
      <section className="lb-hero" aria-labelledby="services-page-title">
        <div>
          <p className="lb-eyebrow">{t(locale, "lobby.services.eyebrow")}</p>
          <h1 className="lb-h1" id="services-page-title">
            {t(locale, "lobby.services.title")}
          </h1>
          <p className="lb-lead">
            {ok
              ? t(locale, "lobby.services.intro", { desks: String(desks.length) })
              : t(locale, "lobby.services.introFallback")}
          </p>
          <div className="lb-doors">
            <a className="lb-btn" href="#scope">
              {t(locale, "lobby.services.cta")}
            </a>
          </div>
        </div>
        <div className="lb-board">
          <div className="lb-board-head">
            <span className="lb-board-title">{t(locale, "lobby.engage.title")}</span>
          </div>
          <div style={{ padding: "16px" }}>
            <ol className="lb-steps" style={{ gridTemplateColumns: "1fr", gap: "16px" }}>
              {([1, 2, 3, 4] as const).map((step) => (
                <li key={step} className="lb-step" style={{ listStyle: "none" }}>
                  <h3 className="lb-h3">{t(locale, `lobby.engage.step${step}Title`)}</h3>
                  <p className="lb-body">{t(locale, `lobby.engage.step${step}Body`)}</p>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      <ServiceBand locale={locale} count={ok ? desks.length : null} />

      <section className="lb-section" id="scope" aria-labelledby="scope-title">
        <SectionHead
          id="scope-title"
          numeral="05"
          eyebrow={t(locale, "lobby.form.title")}
          title={t(locale, "lobby.form.title")}
        />
        <div className="lb-form-wrap">
          <div>
            <p className="lb-body">{t(locale, "lobby.form.intro")}</p>
          </div>
          <ServiceForm locale={locale} sourcePage={sourcePage} privacyHref={privacyHref} />
        </div>
      </section>
    </LobbyShell>
  );
}

export async function LegalPage({
  locale,
  kind,
}: {
  locale: Locale;
  kind: "privacy" | "terms";
}) {
  const { desks } = await deskViews(locale);
  const title =
    kind === "privacy"
      ? t(locale, "lobby.legal.privacyTitle")
      : t(locale, "lobby.legal.termsTitle");
  const body =
    kind === "privacy" ? t(locale, "lobby.legal.privacyBody") : t(locale, "lobby.legal.termsBody");

  return (
    <LobbyShell locale={locale} path="" desks={footerDesks(desks)}>
      <article className="lb-section" style={{ paddingTop: "56px", maxWidth: "68ch" }}>
        <p className="lb-eyebrow">{t(locale, "lobby.brand.name")}</p>
        <h1 className="lb-h1" style={{ fontSize: "clamp(32px, 4vw, 46px)" }}>
          {title}
        </h1>
        <p className="lb-note">{t(locale, "lobby.legal.updated")}</p>
        <p className="lb-lead" style={{ marginTop: "24px" }}>
          {body}
        </p>
      </article>
    </LobbyShell>
  );
}
