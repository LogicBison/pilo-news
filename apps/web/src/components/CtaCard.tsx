import type { Industry } from "@/lib/api";
import { assetFor } from "@/lib/assets";
import { localePath, t, type Locale } from "@/lib/i18n";
import { offersOf } from "@/lib/offers";
import { localized } from "@/lib/theme";
import { channelBase } from "@/lib/url";

import { CtaButton } from "./Cta";

export async function CtaCard({
  industry,
  locale,
  placement,
  articleId,
  compact = false,
}: {
  industry: Industry;
  locale: Locale;
  placement: "hero" | "article" | "topic" | "about" | "search" | "footer";
  articleId?: string;
  compact?: boolean;
}) {
  const base = await channelBase(industry.slug);
  const headline = localized(industry.cta.headline, locale) || t(locale, "lead.title");
  const body = localized(industry.cta.body, locale) || t(locale, "lead.intro");
  const label = localized(industry.cta.label, locale) || t(locale, "cta.primary");
  const offers = offersOf(industry);
  const assetOnPage =
    placement !== "topic" && Boolean(industry.cta.asset && assetFor(industry.cta.asset));
  const leadHref =
    placement === "topic"
      ? `${localePath(locale, base || "/")}#lead-form`
      : "#lead-form";
  const promises = [t(locale, "cta.promise1"), t(locale, "cta.promise2"), t(locale, "cta.promise3")];

  return (
    <section
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
            href={leadHref}
          />
          {offers.brief || (offers.asset && assetOnPage) ? (
            <p className="mt-3">
              {offers.brief ? (
                <a href="#brief-signup" className="sn-action-link">
                  {t(locale, "cta.briefLink")}
                </a>
              ) : (
                <a href="#asset-heading" className="sn-action-link">
                  {t(locale, "cta.assetLink")}
                </a>
              )}
            </p>
          ) : null}
          <p className="sn-action-disclaimer mt-3">{industry.disclaimer}</p>
        </div>
      </div>
    </section>
  );
}
