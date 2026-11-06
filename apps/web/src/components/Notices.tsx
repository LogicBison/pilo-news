import Link from "next/link";

import { t, type Locale } from "@/lib/i18n";

import { Card } from "./ui/card";

export function DegradedNotice({ locale, retryHref }: { locale: Locale; retryHref: string }) {
  return (
    <div
      role="alert"
      className="rounded-[var(--sn-radius)] border border-[var(--sn-border)] border-l-4 border-l-[var(--sn-accent)] bg-[var(--sn-surface)] p-5 text-[var(--sn-text)] shadow-[var(--sn-elev-1)]"
    >
      <p className="text-sm font-semibold uppercase tracking-[0.14em]">{t(locale, "states.degraded")}</p>
      <p className="mt-2 text-sm">{t(locale, "states.degradedBody")}</p>
      <Link href={retryHref} className="sn-btn mt-3 inline-block">
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
    <Card className="border-dashed p-10 text-center">
      <h2 className="text-xl font-semibold text-[var(--sn-text)]">{title ?? t(locale, "states.empty")}</h2>
      <p className="mx-auto mt-2 max-w-lg text-sm text-[var(--sn-muted)]">
        {body ?? t(locale, "states.emptyBody")}
      </p>
    </Card>
  );
}

export function FallbackNotice({ locale, href }: { locale: Locale; href: string }) {
  if (locale !== "es") return null;
  return (
    <div className="rounded-[var(--sn-radius)] border border-[var(--sn-border)] bg-[var(--sn-surface)] p-4 text-sm text-[var(--sn-text)] shadow-[var(--sn-elev-1)]">
      <p>{t(locale, "fallback.notice")}</p>
      <Link href={href} className="mt-1 inline-block font-semibold underline">
        {t(locale, "fallback.link")}
      </Link>
    </div>
  );
}
