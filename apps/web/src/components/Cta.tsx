"use client";

import { useEffect, useRef } from "react";

import { track } from "@/lib/analytics";
import { t, type Locale } from "@/lib/i18n";

export function CtaButton({
  industry,
  locale,
  placement,
  articleId,
  label,
  className = "",
}: {
  industry: string;
  locale: Locale;
  placement: string;
  articleId?: string;
  label: string;
  className?: string;
}) {
  const reported = useRef(false);

  useEffect(() => {
    if (reported.current) return;
    reported.current = true;
    track("cta_impression", { industry, locale, placement, articleId });
  }, [articleId, industry, locale, placement]);

  return (
    <a
      href="#lead-form"
      onClick={() => track("cta_click", { industry, locale, placement, articleId })}
      className={`inline-flex items-center justify-center rounded-full bg-[var(--sn-primary)] px-5 py-3 text-sm font-semibold text-white transition hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--sn-accent)] ${className}`}
    >
      {label}
    </a>
  );
}

export function StickyCta({
  industry,
  locale,
  articleId,
}: {
  industry: string;
  locale: Locale;
  articleId?: string;
}) {
  useEffect(() => {
    const bar = document.getElementById("sn-sticky-cta");
    if (!bar) return;
    let shown = false;
    const onScroll = () => {
      const height = document.documentElement.scrollHeight - window.innerHeight;
      if (height <= 0) return;
      const ratio = window.scrollY / height;
      if (ratio > 0.6 && !shown && !sessionStorage.getItem("sn-sticky-dismissed")) {
        shown = true;
        bar.classList.remove("hidden");
        track("cta_impression", { industry, locale, placement: "sticky" });
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [articleId, industry, locale]);

  return (
    <div
      id="sn-sticky-cta"
      className="fixed inset-x-0 bottom-0 z-40 hidden border-t border-[var(--sn-border)] bg-[var(--sn-bg)] p-3 shadow-lg md:hidden"
    >
      <div className="mx-auto flex max-w-3xl items-center gap-3">
        <a
          href="#lead-form"
          onClick={() => track("cta_click", { industry, locale, placement: "sticky", articleId })}
          className="flex-1 rounded-full bg-[var(--sn-primary)] px-4 py-2.5 text-center text-sm font-semibold text-white"
        >
          {t(locale, "cta.sticky")}
        </a>
        <button
          type="button"
          aria-label={t(locale, "cta.dismiss")}
          onClick={() => {
            sessionStorage.setItem("sn-sticky-dismissed", "1");
            document.getElementById("sn-sticky-cta")?.classList.add("hidden");
          }}
          className="rounded-full border border-[var(--sn-border)] px-3 py-2 text-sm"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
