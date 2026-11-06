"use client";

import { useState } from "react";

import { track } from "@/lib/analytics";
import { t, type Locale } from "@/lib/i18n";
import { captureUtm } from "@/lib/utm";

import { Button } from "./ui/button";
import { ConsentField } from "./ui/consent-field";
import { FieldError } from "./ui/field-error";
import { TextField } from "./ui/text-field";

/**
 * Gated reference asset (S3). The reader joins a list for a dated document, not
 * a vague newsletter. No delivery promise beyond "we send it when it publishes".
 */
export function AssetOffer({
  industry,
  locale,
  asset,
  title,
  body,
  sourcePage,
}: {
  industry: string;
  locale: Locale;
  asset: string;
  title: string;
  body: string;
  sourcePage: string;
}) {
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [message, setMessage] = useState("");

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
          kind: "asset",
          asset,
          name: data.get("name"),
          email: data.get("email"),
          locale,
          consent: data.get("consent") === "on",
          source_page: sourcePage,
          utm: captureUtm(),
        }),
      });
      if (response.status === 429) {
        setStatus("error");
        setMessage(t(locale, "asset.rateLimited"));
        return;
      }
      if (!response.ok) {
        setStatus("error");
        setMessage(t(locale, "asset.error"));
        return;
      }
      setStatus("sent");
      setMessage(t(locale, "asset.success"));
      track("asset_interest", { industry, locale, placement: asset, result: "ok" });
      form.reset();
    } catch {
      setStatus("error");
      setMessage(t(locale, "asset.error"));
    }
  }

  return (
    <section aria-labelledby="asset-heading" className="sn-card mt-8 p-6">
      <div className="flex items-center gap-2">
        <span className="sn-kicker" aria-hidden="true" />
        <p className="sn-eyebrow">{t(locale, "asset.eyebrow")}</p>
      </div>
      <h2 id="asset-heading" className="sn-section-title mt-2 font-bold text-[var(--sn-text)]">
        {title}
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-[var(--sn-muted)]">{body}</p>
      <form onSubmit={onSubmit} className="mt-4 grid gap-3 sm:grid-cols-2">
        <TextField label={t(locale, "asset.name")} name="name" required maxLength={100} autoComplete="name" />
        <TextField
          label={t(locale, "asset.email")}
          name="email"
          type="email"
          required
          maxLength={200}
          autoComplete="email"
        />
        <div className="sm:col-span-2">
          <ConsentField name="consent" className="text-xs leading-relaxed text-[var(--sn-muted)]">
            {t(locale, "asset.consent")}
          </ConsentField>
        </div>
        <div className="flex flex-wrap items-center gap-3 sm:col-span-2">
          <Button type="submit" disabled={status === "sending"}>
            {status === "sending" ? t(locale, "asset.sending") : t(locale, "asset.submit")}
          </Button>
          <p className="text-xs text-[var(--sn-muted)]">{t(locale, "asset.note")}</p>
        </div>
        <div className="sm:col-span-2">
          <FieldError message={message} />
        </div>
      </form>
    </section>
  );
}
