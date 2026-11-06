-- 013_channel_automation.sql - per-channel fetch cadence and free-offer switches.
-- Idempotent: columns are IF NOT EXISTS, the constraint is dropped and re-added.

ALTER TABLE industries
    ADD COLUMN IF NOT EXISTS fetch_interval_minutes INTEGER;

ALTER TABLE industries
    ADD COLUMN IF NOT EXISTS auto_fetch_enabled BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE industries
    ADD COLUMN IF NOT EXISTS offers JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE industries DROP CONSTRAINT IF EXISTS industries_fetch_interval_check;
ALTER TABLE industries
    ADD CONSTRAINT industries_fetch_interval_check
    CHECK (fetch_interval_minutes IS NULL OR fetch_interval_minutes BETWEEN 5 AND 1440);
