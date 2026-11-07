import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { LobbyPage, lobbyMetadata } from "@/components/lobby/LobbyPage";
import { isLocale, resolveLocale } from "@/lib/i18n";

export const dynamic = "force-dynamic";

type Params = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale } = await params;
  return lobbyMetadata(resolveLocale(locale));
}

export default async function LocaleIndex({ params }: Params) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  return <LobbyPage locale={resolveLocale(locale)} />;
}
