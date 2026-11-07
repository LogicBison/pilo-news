import type { Metadata } from "next";
import { headers } from "next/headers";
import type { ReactNode } from "react";

import { HydrationMarker } from "@/components/HydrationMarker";
import { requestSite } from "@/lib/url";

import "./globals.css";
import "./skins.css";

// Per-request so a channel subdomain resolves relative assets, OG images and
// canonical fallbacks against its own origin instead of APP_BASE_URL.
export async function generateMetadata(): Promise<Metadata> {
  const { origin } = await requestSite();
  return {
    metadataBase: new URL(origin),
    title: {
      default: "System News",
      template: "%s | System News",
    },
    description: "Industry news for professionals, in English and Spanish.",
    robots: { index: true, follow: true },
  };
}

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
