-- Source availability: what a publisher allows, and how we prove it.
--
-- The crawler can be as polite as it likes; if the publisher refuses us the
-- source is dead weight. This table's new columns carry the permission record
-- (robots verdict, snapshot hash, when it was checked) and the credentials a
-- licensed feed needs. Secrets are never stored: `auth_secret_ref` names an
-- environment variable the fetcher reads at request time.

ALTER TABLE sources ADD COLUMN IF NOT EXISTS permission_state TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE sources ADD COLUMN IF NOT EXISTS robots_checked_at TIMESTAMPTZ;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS robots_hash TEXT;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS robots_crawl_delay INTEGER;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS auth_type TEXT NOT NULL DEFAULT 'none';
ALTER TABLE sources ADD COLUMN IF NOT EXISTS auth_header_name TEXT;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS auth_secret_ref TEXT;

ALTER TABLE sources DROP CONSTRAINT IF EXISTS sources_permission_state_check;
ALTER TABLE sources
    ADD CONSTRAINT sources_permission_state_check
    CHECK (permission_state IN ('unknown', 'allowed', 'denied', 'licensed'));

ALTER TABLE sources DROP CONSTRAINT IF EXISTS sources_auth_type_check;
ALTER TABLE sources
    ADD CONSTRAINT sources_auth_type_check
    CHECK (auth_type IN ('none', 'header', 'basic'));
