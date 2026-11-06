import { t, type Locale } from "@/lib/i18n";

/**
 * Process and trust block: what happens after a request is sent.
 * Copy is deliberately plain — no urgency, no fabricated social proof.
 */
export function TrustBlock({ locale }: { locale: Locale }) {
  const steps = [
    { title: t(locale, "trust.step1Title"), body: t(locale, "trust.step1Body") },
    { title: t(locale, "trust.step2Title"), body: t(locale, "trust.step2Body") },
    { title: t(locale, "trust.step3Title"), body: t(locale, "trust.step3Body") },
  ];

  return (
    <section aria-labelledby="trust-heading" className="sn-card p-6">
      <div className="flex items-center gap-2">
        <span className="sn-kicker" aria-hidden="true" />
        <p className="sn-eyebrow">{t(locale, "trust.eyebrow")}</p>
      </div>
      <h2 id="trust-heading" className="sn-section-title mt-2 font-semibold text-[var(--sn-text)]">
        {t(locale, "trust.title")}
      </h2>
      <ol className="mt-5 grid gap-4">
        {steps.map((step, index) => (
          <li key={step.title} className="flex gap-3">
            <span className="sn-chip h-fit">{index + 1}</span>
            <div>
              <h3 className="text-sm font-semibold text-[var(--sn-text)]">{step.title}</h3>
              <p className="mt-1 text-sm leading-relaxed text-[var(--sn-muted)]">{step.body}</p>
            </div>
          </li>
        ))}
      </ol>
      <p className="mt-5 border-t border-[var(--sn-border)] pt-4 text-xs leading-relaxed text-[var(--sn-muted)]">
        {t(locale, "trust.note")}
      </p>
    </section>
  );
}
