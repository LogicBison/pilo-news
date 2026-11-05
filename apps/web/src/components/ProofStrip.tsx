import type { BundleData } from "@/lib/api";
import { formatDate, t, type Locale } from "@/lib/i18n";

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
      value: formatDate(bundle.generated_at, locale),
    },
  ];

  return (
    <section aria-label={t(locale, "proof.label")} className="mt-6">
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {facts.map((fact) => (
          <div key={fact.label} className="sn-card sn-card-surface px-4 py-3">
            <dt className="text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-[var(--sn-muted)]">
              {fact.label}
            </dt>
            <dd className="mt-1 text-sm font-semibold text-[var(--sn-text)]">{fact.value}</dd>
          </div>
        ))}
        <div className="sn-card sn-card-surface px-4 py-3">
          <dt className="text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-[var(--sn-muted)]">
            {t(locale, "proof.independentLabel")}
          </dt>
          <dd className="mt-1 text-sm font-semibold text-[var(--sn-text)]">
            {t(locale, "proof.independentValue")}
          </dd>
        </div>
      </dl>
    </section>
  );
}
