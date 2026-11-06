"use client";

import { useEffect, useRef, useState } from "react";

import { t, type Locale } from "@/lib/i18n";
import { captureUtm } from "@/lib/utm";

import { Button } from "./ui/button";
import { FieldError } from "./ui/field-error";
import { TextArea } from "./ui/text-area";
import { TextField } from "./ui/text-field";

type Status = "idle" | "sending" | "success" | "error" | "rate-limited";
type FieldErrors = { name?: string; email?: string; phone?: string; message?: string };
type Values = { name: string; email: string; phone: string; message: string };

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function read(form: HTMLFormElement): Values {
  const data = new FormData(form);
  return {
    name: String(data.get("name") ?? "").trim(),
    email: String(data.get("email") ?? "").trim(),
    phone: String(data.get("phone") ?? "").trim(),
    message: String(data.get("message") ?? "").trim(),
  };
}

/**
 * Desk contact form. Client validation only — the API returns one problem
 * `detail` and no field list, so the form owns per-field errors and the
 * server owns the final say.
 */
export function ContactForm({
  industry,
  locale,
  email,
}: {
  industry: string;
  locale: Locale;
  email?: string;
}) {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<FieldErrors>({});
  const formRef = useRef<HTMLFormElement>(null);
  const successRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (status === "success") successRef.current?.focus();
  }, [status]);

  function validate(values: Values): FieldErrors {
    const next: FieldErrors = {};
    if (!values.name) next.name = t(locale, "contact.errName");
    if (!values.email) next.email = t(locale, "contact.errEmail");
    else if (!EMAIL_PATTERN.test(values.email)) next.email = t(locale, "contact.errEmail");
    if (values.message.length < 10) next.message = t(locale, "contact.errMessage");
    return next;
  }

  function focusFirst(next: FieldErrors) {
    const order: (keyof FieldErrors)[] = ["name", "email", "message"];
    const field = order.find((key) => next[key]);
    if (!field) return;
    formRef.current?.querySelector<HTMLElement>(`[name="${field}"]`)?.focus();
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (status === "sending") return;
    const form = event.currentTarget;
    const values = read(form);
    const next = validate(values);
    setErrors(next);
    if (Object.keys(next).length > 0) {
      setStatus("idle");
      setMessage("");
      focusFirst(next);
      return;
    }

    setStatus("sending");
    setMessage("");
    try {
      const response = await fetch("/api/proxy/v1/contact", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          ...values,
          phone: values.phone || null,
          locale,
          industry,
          website: new FormData(form).get("website") || null,
          utm: captureUtm(),
        }),
      });
      if (response.status === 429) {
        setStatus("rate-limited");
        setMessage(t(locale, "contact.rateLimited"));
        return;
      }
      if (!response.ok) {
        const problem = (await response.json().catch(() => null)) as { detail?: string } | null;
        setStatus("error");
        setMessage(
          response.status === 400 && problem?.detail
            ? problem.detail
            : t(locale, "contact.failure"),
        );
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

  function sendAnother() {
    setStatus("idle");
    setMessage("");
    setErrors({});
    requestAnimationFrame(() => {
      formRef.current?.querySelector<HTMLElement>('[name="name"]')?.focus();
    });
  }

  if (status === "success") {
    return (
      <div
        ref={successRef}
        role="status"
        tabIndex={-1}
        className="mt-6 border-t border-[var(--sn-border)] pt-6"
      >
        <h2 className="text-xl font-semibold text-[var(--sn-text)]">
          {t(locale, "contact.successTitle")}
        </h2>
        <p className="mt-2 max-w-[65ch] text-sm text-[var(--sn-muted)]">{message}</p>
        {email ? (
          <p className="mt-3 text-sm text-[var(--sn-muted)]">
            {t(locale, "contact.emailLabel")}:{" "}
            <a href={`mailto:${email}`} className="font-semibold underline">
              {email}
            </a>
          </p>
        ) : null}
        <Button variant="ghost" onClick={sendAnother} className="mt-4">
          {t(locale, "contact.sendAnother")}
        </Button>
      </div>
    );
  }

  return (
    <form
      ref={formRef}
      noValidate
      aria-busy={status === "sending"}
      onSubmit={onSubmit}
      className="mt-6 border-t border-[var(--sn-border)] pt-6"
    >
      <h2 className="text-xl font-semibold text-[var(--sn-text)]">{t(locale, "contact.formTitle")}</h2>
      <p className="mt-2 max-w-[65ch] text-sm text-[var(--sn-muted)]">
        {t(locale, "contact.formIntro")}
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <TextField
          label={t(locale, "contact.name")}
          name="name"
          required
          maxLength={100}
          autoComplete="name"
          labelWeight="medium"
          error={errors.name}
        />
        <TextField
          label={t(locale, "contact.email")}
          name="email"
          type="email"
          required
          maxLength={200}
          autoComplete="email"
          labelWeight="medium"
          error={errors.email}
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
          error={errors.phone}
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
        error={errors.message}
      />
      <div aria-hidden="true" className="hidden">
        <label>
          {t(locale, "contact.honeypot")}
          <input name="website" tabIndex={-1} autoComplete="off" />
        </label>
      </div>
      <p className="mt-3 text-xs text-[var(--sn-muted)]">{t(locale, "common.requiredNote")}</p>
      <FieldError message={message} />
      {message && email && status !== "sending" ? (
        <p className="mt-2 text-sm text-[var(--sn-muted)]">
          {t(locale, "contact.emailAlternative")}{" "}
          <a href={`mailto:${email}`} className="font-semibold underline">
            {email}
          </a>
        </p>
      ) : null}
      <Button type="submit" disabled={status === "sending"} className="mt-4">
        {status === "sending" ? t(locale, "contact.sending") : t(locale, "contact.submit")}
      </Button>
    </form>
  );
}
