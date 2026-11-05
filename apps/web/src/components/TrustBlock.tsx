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
      <h2 id="trust-heading" className="text-xl font-semibold tracking-tight text-[var(--sn-text)]">
        {t(locale, "trust.title")}
      </h2>
      <ol className="mt-4 grid gap-4 sm:grid-cols-3">
        {steps.map((step, index) => (
          <li key={step.title}>
            <p className="sn-chip">{index + 1}</p>
            <h3 className="mt-2 text-sm font-semibold text-[var(--sn-text)]">{step.title}</h3>
            <p className="mt-1 text-sm leading-relaxed text-[var(--sn-muted)]">{step.body}</p>
          </li>
        ))}
      </ol>
      <p className="mt-4 text-xs leading-relaxed text-[var(--sn-muted)]">{t(locale, "trust.note")}</p>
    </section>
  );
}
