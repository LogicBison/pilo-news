-- 007_retention_alignment.sql - align the visible retention window with purge policy.
-- Seeded channels used a 7-day window while purge_after_days is 30, so a month of
-- published coverage was hidden. Raise the default window to 30 days.
-- Idempotent: only rows still on the 7-day default are changed; operator edits are kept.

UPDATE industries
SET retention_days = 30,
    updated_at = now()
WHERE retention_days = 7;
