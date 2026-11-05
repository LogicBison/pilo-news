import type { Metadata } from "next";
import { headers } from "next/headers";
import type { ReactNode } from "react";

import { HydrationMarker } from "@/components/HydrationMarker";
import { SITE_URL } from "@/lib/seo";

import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "System News",
    template: "%s | System News",
  },
  description: "Industry news for professionals, in English and Spanish.",
  robots: { index: true, follow: true },
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const requestHeaders = await headers();
  const locale = requestHeaders.get("x-sn-locale") === "es" ? "es" : "en";
  return (
    <html lang={locale}>
      <body>
        <HydrationMarker />
        {children}
      </body>
    </html>
  );
}
