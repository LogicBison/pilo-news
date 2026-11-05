-- 005_source_quality.sql - quality policy applied to the seeded feed portfolio.
-- Idempotent: inserts only missing rows, disables feeds that fail the quality gate.

-- WSJ Markets (added in 004) serves a legacy, stale document: newest item was
-- 647 days old when verified on 2026-11-05. Disable rather than delete so
-- provenance and operator history survive.
UPDATE sources
SET enabled = FALSE,
    last_error = 'quality: stale feed (newest item 647 days old)',
    updated_at = now()
WHERE feed_url = 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml'
  AND enabled = TRUE;

-- Secondary feeds that passed live verification on 2026-11-05.
INSERT INTO sources (industry_id, name, feed_url, language, trust, enabled, poll_interval_min)
SELECT i.id, v.name, v.feed_url, v.language, v.trust, TRUE, 720
FROM industries i
JOIN (
    VALUES
        ('financial', 'Banking Dive', 'https://www.bankingdive.com/feeds/news/', 'en', 0.85),
        ('education', 'Higher Ed Dive', 'https://www.highereddive.com/feeds/news/', 'en', 0.85),
        ('education', 'Educación Futura', 'https://www.educacionfutura.org/feed/', 'es', 0.78),
        ('logistics', 'Trucking Dive', 'https://www.truckingdive.com/feeds/news/', 'en', 0.85)
) AS v (industry_slug, name, feed_url, language, trust) ON v.industry_slug = i.slug
ON CONFLICT (industry_id, feed_url) DO NOTHING;
