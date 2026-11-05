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
      className={`sn-btn ${className}`}
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
      className="fixed inset-x-0 bottom-0 z-40 hidden border-t border-[var(--sn-border)] bg-[var(--sn-bg)]/95 p-3 shadow-[var(--sn-elev-3)] backdrop-blur md:hidden"
    >
      <div className="mx-auto flex max-w-3xl items-center gap-3">
        <a
          href="#lead-form"
          onClick={() => track("cta_click", { industry, locale, placement: "sticky", articleId })}
          className="sn-btn flex-1"
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
          className="sn-btn sn-btn-ghost px-3 py-2"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
