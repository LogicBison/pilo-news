import { getIndustry, getNews } from "@/lib/api";
import { localePath, resolveLocale } from "@/lib/i18n";
import { SITE_URL } from "@/lib/seo";

const ITEM_LIMIT = 40;

function escapeXml(value: string): string {
  return value
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function pubDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? new Date().toUTCString() : date.toUTCString();
}

/**
 * Per-channel RSS 2.0 feed. Every channel gets one in both locales so readers
 * can follow a desk without an account and without email.
 */
export async function GET(
  _request: Request,
  context: { params: Promise<{ locale: string; industry: string }> },
) {
  const { locale, industry } = await context.params;
  const resolved = resolveLocale(locale);
  const channel = await getIndustry(industry, resolved);
  if (!channel.ok) {
    return new Response("Not found", { status: 404 });
  }

  const news = await getNews(industry, resolved, { limit: ITEM_LIMIT });
  const items = news.ok ? news.data : [];
  const home = `${SITE_URL}${localePath(resolved, `/${industry}`)}`;
  const feed = `${home}/feed.xml`;
  const description = channel.data.tagline || channel.data.name;

  const entries = items
    .map((article) => {
      const link = `${SITE_URL}${localePath(resolved, `/${industry}/article/${article.id}`)}`;
      const body = article.summary ?? article.excerpt ?? article.title;
      const categories = article.topics
        .slice(0, 4)
        .map((topic) => `      <category>${escapeXml(topic.label)}</category>`)
        .join("\n");
      return [
        "    <item>",
        `      <title>${escapeXml(article.title)}</title>`,
        `      <link>${escapeXml(link)}</link>`,
        `      <guid isPermaLink="true">${escapeXml(link)}</guid>`,
        `      <pubDate>${pubDate(article.published_at)}</pubDate>`,
        `      <description>${escapeXml(body)}</description>`,
        categories,
        "    </item>",
      ]
        .filter(Boolean)
        .join("\n");
    })
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${escapeXml(`${channel.data.name} — System News`)}</title>
    <link>${escapeXml(home)}</link>
    <description>${escapeXml(description)}</description>
    <language>${resolved}</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${escapeXml(feed)}" rel="self" type="application/rss+xml" />
${entries}
  </channel>
</rss>
`;

  return new Response(xml, {
    status: 200,
    headers: {
      "content-type": "application/rss+xml; charset=utf-8",
      "cache-control": "public, s-maxage=600, stale-while-revalidate=60",
    },
  });
}
