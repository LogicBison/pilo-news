import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { ServicesPage, servicesMetadata } from "@/components/lobby/LobbyPage";
import { isLocale, resolveLocale } from "@/lib/i18n";

export const dynamic = "force-dynamic";

type Params = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { locale } = await params;
  return servicesMetadata(resolveLocale(locale));
}

export default async function Services({ params }: Params) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  return <ServicesPage locale={resolveLocale(locale)} />;
}
