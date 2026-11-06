import type { BundleData } from "@/lib/api";
import { formatDay, t, type Locale } from "@/lib/i18n";

/**
 * Verifiable proof strip. Every value comes from the bundle the page already
 * fetched — no fabricated counts, no testimonials, no "1,200 readers" theatre.
 */
export function ProofStrip({ bundle, locale }: { bundle: BundleData; locale: Locale }) {
  const number = new Intl.NumberFormat(locale === "es" ? "es-ES" : "en-US");
  const facts = [
    {
      label: t(locale, "proof.stories"),
      value: number.format(bundle.total ?? bundle.items.length),
    },
    {
      label: t(locale, "proof.languages"),
      value: t(locale, "proof.languagesValue"),
    },
    {
      label: t(locale, "proof.updated"),
      value: formatDay(bundle.generated_at, locale),
    },
    {
      label: t(locale, "proof.independentLabel"),
      value: t(locale, "proof.independentValue"),
    },
  ];

  return (
    <section aria-label={t(locale, "proof.label")} className="sn-proof-band">
      <dl className="sn-proof-grid">
        {facts.map((fact) => (
          <div key={fact.label} className="sn-proof-item">
            <dt className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--sn-muted)]">
              {fact.label}
            </dt>
            <dd className="sn-proof-value">{fact.value}</dd>
          </div>
        ))}
      </dl>
      <p className="sn-proof-note">{t(locale, "proof.sourceNote")}</p>
    </section>
  );
}
