import Link from "next/link";
import { headers } from "next/headers";

import { t } from "@/lib/i18n";
import { requestSite } from "@/lib/url";

export default async function NotFound() {
  const requestHeaders = await headers();
  const locale = requestHeaders.get("x-sn-locale") === "es" ? "es" : "en";
  const { channel } = await requestSite();
  const industry = channel ?? process.env.SN_DEFAULT_INDUSTRY ?? "legal";
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-4 px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--sn-muted)]">
        404
      </p>
      <h1 className="text-3xl font-semibold">{t(locale, "states.notFoundTitle")}</h1>
      <p className="text-sm text-[var(--sn-muted)]">{t(locale, "states.notFoundBody")}</p>
      <Link
        href={`${locale === "es" ? "/es" : ""}${channel ? "" : `/${industry}`}`}
        className="w-fit rounded-full bg-[var(--sn-primary)] px-5 py-2.5 text-sm font-semibold text-white"
      >
        {t(locale, "nav.home")}
      </Link>
    </main>
  );
}
