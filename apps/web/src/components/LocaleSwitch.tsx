"use client";

import { usePathname } from "next/navigation";

import { t, type Locale } from "@/lib/i18n";

export function LocaleSwitch({ locale }: { locale: Locale }) {
  const pathname = usePathname() || "/";
  const target =
    locale === "en"
      ? `/es${pathname === "/" ? "" : pathname}`
      : pathname === "/es"
        ? "/"
        : pathname.replace(/^\/es/, "") || "/";

  const switchTo = (next: Locale) => {
    document.cookie = `sn_locale=${next}; path=/; max-age=31536000; samesite=lax`;
    window.location.assign(next === locale ? pathname : target);
  };

  return (
    <div className="flex items-center gap-1 rounded-full border border-[var(--sn-border)] p-1 text-xs">
      <span className="sr-only">{t(locale, "localeSwitch.label")}</span>
      {(["en", "es"] as const).map((option) => (
        <a
          key={option}
          href={option === locale ? pathname : target}
          onClick={() => switchTo(option)}
          aria-current={locale === option ? "true" : undefined}
          className={`rounded-full px-3 py-1 font-semibold transition ${
            locale === option
              ? "bg-[var(--sn-primary)] text-white"
              : "text-[var(--sn-muted)] hover:text-[var(--sn-text)]"
          }`}
        >
          {t(locale, `localeSwitch.${option}`)}
        </a>
      ))}
    </div>
  );
}
