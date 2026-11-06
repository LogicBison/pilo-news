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
  const promises = [t(locale, "cta.promise1"), t(locale, "cta.promise2"), t(locale, "cta.promise3")];

  return (
    <aside
      aria-label={headline}
      className={`sn-cta sn-action self-start ${compact ? "p-4" : "p-6 md:p-7"}`}
    >
      <div className="sn-action-inner">
        <div>
          <div className="flex items-center gap-2">
            <span className="sn-kicker" aria-hidden="true" />
            <p className="sn-eyebrow">{t(locale, "cta.primary")}</p>
          </div>
          <h2
            className={`mt-2 font-bold tracking-tight text-[var(--sn-text)] ${
              compact ? "text-lg" : "text-2xl leading-tight"
            }`}
          >
            {headline}
          </h2>
          {!compact ? (
            <p className="mt-2 text-sm leading-relaxed text-[var(--sn-muted)]">{body}</p>
          ) : null}
          {!compact ? (
            <div className="sn-action-promises mt-4">
              {promises.map((promise) => (
                <span key={promise}>{promise}</span>
              ))}
            </div>
          ) : null}
        </div>
        <div className={compact ? "mt-4" : "mt-5 md:mt-0"}>
          <CtaButton
            industry={industry.slug}
            locale={locale}
            placement={placement}
            articleId={articleId}
            label={label}
          />
          <p className="mt-3">
            <a href="#brief-signup" className="sn-action-link">
              {t(locale, "cta.briefLink")}
            </a>
          </p>
          <p className="sn-action-disclaimer mt-3">{industry.disclaimer}</p>
        </div>
      </div>
    </aside>
  );
}
