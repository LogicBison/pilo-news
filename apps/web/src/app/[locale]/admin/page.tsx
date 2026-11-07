import type { Metadata } from "next";

import { resolveLocale } from "@/lib/i18n";

import { DevelopedBy } from "@/components/DevelopedBy";

import { AdminConsole } from "./AdminConsole";

export const metadata: Metadata = {
  title: "Editorial console",
  robots: { index: false, follow: false },
};

export default async function AdminPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const resolved = resolveLocale(locale);
  return (
    <>
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <AdminConsole
          locale={resolved}
          defaultIndustry={process.env.SN_DEFAULT_INDUSTRY ?? "legal"}
        />
      </main>
      <footer className="mx-auto max-w-6xl px-4 pb-8 sm:px-6">
        <DevelopedBy locale={resolved} />
      </footer>
    </>
  );
}
