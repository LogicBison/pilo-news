"use client";

import { useState } from "react";

import { sessionHash, track } from "@/lib/analytics";
import { t, type Locale } from "@/lib/i18n";
import { captureUtm } from "@/lib/utm";

import { Button } from "./ui/button";
import { ConsentField } from "./ui/consent-field";
import { TextField } from "./ui/text-field";

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
          utm: captureUtm(),
          session_hash: sessionHash(),
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
      <section id="brief-signup" role="status" className="sn-brief">
        <span className="sn-chip">{t(locale, "brief.received")}</span>
        <h2 className="sn-section-title mt-3 font-semibold text-[var(--sn-text)]">
          {t(locale, "brief.title")}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-[var(--sn-text)]">{t(locale, "brief.success")}</p>
      </section>
    );
  }

  return (
    <section id="brief-signup" aria-labelledby="brief-heading" className="sn-brief">
      <div className="sn-brief-grid">
        <div>
          <div className="flex items-center gap-2">
            <span className="sn-kicker" aria-hidden="true" />
            <p className="sn-eyebrow">{t(locale, "brief.eyebrow")}</p>
          </div>
          <h2 id="brief-heading" className="sn-section-title mt-2 font-semibold text-[var(--sn-text)]">
            {t(locale, "brief.title")}
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-[var(--sn-muted)]">{t(locale, "brief.body")}</p>
          <ul className="sn-brief-list">
            <li>{t(locale, "brief.value1")}</li>
            <li>{t(locale, "brief.value2")}</li>
          </ul>
          <p className="sn-required-note mt-2">{t(locale, "common.requiredNote")}</p>
        </div>
        <form onSubmit={onSubmit} onFocus={onStart} className="grid gap-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <TextField
              label={t(locale, "brief.name")}
              name="name"
              required
              maxLength={100}
              autoComplete="given-name"
            />
            <TextField
              label={t(locale, "brief.email")}
              name="email"
              type="email"
              required
              autoComplete="email"
            />
          </div>
          <ConsentField
            name="consent"
            className="text-xs leading-relaxed text-[var(--sn-muted)]"
            boxClassName="mt-0.5 h-4 w-4"
          >
            {t(locale, "brief.consent")}
          </ConsentField>
          <input
            type="text"
            name="website"
            tabIndex={-1}
            autoComplete="off"
            aria-hidden="true"
            className="hidden"
            placeholder={t(locale, "lead.honeypot")}
          />
          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={status === "sending"}>
              {status === "sending" ? t(locale, "brief.sending") : t(locale, "brief.submit")}
            </Button>
            <p className="text-xs text-[var(--sn-muted)]">{t(locale, "brief.privacyNote")}</p>
          </div>
          {status === "error" || status === "rate-limited" ? (
            <p aria-live="polite" className="text-sm text-[var(--sn-danger)]">
              {status === "rate-limited" ? t(locale, "lead.rateLimited") : t(locale, "brief.error")}
            </p>
          ) : null}
        </form>
      </div>
    </section>
  );
}
