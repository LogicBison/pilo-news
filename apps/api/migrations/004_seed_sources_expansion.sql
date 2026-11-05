-- 004_seed_sources_expansion.sql - verified secondary feeds per channel.
-- Idempotent: inserts only missing rows; never overwrites operator edits.
-- Verification: every URL returned a parseable RSS/Atom document on 2026-11-05.

INSERT INTO sources (industry_id, name, feed_url, language, trust, enabled, poll_interval_min)
SELECT i.id, v.name, v.feed_url, v.language, v.trust, TRUE, 720
FROM industries i
JOIN (
    VALUES
        ('legal', 'Above the Law', 'https://abovethelaw.com/feed/', 'en', 0.85),
        ('legal', 'Diario Jurídico', 'https://www.diariojuridico.com/feed/', 'es', 0.78),
        ('financial', 'WSJ Markets', 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml', 'en', 0.92),
        ('behavioral-health', 'Psychology Today', 'https://www.psychologytoday.com/us/front/feed', 'en', 0.85),
        ('behavioral-health', 'Infocop', 'https://www.infocop.es/feed/', 'es', 0.80),
        ('education', 'The Hechinger Report', 'https://hechingerreport.org/feed/', 'en', 0.87),
        ('logistics', 'Supply Chain Dive', 'https://www.supplychaindive.com/feeds/news/', 'en', 0.85)
) AS v (industry_slug, name, feed_url, language, trust) ON v.industry_slug = i.slug
ON CONFLICT (industry_id, feed_url) DO NOTHING;
