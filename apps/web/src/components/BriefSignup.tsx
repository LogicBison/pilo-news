"use client";

import { useState } from "react";

import { track } from "@/lib/analytics";
import { t, type Locale } from "@/lib/i18n";

type Status = "idle" | "sending" | "success" | "error" | "rate-limited";

interface BriefSignupProps {
  industry: string;
  locale: Locale;
  placement: string;
  articleId?: string;
  sourcePage: string;
}

/**
 * L2 rung of the offer ladder: capture interest without asking for a phone
 * number or a message. The lead API requires a name, so the form asks for one;
 * everything else is optional. Delivery of the brief itself waits on U8.
 */
export function BriefSignup({ industry, locale, placement, articleId, sourcePage }: BriefSignupProps) {
  const [status, setStatus] = useState<Status>("idle");
  const [started, setStarted] = useState(false);

  const onStart = () => {
    if (started) return;
    setStarted(true);
    track("lead_form_start", { industry, locale, placement, articleId });
  };

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setStatus("sending");
    try {
      const response = await fetch("/api/proxy/v1/leads", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          industry,
          kind: "brief",
          name: data.get("name"),
          email: data.get("email"),
          locale,
          consent: data.get("consent") === "on",
          source_page: sourcePage,
          article_id: articleId ?? null,
          website: data.get("website") || null,
        }),
      });
      if (response.status === 429) {
        setStatus("rate-limited");
        track("lead_submit", { industry, locale, placement, articleId, result: "rate_limited" });
        return;
      }
      if (!response.ok) {
        setStatus("error");
        track("lead_submit", { industry, locale, placement, articleId, result: "error" });
        return;
      }
      setStatus("success");
      track("lead_submit", { industry, locale, placement, articleId, result: "ok" });
      form.reset();
    } catch {
      setStatus("error");
      track("lead_submit", { industry, locale, placement, articleId, result: "error" });
    }
  }

  if (status === "success") {
    return (
      <section role="status" className="sn-card sn-card-surface p-5">
        <h2 className="text-lg font-semibold text-[var(--sn-text)]">{t(locale, "brief.title")}</h2>
        <p className="mt-2 text-sm leading-relaxed text-[var(--sn-text)]">{t(locale, "brief.success")}</p>
      </section>
    );
  }

  return (
    <section aria-labelledby="brief-heading" className="sn-card p-5">
      <h2 id="brief-heading" className="text-lg font-semibold text-[var(--sn-text)]">
        {t(locale, "brief.title")}
      </h2>
      <p className="mt-1 text-sm leading-relaxed text-[var(--sn-muted)]">{t(locale, "brief.body")}</p>
      <form onSubmit={onSubmit} onFocus={onStart} className="mt-4 grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "brief.name")}
          <input name="name" required maxLength={100} autoComplete="given-name" className="sn-input" />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "brief.email")}
          <input
            name="email"
            type="email"
            required
            autoComplete="email"
            className="sn-input"
          />
        </label>
        <label className="flex items-start gap-2 text-xs leading-relaxed text-[var(--sn-muted)] sm:col-span-2">
          <input type="checkbox" name="consent" required className="mt-0.5 h-4 w-4" />
          <span>{t(locale, "brief.consent")}</span>
        </label>
        <input
          type="text"
          name="website"
          tabIndex={-1}
          autoComplete="off"
          aria-hidden="true"
          className="hidden"
          placeholder={t(locale, "lead.honeypot")}
        />
        <div className="flex flex-wrap items-center gap-3 sm:col-span-2">
          <button type="submit" className="sn-btn" disabled={status === "sending"}>
            {status === "sending" ? t(locale, "brief.sending") : t(locale, "brief.submit")}
          </button>
          <p className="text-xs text-[var(--sn-muted)]">{t(locale, "brief.privacyNote")}</p>
        </div>
        {status === "error" || status === "rate-limited" ? (
          <p aria-live="polite" className="text-sm text-[var(--sn-danger,#b91c1c)] sm:col-span-2">
            {status === "rate-limited" ? t(locale, "lead.rateLimited") : t(locale, "brief.error")}
          </p>
        ) : null}
      </form>
    </section>
  );
}
