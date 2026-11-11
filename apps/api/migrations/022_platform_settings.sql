-- M22: runtime settings an operator may override without a redeploy.
--
-- `.env.<env>` stays the deployment's default; this table holds the values the
-- admin console has changed. One row per setting family so a whole panel saves
-- atomically. Secrets are deliberately not eligible: the API key never enters
-- the database.

CREATE TABLE IF NOT EXISTS platform_settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by TEXT
);
