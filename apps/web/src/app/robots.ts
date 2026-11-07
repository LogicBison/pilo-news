import type { MetadataRoute } from "next";

import { channelDomain } from "@/lib/hosts";
import { requestSite } from "@/lib/url";

export const dynamic = "force-dynamic";

export default async function robots(): Promise<MetadataRoute.Robots> {
  const site = await requestSite();

  // The apex is the network's front door: the lobby, the services page and the
  // legal pages are indexable. Only the console and machine endpoints are not.
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/admin", "/es/admin", "/api/", "/v1/"],
      },
    ],
    sitemap: `${site.origin}/sitemap.xml`,
    host: site.origin,
  };
}
