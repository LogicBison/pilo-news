import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { LegalPage } from "@/components/lobby/LobbyPage";
import { isLocale, resolveLocale, t } from "@/lib/i18n";
import { pageMetadata } from "@/lib/seo";

export const dynamic = "force-dynamic";

type Params = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale } = await params;
  const resolved = resolveLocale(locale);
  return pageMetadata({
    title: t(resolved, "lobby.legal.termsTitle"),
    description: t(resolved, "lobby.legal.termsTitle"),
    path: "/terms",
    locale: resolved,
    absoluteTitle: true,
  });
}

export default async function TermsPage({ params }: Params) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  return <LegalPage locale={resolveLocale(locale)} kind="terms" />;
}
