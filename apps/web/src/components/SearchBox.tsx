import { localePath, t, type Locale } from "@/lib/i18n";

export function SearchBox({
  industry,
  locale,
  initialQuery = "",
}: {
  industry: string;
  locale: Locale;
  initialQuery?: string;
}) {
  return (
    <form
      action={localePath(locale, `/${industry}/search`)}
      method="get"
      role="search"
      className="flex flex-col gap-3 sm:flex-row"
    >
      <label className="flex-1">
        <span className="sr-only">{t(locale, "search.queryLabel")}</span>
        <input
          type="search"
          name="q"
          defaultValue={initialQuery}
          minLength={3}
          maxLength={64}
          placeholder={t(locale, "search.placeholder")}
          className="w-full rounded-full border border-[var(--sn-border)] bg-[var(--sn-bg)] px-5 py-3 text-sm text-[var(--sn-text)]"
        />
      </label>
      <button
        type="submit"
        className="rounded-full bg-[var(--sn-primary)] px-6 py-3 text-sm font-semibold text-white"
      >
        {t(locale, "search.submit")}
      </button>
    </form>
  );
}
