"use client";

import { useEffect, useRef, useState } from "react";

import { sessionHash, track } from "@/lib/analytics";
import { t, type Locale } from "@/lib/i18n";
import { captureUtm } from "@/lib/utm";

type Status = "idle" | "sending" | "success" | "error" | "rate-limited";
type FieldErrors = { name?: string; email?: string; message?: string };

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Apex service inquiry. Posts to the contact endpoint with no industry: the
 * inquiry belongs to the network, not to a desk, so it lands in the operator's
 * contact tab with `source_page` saying which lobby page asked.
 */
export function ServiceForm({
  locale,
  sourcePage,
  privacyHref,
  submitLabel,
  placement = "lobby-services",
}: {
  locale: Locale;
  sourcePage: string;
  privacyHref: string;
  /** Defaults to the scope-call label; the contact section passes its own. */
  submitLabel?: string;
  placement?: string;
}) {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<FieldErrors>({});
  const formRef = useRef<HTMLFormElement>(null);
  const successRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (status === "success") successRef.current?.focus();
  }, [status]);

  function read(form: HTMLFormElement) {
    const data = new FormData(form);
    return {
      name: String(data.get("name") ?? "").trim(),
      email: String(data.get("email") ?? "").trim(),
      phone: String(data.get("phone") ?? "").trim(),
      message: String(data.get("message") ?? "").trim(),
      consent: data.get("consent") === "on",
    };
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (status === "sending") return;
    const form = event.currentTarget;
    const values = read(form);
    const next: FieldErrors = {};
    if (!values.name) next.name = t(locale, "lobby.form.name") + "?";
    if (!values.email || !EMAIL_PATTERN.test(values.email)) {
      next.email = t(locale, "lobby.form.error");
    }
    if (values.message.length < 10) next.message = t(locale, "lobby.form.error");
    setErrors(next);
    if (Object.keys(next).length > 0) {
      setStatus("idle");
      return;
    }

    setStatus("sending");
    track("lead_form_start", { surface: "lobby", locale, placement });
    try {
      const response = await fetch("/api/proxy/v1/contact", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          name: values.name,
          email: values.email,
          phone: values.phone || null,
          message: values.message,
          locale,
          website: new FormData(form).get("website") || null,
          source_page: sourcePage,
          utm: captureUtm(),
          session_hash: sessionHash(),
        }),
      });
      if (response.status === 429) {
        setStatus("rate-limited");
        setMessage(t(locale, "lobby.form.limited"));
        return;
      }
      if (!response.ok) {
        setStatus("error");
        setMessage(t(locale, "lobby.form.error"));
        return;
      }
      setStatus("success");
      setMessage(t(locale, "lobby.form.success"));
      track("lead_submit", { surface: "lobby", locale, placement });
      form.reset();
    } catch {
      setStatus("error");
      setMessage(t(locale, "lobby.form.error"));
    }
  }

  if (status === "success") {
    return (
      <div ref={successRef} role="status" tabIndex={-1} className="lb-status lb-status-ok">
        {message}
      </div>
    );
  }

  return (
    <form ref={formRef} className="lb-form" onSubmit={onSubmit} noValidate>
      <div className="lb-field">
        <label htmlFor="lb-name">{t(locale, "lobby.form.name")}</label>
        <input
          id="lb-name"
          name="name"
          type="text"
          autoComplete="name"
          required
          aria-invalid={Boolean(errors.name)}
        />
        {errors.name ? <p className="lb-field-error">{errors.name}</p> : null}
      </div>
      <div className="lb-field">
        <label htmlFor="lb-email">{t(locale, "lobby.form.email")}</label>
        <input
          id="lb-email"
          name="email"
          type="email"
          autoComplete="email"
          inputMode="email"
          required
          aria-invalid={Boolean(errors.email)}
        />
        {errors.email ? <p className="lb-field-error">{errors.email}</p> : null}
      </div>
      <div className="lb-field">
        <label htmlFor="lb-phone">{t(locale, "lobby.form.phone")}</label>
        <input id="lb-phone" name="phone" type="tel" autoComplete="tel" />
      </div>
      <div className="lb-field">
        <label htmlFor="lb-message">{t(locale, "lobby.form.message")}</label>
        <textarea
          id="lb-message"
          name="message"
          required
          minLength={10}
          maxLength={2000}
          aria-invalid={Boolean(errors.message)}
          aria-describedby="lb-message-hint"
        />
        <p className="lb-field-hint" id="lb-message-hint">
          {t(locale, "lobby.form.messageHint")}
        </p>
        {errors.message ? <p className="lb-field-error">{errors.message}</p> : null}
      </div>
      <div className="lb-check">
        <input id="lb-consent" name="consent" type="checkbox" required />
        <label htmlFor="lb-consent">
          {t(locale, "lobby.form.consent")}{" "}
          <a href={privacyHref}>{t(locale, "lobby.form.consentLink")}</a>
        </label>
      </div>
      <div className="lb-honeypot" aria-hidden="true">
        <label htmlFor="lb-website">Website</label>
        <input id="lb-website" name="website" type="text" tabIndex={-1} autoComplete="off" />
      </div>
      {status === "error" || status === "rate-limited" ? (
        <p className="lb-status lb-status-error" role="alert">
          {message}
        </p>
      ) : null}
      <button type="submit" className="lb-btn" disabled={status === "sending"}>
        {status === "sending"
          ? t(locale, "lobby.form.sending")
          : (submitLabel ?? t(locale, "lobby.form.submit"))}
      </button>
    </form>
  );
}
