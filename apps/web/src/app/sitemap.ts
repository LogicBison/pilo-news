import type { MetadataRoute } from "next";

import { getIndustries, getReferences } from "@/lib/api";
import { channelDomain } from "@/lib/hosts";
import { localePath } from "@/lib/i18n";
import { channelOrigin, requestSite } from "@/lib/url";

export const dynamic = "force-dynamic";

const FALLBACK_SLUGS = ["legal", "financial", "behavioral-health", "education", "logistics"];

/**
 * One sitemap per host. A channel subdomain lists only its own URLs; the apex
 * doorway (and `/sitemap.xml` on it) lists nothing, because every apex URL
 * either redirects to a channel site or is not indexable.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const site = await requestSite();

  // The apex now has content of its own: the lobby, the services page and the
  // network legal pages. Everything else on the apex is a desk, and desks list
  // themselves on their own host.
  if (channelDomain() && !site.channel) {
    const apexPaths = ["", "/services", "/privacy", "/terms"];
    return apexPaths.flatMap((suffix) => {
      const en = `${site.origin}${suffix || "/"}`;
      const es = `${site.origin}/es${suffix}`;
      return [
        {
          url: en,
          lastModified: new Date(),
          changeFrequency: suffix === "" ? "daily" : "monthly",
          priority: suffix === "" ? 1 : 0.7,
          alternates: { languages: { en, es, "x-default": en } },
        },
        {
          url: es,
          lastModified: new Date(),
          changeFrequency: suffix === "" ? "daily" : "monthly",
          priority: suffix === "" ? 0.9 : 0.6,
          alternates: { languages: { en, es, "x-default": en } },
        },
      ];
    });
  }

  const result = await getIndustries("en");
  const allSlugs = result.ok ? result.data.map((industry) => industry.slug) : FALLBACK_SLUGS;
  const slugs = site.channel ? allSlugs.filter((slug) => slug === site.channel) : allSlugs;
  const entries: MetadataRoute.Sitemap = [];

  for (const slug of slugs) {
    // A channel's own host is its canonical home, so every entry is rooted at
    // the subdomain with no `/<slug>` prefix.
    const origin = await channelOrigin(slug);
    const href = (suffix: string) => `${origin}${localePath("en", suffix || "/")}`;
    const alternates = (suffix: string) => {
      const en = href(suffix);
      const es = `${origin}${localePath("es", suffix || "/")}`;
      return { languages: { en, es, "x-default": en } };
    };

    for (const suffix of ["", "/about", "/contact", "/search", "/privacy", "/terms"]) {
      entries.push({
        url: href(suffix),
        lastModified: new Date(),
        changeFrequency: suffix === "" ? "hourly" : "monthly",
        priority: suffix === "" ? 0.9 : 0.5,
        alternates: alternates(suffix),
      });
    }

    entries.push({
      url: href("/references"),
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.6,
      alternates: alternates("/references"),
    });

    const references = await getReferences(slug, "en");
    if (references.ok) {
      for (const issue of references.data) {
        entries.push({
          url: href(`/references/${issue.issue_date}`),
          lastModified: issue.published_at ? new Date(issue.published_at) : new Date(),
          changeFrequency: "yearly",
          priority: 0.5,
        });
      }
    }
  }
  return entries;
}
