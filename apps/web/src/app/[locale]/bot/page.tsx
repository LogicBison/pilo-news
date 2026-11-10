import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { isLocale, resolveLocale, t } from "@/lib/i18n";
import { deskViews } from "@/lib/lobby";
import { pageMetadata } from "@/lib/seo";
import { DESK_EMAIL, LobbyShell } from "@/components/lobby/shell";

export const dynamic = "force-dynamic";

type Params = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale } = await params;
  const resolved = resolveLocale(locale);
  return pageMetadata({
    title: t(resolved, "lobby.bot.title"),
    description: t(resolved, "lobby.bot.intro"),
    path: "/bot",
    locale: resolved,
    absoluteTitle: true,
  });
}

/**
 * The page the crawler's user agent advertises: identity, scope, pacing and
 * the way to opt out. Machine-facing, so it is deliberately not in the nav.
 */
export default async function BotPage({ params }: Params) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const resolved = resolveLocale(locale);
  const { desks } = await deskViews(resolved);
  const blocks = ["identity", "reading", "pacing", "block", "allowlist"] as const;

  return (
    <LobbyShell locale={resolved} path="/bot" desks={desks}>
      <article className="lb-section" style={{ paddingTop: "56px", maxWidth: "68ch" }}>
        <p className="lb-eyebrow">{t(resolved, "lobby.brand.name")}</p>
        <h1
          className="lb-h1"
          style={{ fontSize: "clamp(32px, 4vw, 46px)", maxWidth: "24ch" }}
        >
          {t(resolved, "lobby.bot.title")}
        </h1>
        <p className="lb-lead" style={{ marginTop: "24px" }}>
          {t(resolved, "lobby.bot.intro")}
        </p>
        {blocks.map((block) => (
          <section key={block} style={{ marginTop: "30px" }}>
            <h2 className="lb-h3">{t(resolved, `lobby.bot.${block}Title`)}</h2>
            <p className="lb-body">
              {t(resolved, `lobby.bot.${block}Body`, { email: DESK_EMAIL })}
            </p>
          </section>
        ))}
      </article>
    </LobbyShell>
  );
}
