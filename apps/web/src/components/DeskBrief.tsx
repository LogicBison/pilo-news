import { t, type Locale } from "@/lib/i18n";

export function DeskBrief({
  brief,
  locale,
  fallbackNote,
}: {
  brief: string | null;
  locale: Locale;
  fallbackNote?: string;
}) {
  return (
    <section
      aria-labelledby="desk-brief-heading"
      className="rounded-[var(--sn-radius)] border-l-4 border-[var(--sn-accent)] bg-[var(--sn-surface)] p-5"
    >
      <h2
        id="desk-brief-heading"
        className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--sn-muted)]"
      >
        {t(locale, "home.deskBrief")}
      </h2>
      {brief ? (
        <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-[var(--sn-text)]">{brief}</p>
      ) : (
        <p className="mt-2 text-sm text-[var(--sn-muted)]">
          {fallbackNote ?? t(locale, "home.aiUnavailable")}
        </p>
      )}
    </section>
  );
}
