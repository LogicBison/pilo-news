import type { MetadataRoute } from "next";

import { getIndustries } from "@/lib/api";
import { SITE_URL } from "@/lib/seo";

const FALLBACK_SLUGS = ["legal", "financial", "behavioral-health", "education", "logistics"];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const result = await getIndustries("en");
  const slugs = result.ok ? result.data.map((industry) => industry.slug) : FALLBACK_SLUGS;
  const paths = ["", "/about", "/contact", "/search"];
  const entries: MetadataRoute.Sitemap = [];

  for (const slug of slugs) {
    for (const suffix of paths) {
      const path = `/${slug}${suffix}`;
      entries.push({
        url: `${SITE_URL}${path}`,
        lastModified: new Date(),
        changeFrequency: suffix === "" ? "hourly" : "monthly",
        priority: suffix === "" ? 0.9 : 0.5,
        alternates: {
          languages: {
            en: `${SITE_URL}${path}`,
            es: `${SITE_URL}/es${path}`,
          },
        },
      });
    }
  }
  return entries;
}
