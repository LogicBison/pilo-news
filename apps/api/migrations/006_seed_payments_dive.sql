-- 006_seed_payments_dive.sql - fourth financial source to meet the coverage floor.
-- Idempotent: inserts only the missing row.

INSERT INTO sources (industry_id, name, feed_url, language, trust, enabled, poll_interval_min)
SELECT i.id, 'Payments Dive', 'https://www.paymentsdive.com/feeds/news/', 'en', 0.85, TRUE, 720
FROM industries i
WHERE i.slug = 'financial'
ON CONFLICT (industry_id, feed_url) DO NOTHING;
