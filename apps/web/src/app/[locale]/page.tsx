import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { localePath, resolveLocale } from "@/lib/i18n";

export const dynamic = "force-dynamic";

export default async function LocaleIndex({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const resolved = resolveLocale(locale);
  const industry = process.env.SN_DEFAULT_INDUSTRY ?? "legal";
  redirect(localePath(resolved, `/${industry}`));
}

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};
