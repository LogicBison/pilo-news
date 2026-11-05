"use client";

import { useState } from "react";

import { t, type Locale } from "@/lib/i18n";

export function ContactForm({ industry, locale }: { industry: string; locale: Locale }) {
  const [status, setStatus] = useState<"idle" | "sending" | "success" | "error" | "rate-limited">(
    "idle",
  );
  const [message, setMessage] = useState("");

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setStatus("sending");
    setMessage("");
    try {
      const response = await fetch("/api/proxy/v1/contact", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          name: data.get("name"),
          email: data.get("email"),
          phone: data.get("phone") || null,
          message: data.get("message"),
          locale,
          industry,
          website: data.get("website") || null,
        }),
      });
      if (response.status === 429) {
        setStatus("rate-limited");
        setMessage(t(locale, "contact.rateLimited"));
        return;
      }
      if (!response.ok) {
        setStatus("error");
        setMessage(t(locale, "contact.failure"));
        return;
      }
      setStatus("success");
      setMessage(t(locale, "contact.success"));
      form.reset();
    } catch {
      setStatus("error");
      setMessage(t(locale, "contact.failure"));
    }
  }

  if (status === "success") {
    return (
      <div role="status" className="rounded-[calc(var(--sn-radius)+6px)] border border-emerald-300 bg-emerald-50 p-6 text-emerald-950 shadow-[var(--sn-elev-1)]">
        <p className="text-sm">{message}</p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="sn-card p-6">
      <h2 className="text-xl font-semibold text-[var(--sn-text)]">{t(locale, "contact.formTitle")}</h2>
      <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(locale, "contact.formIntro")}</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "contact.name")}
          <input name="name" required maxLength={100} autoComplete="name" className="sn-input" />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium">
          {t(locale, "contact.email")}
          <input name="email" type="email" required maxLength={200} autoComplete="email" className="sn-input" />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium sm:col-span-2">
          {t(locale, "contact.phone")} <span className="font-normal text-[var(--sn-muted)]">({t(locale, "common.optional")})</span>
          <input name="phone" type="tel" maxLength={40} autoComplete="tel" className="sn-input" />
        </label>
      </div>
      <label className="mt-4 flex flex-col gap-1 text-sm font-medium">
        {t(locale, "contact.message")}
        <textarea name="message" required minLength={10} maxLength={2000} rows={5} className="sn-input" />
      </label>
      <div aria-hidden="true" className="hidden">
        <label>
          {t(locale, "contact.honeypot")}
          <input name="website" tabIndex={-1} autoComplete="off" />
        </label>
      </div>
      <div aria-live="polite" className="mt-3 text-sm text-red-700">
        {message}
      </div>
      <button
        type="submit"
        disabled={status === "sending"}
        className="sn-btn mt-4"
      >
        {status === "sending" ? t(locale, "contact.sending") : t(locale, "contact.submit")}
      </button>
    </form>
  );
}
