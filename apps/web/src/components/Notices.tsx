import Link from "next/link";

import { t, type Locale } from "@/lib/i18n";

export function DegradedNotice({ locale, retryHref }: { locale: Locale; retryHref: string }) {
  return (
    <div
      role="alert"
      className="rounded-[var(--sn-radius)] border border-amber-300 bg-amber-50 p-5 text-amber-950"
    >
      <p className="text-sm font-semibold uppercase tracking-[0.14em]">{t(locale, "states.degraded")}</p>
      <p className="mt-2 text-sm">{t(locale, "states.degradedBody")}</p>
      <Link
        href={retryHref}
        className="mt-3 inline-block rounded-full bg-amber-900 px-4 py-2 text-sm font-semibold text-white"
      >
        {t(locale, "states.retry")}
      </Link>
    </div>
  );
}

export function EmptyState({
  locale,
  title,
  body,
}: {
  locale: Locale;
  title?: string;
  body?: string;
}) {
  return (
    <div className="rounded-[var(--sn-radius)] border border-dashed border-[var(--sn-border)] p-8 text-center">
      <h2 className="text-xl font-semibold text-[var(--sn-text)]">{title ?? t(locale, "states.empty")}</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm text-[var(--sn-muted)]">
        {body ?? t(locale, "states.emptyBody")}
      </p>
    </div>
  );
}

export function FallbackNotice({ locale, href }: { locale: Locale; href: string }) {
  if (locale !== "es") return null;
  return (
    <div className="rounded-[var(--sn-radius)] border border-blue-300 bg-blue-50 p-4 text-sm text-blue-950">
      <p>{t(locale, "fallback.notice")}</p>
      <Link href={href} className="mt-1 inline-block font-semibold underline">
        {t(locale, "fallback.link")}
      </Link>
    </div>
  );
}
