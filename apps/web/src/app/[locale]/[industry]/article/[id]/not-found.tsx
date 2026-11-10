import Link from "next/link";
import { headers } from "next/headers";

import { t } from "@/lib/i18n";

/**
 * A missing story gets the story's own 404, not the site's: the reader is told
 * what actually happens to an article (the 30-day archive), which is the
 * retention the product really enforces.
 *
 * Home is the site root, not the article's channel: on a channel host that is
 * the channel front, on the apex it is the lobby, and both are correct without
 * knowing which desk the dead link belonged to. A channel-derived href left
 * the link empty on subdomains, which sent the reader back to the 404.
 */
export default async function ArticleNotFound() {
  const requestHeaders = await headers();
  const locale = requestHeaders.get("x-sn-locale") === "es" ? "es" : "en";
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-4 px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--sn-muted)]">
        404
      </p>
      <h1 className="text-3xl font-semibold">{t(locale, "article.notFound")}</h1>
      <p className="text-sm text-[var(--sn-muted)]">{t(locale, "article.notFoundBody")}</p>
      <Link
        href={locale === "es" ? "/es" : "/"}
        className="w-fit rounded-full bg-[var(--sn-primary)] px-5 py-2.5 text-sm font-semibold text-white"
        data-testid="article-404-home"
      >
        {t(locale, "nav.home")}
      </Link>
    </main>
  );
}
