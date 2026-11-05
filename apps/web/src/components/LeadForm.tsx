"use client";

import { useState } from "react";

import { track } from "@/lib/analytics";
import { t, type Locale } from "@/lib/i18n";

interface LeadFormProps {
  industry: string;
  industryName: string;
  locale: Locale;
  kind: "consultation" | "brief";
  placement: string;
  articleId?: string;
  sourcePage: string;
}

type Status = "idle" | "sending" | "success" | "error" | "rate-limited";

export function LeadForm({
  industry,
  industryName,
  locale,
  kind,
  placement,
  articleId,
  sourcePage,
}: LeadFormProps) {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [started, setStarted] = useState(false);
  const logistics = industry === "logistics";

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
    setMessage("");
    try {
      const response = await fetch("/api/proxy/v1/leads", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          industry,
          kind,
          name: data.get("name"),
          email: data.get("email"),
          phone: data.get("phone") || null,
          company: data.get("company") || null,
          message: data.get("message") || null,
          locale,
          consent: data.get("consent") === "on",
          source_page: sourcePage,
          article_id: articleId ?? null,
          website: data.get("website") || null,
        }),
      });
      if (response.status === 429) {
        setStatus("rate-limited");
        setMessage(t(locale, "lead.rateLimited"));
        track("lead_submit", { industry, locale, placement, articleId, result: "rate_limited" });
        return;
      }
      if (!response.ok) {
        setStatus("error");
        setMessage(t(locale, "lead.error"));
        track("lead_submit", { industry, locale, placement, articleId, result: "error" });
        return;
      }
      setStatus("success");
      setMessage(t(locale, "lead.success"));
      track("lead_submit", { industry, locale, placement, articleId, result: "ok" });
      form.reset();
    } catch {
      setStatus("error");
      setMessage(t(locale, "lead.error"));
      track("lead_submit", { industry, locale, placement, articleId, result: "error" });
    }
  }

  if (status === "success") {
    return (
      <div
        role="status"
        className="rounded-[calc(var(--sn-radius)+6px)] border border-emerald-300 bg-emerald-50 p-6 text-emerald-950 shadow-[var(--sn-elev-1)]"
      >
        <h3 className="text-xl font-semibold">{t(locale, "lead.title")}</h3>
        <p className="mt-2 text-sm">{message}</p>
      </div>
    );
  }

  return (
    <form
      id="lead-form"
      onSubmit={onSubmit}
      onFocus={onStart}
      className="sn-card p-6"
    >
      <h2 className="text-2xl font-bold tracking-tight text-[var(--sn-text)]">{t(locale, "lead.title")}</h2>
      <p className="mt-2 text-sm text-[var(--sn-muted)]">
        {t(locale, "lead.intro")} <span className="font-medium">{industryName}</span>
      </p>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "lead.name")}
          <input
            name="name"
            required
            maxLength={100}
            autoComplete="name"
            className="sn-input"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "lead.email")}
          <input
            name="email"
            type="email"
            required
            maxLength={200}
            autoComplete="email"
            className="sn-input"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "lead.phone")} {logistics ? null : <span className="font-normal text-[var(--sn-muted)]">({t(locale, "common.optional")})</span>}
          <input
            name="phone"
            type="tel"
            required={logistics}
            maxLength={40}
            autoComplete="tel"
            className="sn-input"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "lead.company")} {logistics ? null : <span className="font-normal text-[var(--sn-muted)]">({t(locale, "common.optional")})</span>}
          <input
            name="company"
            required={logistics}
            maxLength={120}
            autoComplete="organization"
            className="sn-input"
          />
        </label>
      </div>
      <label className="mt-4 flex flex-col gap-1 text-sm font-medium">
        {t(locale, "lead.message")}
        <textarea
          name="message"
          rows={4}
          maxLength={2000}
          className="sn-input"
        />
      </label>
      <div aria-hidden="true" className="hidden">
        <label>
          {t(locale, "lead.honeypot")}
          <input name="website" tabIndex={-1} autoComplete="off" />
        </label>
      </div>
      <label className="mt-4 flex items-start gap-3 text-sm">
        <input type="checkbox" name="consent" required className="mt-1 h-4 w-4" />
        <span>
          {t(locale, "lead.consent")}{" "}
          <a
            href={`/${locale === "es" ? "es/" : ""}${industry}/privacy`}
            className="font-semibold underline"
          >
            {t(locale, "lead.consentLink")}
          </a>
        </span>
      </label>
      <p className="mt-3 text-xs text-[var(--sn-muted)]">{t(locale, "lead.privacyNote")}</p>
      <div aria-live="polite" className="mt-3 text-sm text-red-700">
        {message}
      </div>
      <button
        type="submit"
        disabled={status === "sending"}
        className="sn-btn mt-4"
      >
        {status === "sending" ? t(locale, "lead.sending") : t(locale, "lead.submit")}
      </button>
    </form>
  );
}
