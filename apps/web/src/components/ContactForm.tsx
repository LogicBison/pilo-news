"use client";

import { useState } from "react";

import { t, type Locale } from "@/lib/i18n";

import { Button } from "./ui/button";
import { FieldError } from "./ui/field-error";
import { TextArea } from "./ui/text-area";
import { TextField } from "./ui/text-field";

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
      <div
        role="status"
        className="rounded-[var(--sn-radius)] border border-[var(--sn-border)] bg-[var(--sn-surface)] p-6 text-[var(--sn-text)] shadow-[var(--sn-elev-1)]"
      >
        <p className="text-sm">{message}</p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="sn-card p-6">
      <h2 className="text-xl font-semibold text-[var(--sn-text)]">{t(locale, "contact.formTitle")}</h2>
      <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(locale, "contact.formIntro")}</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <TextField
          label={t(locale, "contact.name")}
          name="name"
          required
          maxLength={100}
          autoComplete="name"
          labelWeight="medium"
        />
        <TextField
          label={t(locale, "contact.email")}
          name="email"
          type="email"
          required
          maxLength={200}
          autoComplete="email"
          labelWeight="medium"
        />
        <TextField
          label={t(locale, "contact.phone")}
          name="phone"
          type="tel"
          maxLength={40}
          autoComplete="tel"
          labelWeight="medium"
          wrapperClassName="sm:col-span-2"
          optionalLabel={t(locale, "common.optional")}
        />
      </div>
      <TextArea
        label={t(locale, "contact.message")}
        name="message"
        required
        minLength={10}
        maxLength={2000}
        rows={5}
        wrapperClassName="mt-4"
        labelWeight="medium"
      />
      <div aria-hidden="true" className="hidden">
        <label>
          {t(locale, "contact.honeypot")}
          <input name="website" tabIndex={-1} autoComplete="off" />
        </label>
      </div>
      <FieldError message={message} />
      <Button type="submit" disabled={status === "sending"} className="mt-4">
        {status === "sending" ? t(locale, "contact.sending") : t(locale, "contact.submit")}
      </Button>
    </form>
  );
}
