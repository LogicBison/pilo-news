-- 015_lead_attribution.sql - non-PII attribution for leads and contact messages.
-- Idempotent: columns are IF NOT EXISTS; existing rows stay valid.

ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS country TEXT;

ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS session_hash TEXT;

ALTER TABLE contact_messages
    ADD COLUMN IF NOT EXISTS source_page TEXT;

ALTER TABLE contact_messages
    ADD COLUMN IF NOT EXISTS utm JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE contact_messages
    ADD COLUMN IF NOT EXISTS ip_hash TEXT;

ALTER TABLE contact_messages
    ADD COLUMN IF NOT EXISTS ua_hash TEXT;

ALTER TABLE contact_messages
    ADD COLUMN IF NOT EXISTS country TEXT;

ALTER TABLE contact_messages
    ADD COLUMN IF NOT EXISTS session_hash TEXT;
