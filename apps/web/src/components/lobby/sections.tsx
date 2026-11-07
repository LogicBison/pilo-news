import Link from "next/link";

import { formatDay, t, type Locale } from "@/lib/i18n";
import { offerChips, type DeskView } from "@/lib/lobby";

import { DeskPlateLink } from "./DeskPlateLink";
import { SectionHead } from "./shell";

function pick(desks: DeskView[], key: keyof DeskView["offers"]): DeskView | undefined {
  return desks.find((desk) => desk.offers[key]);
}

const SERVICES = (locale: Locale) => (locale === "es" ? "/es/services" : "/services");

/** `point3` is the reviewer signature line: held until D-005/G2 closes. */
const CONTENT_POINTS = [1, 2, 4] as const;

export function Hero({ desks, locale }: { desks: DeskView[]; locale: Locale }) {
  return (
    <section className="lb-hero" aria-labelledby="lobby-title">
      <div>
        <p className="lb-eyebrow">
          {t(locale, "lobby.hero.eyebrow", { desks: String(desks.length) })}
        </p>
        <h1 className="lb-h1" id="lobby-title">
          {t(locale, "lobby.hero.title")}
        </h1>
        <p className="lb-lead">{t(locale, "lobby.hero.lead")}</p>
        <div className="lb-doors">
          <a className="lb-btn" href={`${locale === "es" ? "/es" : ""}#directory`}>
            {t(locale, "lobby.hero.doorReader")}
          </a>
          <Link className="lb-btn lb-btn-ghost" href={SERVICES(locale)}>
            {t(locale, "lobby.hero.doorBuyer")}
          </Link>
        </div>
        <p className="lb-note">{t(locale, "lobby.hero.note")}</p>
      </div>
      <LiveBoard desks={desks} locale={locale} />
    </section>
  );
}

export function LiveBoard({ desks, locale }: { desks: DeskView[]; locale: Locale }) {
  return (
    <div className="lb-board">
      <div className="lb-board-head">
        <span className="lb-board-title">{t(locale, "lobby.brand.tagline")}</span>
        <span className="lb-live">
          <span className="lb-live-dot" aria-hidden="true" />
          {t(locale, "lobby.board.liveLabel")}
        </span>
      </div>
      <div className="lb-board-scroll">
        <table>
          <caption className="sr-only">
            {t(locale, "lobby.a11y.boardCaption", { desks: String(desks.length) })}
          </caption>
          <thead>
            <tr>
              <th scope="col">{t(locale, "lobby.board.headDesk")}</th>
              <th scope="col">{t(locale, "lobby.board.headUpdates")}</th>
              <th scope="col">{t(locale, "lobby.board.headLanguages")}</th>
              <th scope="col">{t(locale, "lobby.board.headFiled")}</th>
            </tr>
          </thead>
          <tbody>
            {desks.map((desk) => (
              <tr key={desk.slug}>
                <td className="lb-desk-name">
                  <a href={desk.href}>{desk.name}</a>
                </td>
                <td>{t(locale, "lobby.board.everyHours", { hours: String(desk.hours) })}</td>
                <td>{desk.locales.map((code) => code.toUpperCase()).join(" · ")}</td>
                <td>{desk.latest ? formatDay(desk.latest, locale) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="lb-board-foot">{t(locale, "lobby.board.summary")}</p>
    </div>
  );
}

export function DirectoryBoard({ desks, locale }: { desks: DeskView[]; locale: Locale }) {
  return (
    <section className="lb-section" id="directory" aria-labelledby="directory-title">
      <SectionHead
        id="directory-title"
        numeral="01"
        eyebrow={t(locale, "lobby.dir.eyebrow")}
        title={t(locale, "lobby.dir.title", { desks: String(desks.length) })}
      />
      <p className="lb-body">{t(locale, "lobby.dir.intro")}</p>
      <div className="lb-dir" style={{ marginTop: "28px" }}>
        {desks.map((desk) => (
          <DeskPlate key={desk.slug} desk={desk} locale={locale} />
        ))}
      </div>
    </section>
  );
}

function DeskPlate({ desk, locale }: { desk: DeskView; locale: Locale }) {
  return (
    <DeskPlateLink
      href={desk.href}
      slug={desk.slug}
      locale={locale}
      accent={desk.accent}
      label={t(locale, "lobby.a11y.plate", { name: desk.name, tagline: desk.tagline })}
    >
      <span className="lb-plate-name">{desk.name}</span>
      <span className="lb-plate-tagline">{desk.tagline}</span>
      <span className="lb-plate-chips">
        {offerChips(desk).map((chip) => (
          <span key={chip.key} className="lb-chip">
            {t(locale, chip.label)}
          </span>
        ))}
        {desk.locales.map((code) => (
          <span key={code} className="lb-chip lb-chip-code">
            {code.toUpperCase()}
          </span>
        ))}
      </span>
      <span className="lb-plate-arrow" aria-hidden="true">
        →
      </span>
    </DeskPlateLink>
  );
}

export function OfferCards({ desks, locale }: { desks: DeskView[]; locale: Locale }) {
  const cards = [
    { key: "asset", desk: pick(desks, "asset") },
    { key: "question", desk: pick(desks, "question") },
    { key: "specialist", desk: pick(desks, "consultation") },
  ].filter((card) => card.desk) as { key: string; desk: DeskView }[];

  if (cards.length === 0) return null;
  return (
    <section className="lb-section" id="offers" aria-labelledby="offers-title">
      <SectionHead
        id="offers-title"
        numeral="02"
        eyebrow={t(locale, "lobby.offer.eyebrow")}
        title={t(locale, "lobby.offer.title")}
      />
      <div className="lb-cards">
        {cards.map(({ key, desk }) => (
          <article key={key} className="lb-card">
            <h3 className="lb-h3">{t(locale, `lobby.offer.${key}.title`)}</h3>
            <p>{t(locale, `lobby.offer.${key}.body`)}</p>
            <a className="lb-link" href={desk.href}>
              {t(locale, `lobby.offer.${key}.cta`)} →
            </a>
          </article>
        ))}
      </div>
    </section>
  );
}

export function MethodSteps({ locale }: { locale: Locale }) {
  const steps = [1, 2, 3] as const;
  return (
    <section className="lb-section" id="method" aria-labelledby="method-title">
      <SectionHead
        id="method-title"
        numeral="03"
        eyebrow={t(locale, "lobby.how.eyebrow")}
        title={t(locale, "lobby.how.title")}
      />
      <div className="lb-steps">
        {steps.map((step) => (
          <div key={step} className="lb-step">
            <h3 className="lb-h3">{t(locale, `lobby.how.step${step}Title`)}</h3>
            <p className="lb-body">{t(locale, `lobby.how.step${step}Body`)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function ServiceBand({ locale, count }: { locale: Locale; count: number | null }) {
  const scopeHref = `${SERVICES(locale)}#scope`;
  // A failed API must not print "the 0 desks": the copy drops the number
  // instead of stating something false.
  const intro =
    count === null
      ? t(locale, "lobby.services.introFallback")
      : t(locale, "lobby.services.intro", { desks: String(count) });
  const points = [1, 2, 3, 4] as const;
  return (
    <section className="lb-band" id="services" aria-labelledby="services-title">
      <div className="lb-section-head">
        <span className="lb-numeral" aria-hidden="true">
          04
        </span>
        <div>
          <p className="lb-eyebrow">{t(locale, "lobby.services.eyebrow")}</p>
          <h2 className="lb-h2" id="services-title">
            {t(locale, "lobby.services.title")}
          </h2>
        </div>
        <span className="lb-rule" aria-hidden="true" />
      </div>
      <p className="lb-lead">{intro}</p>
      <div className="lb-service-grid">
        <article className="lb-service">
          <span className="lb-service-numeral" aria-hidden="true">
            01
          </span>
          <h3>{t(locale, "lobby.services.news.title")}</h3>
          <p>{t(locale, "lobby.services.news.body")}</p>
          <ul>
            {points.map((point) => (
              <li key={point}>{t(locale, `lobby.services.news.point${point}`)}</li>
            ))}
          </ul>
          <p className="lb-for">{t(locale, "lobby.services.news.for")}</p>
        </article>
        <article className="lb-service">
          <span className="lb-service-numeral" aria-hidden="true">
            02
          </span>
          <h3>{t(locale, "lobby.services.content.title")}</h3>
          <p>{t(locale, "lobby.services.content.body")}</p>
          <ul>
            {/* G2 open: `services.content.signature` is withheld until a
                reviewer is named, so the list is 1, 2, 4 - not 1..4. */}
            {(CONTENT_POINTS as unknown as number[]).map((point: number) => (
              <li key={point}>{t(locale, `lobby.services.content.point${point}`)}</li>
            ))}
          </ul>
          <p className="lb-for">{t(locale, "lobby.services.content.for")}</p>
        </article>
      </div>
      <div className="lb-doors" style={{ marginTop: "28px" }}>
        <Link className="lb-btn" href={scopeHref}>
          {t(locale, "lobby.services.cta")}
        </Link>
      </div>
    </section>
  );
}

export function ProcessSteps({ locale }: { locale: Locale }) {
  const steps = [1, 2, 3, 4] as const;
  return (
    <section className="lb-section" id="process" aria-labelledby="process-title">
      <SectionHead
        id="process-title"
        numeral="05"
        eyebrow={t(locale, "lobby.engage.eyebrow")}
        title={t(locale, "lobby.engage.title")}
      />
      <div className="lb-process">
        {steps.map((step) => (
          <div key={step} className="lb-step">
            <h3 className="lb-h3">{t(locale, `lobby.engage.step${step}Title`)}</h3>
            <p className="lb-body">{t(locale, `lobby.engage.step${step}Body`)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function LobbyFaq({ locale }: { locale: Locale }) {
  const questions = [1, 2, 3, 4, 5, 6, 7, 8] as const;
  return (
    <section className="lb-section" id="questions" aria-labelledby="questions-title">
      <SectionHead
        id="questions-title"
        numeral="06"
        eyebrow={t(locale, "lobby.faq.eyebrow")}
        title={t(locale, "lobby.faq.title")}
      />
      <div className="lb-faq">
        {questions.map((n) => (
          <details key={n}>
            <summary>{t(locale, `lobby.faq.q${n}`)}</summary>
            <p>{t(locale, `lobby.faq.a${n}`)}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

export function FinalDoors({ locale, desks }: { locale: Locale; desks: DeskView[] }) {
  return (
    <section className="lb-section" aria-labelledby="final-title">
      <div className="lb-section-head">
        <span className="lb-numeral" aria-hidden="true">
          08
        </span>
        <h2 className="lb-h2" id="final-title">
          {t(locale, "lobby.final.title")}
        </h2>
        <span className="lb-rule" aria-hidden="true" />
      </div>
      <div className="lb-doors-final">
        <a className="lb-door" href={`${locale === "es" ? "/es" : ""}#directory`}>
          <h3>{t(locale, "lobby.final.readerTitle")}</h3>
          <p>{t(locale, "lobby.final.readerBody", { desks: String(desks.length) })}</p>
          <span className="lb-link">{t(locale, "lobby.final.readerCta")} →</span>
        </a>
        <Link className="lb-door lb-door-inverse" href={`${SERVICES(locale)}#scope`}>
          <h3>{t(locale, "lobby.final.buyerTitle")}</h3>
          <p>{t(locale, "lobby.final.buyerBody")}</p>
          <span className="lb-link">{t(locale, "lobby.final.buyerCta")} →</span>
        </Link>
      </div>
    </section>
  );
}

export function DirectoryUnavailable({ locale }: { locale: Locale }) {
  return (
    <div className="lb-empty" role="status">
      {/* The degraded page still needs its one h1. */}
      <h1 className="lb-h2" style={{ margin: 0 }}>
        {t(locale, "lobby.dir.emptyTitle")}
      </h1>
      <p>{t(locale, "lobby.dir.emptyBody")}</p>
      <p style={{ marginTop: "16px" }}>
        <a className="lb-link" href={locale === "es" ? "/es" : "/"}>
          {t(locale, "lobby.dir.retry")}
        </a>
      </p>
    </div>
  );
}
