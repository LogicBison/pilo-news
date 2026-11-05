import type { Industry } from "@/lib/api";
import { t, type Locale } from "@/lib/i18n";
import { localized } from "@/lib/theme";

import { CtaButton } from "./Cta";

export function CtaCard({
  industry,
  locale,
  placement,
  articleId,
  compact = false,
}: {
  industry: Industry;
  locale: Locale;
  placement: "hero" | "article" | "about" | "search" | "footer";
  articleId?: string;
  compact?: boolean;
}) {
  const headline = localized(industry.cta.headline, locale) || t(locale, "lead.title");
  const body = localized(industry.cta.body, locale) || t(locale, "lead.intro");
  const label = localized(industry.cta.label, locale) || t(locale, "cta.primary");

  return (
    <aside
      aria-label={headline}
      className={`rounded-[var(--sn-radius)] border border-[var(--sn-border)] bg-[var(--sn-surface)] ${
        compact ? "p-4" : "p-6"
      }`}
    >
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--sn-accent)]">
        {t(locale, "cta.primary")}
      </p>
      <h2 className={`mt-2 font-semibold text-[var(--sn-text)] ${compact ? "text-lg" : "text-2xl"}`}>
        {headline}
      </h2>
      {!compact ? <p className="mt-2 text-sm leading-relaxed text-[var(--sn-muted)]">{body}</p> : null}
      <div className="mt-4">
        <CtaButton
          industry={industry.slug}
          locale={locale}
          placement={placement}
          articleId={articleId}
          label={label}
        />
      </div>
      <p className="mt-3 text-xs leading-relaxed text-[var(--sn-muted)]">{industry.disclaimer}</p>
    </aside>
  );
}
