import { localePath, t, type Locale } from "@/lib/i18n";
import { channelBase } from "@/lib/url";

export async function SearchBox({
  industry,
  locale,
  initialQuery = "",
}: {
  industry: string;
  locale: Locale;
  initialQuery?: string;
}) {
  const base = await channelBase(industry);
  return (
    <form
      action={localePath(locale, `${base}/search`)}
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
          className="sn-input rounded-full px-5 py-3"
        />
      </label>
      <button
        type="submit"
        className="sn-btn"
      >
        {t(locale, "search.submit")}
      </button>
    </form>
  );
}
