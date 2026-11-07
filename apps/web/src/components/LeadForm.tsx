"use client";

import { useState } from "react";

import { sessionHash, track } from "@/lib/analytics";
import type { CtaQualification } from "@/lib/api";
import { t, type Locale } from "@/lib/i18n";
import { captureUtm } from "@/lib/utm";
import { localized } from "@/lib/theme";

import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Chip } from "./ui/chip";
import { ConsentField } from "./ui/consent-field";
import { FieldError } from "./ui/field-error";
import { SelectField } from "./ui/select-field";
import { TextArea } from "./ui/text-area";
import { TextField } from "./ui/text-field";
import { TrustLine } from "./ui/trust-line";

interface LeadFormProps {
  industry: string;
  industryName: string;
  /** `""` on a channel subdomain, `"/stem-cell"` on a shared host. */
  base?: string;
  locale: Locale;
  kind: "consultation" | "brief";
  placement: string;
  articleId?: string;
  sourcePage: string;
  qualify?: CtaQualification;
}

type Status = "idle" | "sending" | "success" | "error" | "rate-limited";

export function LeadForm({
  industry,
  industryName,
  base = "",
  locale,
  kind,
  placement,
  articleId,
  sourcePage,
  qualify,
}: LeadFormProps) {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [started, setStarted] = useState(false);
  const logistics = industry === "logistics";
  const options = (qualify?.options ?? []).filter((option) => option.value && option.label);

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
          qualification: data.get("qualification") || null,
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
      <Card role="status" className="p-6">
        <Chip>{t(locale, "lead.received")}</Chip>
        <h3 className="sn-section-title mt-3 font-semibold text-[var(--sn-text)]">
          {t(locale, "lead.title")}
        </h3>
        <p className="mt-2 text-sm text-[var(--sn-muted)]">{message}</p>
        <p className="mt-4 border-t border-[var(--sn-border)] pt-4 text-sm text-[var(--sn-text)]">
          {t(locale, "lead.successNext")}
        </p>
        <a href="#brief-signup" className="sn-btn sn-btn-ghost mt-4">
          {t(locale, "brief.submit")}
        </a>
      </Card>
    );
  }

  return (
    <form id="lead-form" onSubmit={onSubmit} onFocus={onStart} className="sn-card p-6">
      <div className="flex items-center gap-2">
        <span className="sn-kicker" aria-hidden="true" />
        <p className="sn-eyebrow">{t(locale, "lead.eyebrow")}</p>
      </div>
      <h2 className="sn-section-title mt-2 font-bold text-[var(--sn-text)]">{t(locale, "lead.title")}</h2>
      <p className="mt-2 text-sm text-[var(--sn-muted)]">
        {t(locale, "lead.intro")} <span className="font-medium">{industryName}</span>
      </p>
      <p className="sn-required-note mt-2">{t(locale, "common.requiredNote")}</p>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <TextField
          label={t(locale, "lead.name")}
          name="name"
          required
          maxLength={100}
          autoComplete="name"
        />
        <TextField
          label={t(locale, "lead.email")}
          name="email"
          type="email"
          required
          maxLength={200}
          autoComplete="email"
        />
      </div>

      {options.length > 0 ? (
        <SelectField
          label={localized(qualify?.label, locale) || t(locale, "lead.message")}
          name="qualification"
          required={qualify?.required !== false}
          defaultValue=""
          wrapperClassName="mt-3"
        >
          <option value="" disabled>
            {t(locale, "lead.chooseOption")}
          </option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {localized(option.label, locale)}
            </option>
          ))}
        </SelectField>
      ) : null}

      {logistics ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <TextField
            label={t(locale, "lead.phone")}
            name="phone"
            type="tel"
            required
            maxLength={40}
            autoComplete="tel"
          />
          <TextField
            label={t(locale, "lead.company")}
            name="company"
            required
            maxLength={120}
            autoComplete="organization"
          />
        </div>
      ) : (
        <details className="sn-more">
          <summary>{t(locale, "lead.optionalDetails")}</summary>
          <div className="sn-more-body grid gap-3 sm:grid-cols-2">
            <TextField
              label={t(locale, "lead.phone")}
              name="phone"
              type="tel"
              maxLength={40}
              autoComplete="tel"
              labelWeight="medium"
              optionalLabel={t(locale, "common.optional")}
            />
            <TextField
              label={t(locale, "lead.company")}
              name="company"
              maxLength={120}
              autoComplete="organization"
              labelWeight="medium"
              optionalLabel={t(locale, "common.optional")}
            />
          </div>
        </details>
      )}

      <TextArea
        label={t(locale, "lead.details")}
        name="message"
        rows={3}
        maxLength={2000}
        wrapperClassName="mt-3"
        optionalLabel={t(locale, "common.optional")}
      />

      <div aria-hidden="true" className="hidden">
        <label>
          {t(locale, "lead.honeypot")}
          <input name="website" tabIndex={-1} autoComplete="off" />
        </label>
      </div>

      <ConsentField name="consent" className="mt-4">
        {t(locale, "lead.consent")}{" "}
        <a
          href={`${locale === "es" ? "/es" : ""}${base}/privacy`}
          className="font-semibold underline"
        >
          {t(locale, "lead.consentLink")}
        </a>
      </ConsentField>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <Button type="submit" disabled={status === "sending"}>
          {status === "sending" ? t(locale, "lead.sending") : t(locale, "lead.submit")}
        </Button>
        <Chip>{t(locale, "lead.responseTime")}</Chip>
      </div>
      <TrustLine className="mt-3">{t(locale, "lead.privacyNote")}</TrustLine>
      <FieldError message={message} />
    </form>
  );
}
