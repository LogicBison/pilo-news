"use client";

import { useState } from "react";

import { sessionHash, track } from "@/lib/analytics";
import { t, type Locale } from "@/lib/i18n";
import { captureUtm } from "@/lib/utm";

import { Button } from "./ui/button";
import { ConsentField } from "./ui/consent-field";
import { FieldError } from "./ui/field-error";
import { TextArea } from "./ui/text-area";
import { TextField } from "./ui/text-field";

/**
 * Article-level rung: "ask one question". Lower friction than a consultation —
 * a written answer is a lead with a stated need, and it does not ask for a call.
 */
export function AskQuestion({
  industry,
  locale,
  articleId,
  sourcePage,
}: {
  industry: string;
  locale: Locale;
  articleId?: string;
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
          kind: "question",
          name: data.get("name"),
          email: data.get("email"),
          message: data.get("question"),
          locale,
          consent: data.get("consent") === "on",
          source_page: sourcePage,
          article_id: articleId ?? null,
          utm: captureUtm(),
          session_hash: sessionHash(),
        }),
      });
      if (response.status === 429) {
        setStatus("error");
        setMessage(t(locale, "question.rateLimited"));
        return;
      }
      if (!response.ok) {
        setStatus("error");
        setMessage(t(locale, "question.error"));
        return;
      }
      setStatus("sent");
      setMessage(t(locale, "question.success"));
      track("question_submit", { industry, locale, placement: "article-question", articleId, result: "ok" });
      form.reset();
    } catch {
      setStatus("error");
      setMessage(t(locale, "question.error"));
    }
  }

  return (
    <section id="ask-question" aria-labelledby="ask-question-heading" className="sn-card mt-8 p-6">
      <div className="flex items-center gap-2">
        <span className="sn-kicker" aria-hidden="true" />
        <p className="sn-eyebrow">{t(locale, "question.eyebrow")}</p>
      </div>
      <h2 id="ask-question-heading" className="sn-section-title mt-2 font-bold text-[var(--sn-text)]">
        {t(locale, "question.title")}
      </h2>
      <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(locale, "question.body")}</p>
      <form onSubmit={onSubmit} className="mt-4 grid gap-3">
        <div className="grid gap-3 sm:grid-cols-2">
          <TextField label={t(locale, "question.name")} name="name" required maxLength={100} autoComplete="name" />
          <TextField
            label={t(locale, "question.email")}
            name="email"
            type="email"
            required
            maxLength={200}
            autoComplete="email"
          />
        </div>
        <TextArea
          label={t(locale, "question.label")}
          name="question"
          required
          minLength={10}
          maxLength={600}
          rows={3}
          hint={t(locale, "question.hint")}
        />
        <ConsentField name="consent" className="text-xs leading-relaxed text-[var(--sn-muted)]">
          {t(locale, "question.consent")}
        </ConsentField>
        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={status === "sending"}>
            {status === "sending" ? t(locale, "question.sending") : t(locale, "question.submit")}
          </Button>
          <p className="text-xs text-[var(--sn-muted)]">{t(locale, "question.note")}</p>
        </div>
        <FieldError message={message} />
      </form>
    </section>
  );
}
