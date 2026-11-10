-- Acquisition quality: better overlap, and a shareable traffic record.
--
-- `pg_trgm` makes "is this the same story" a database question instead of
-- loading every recent title into the CLI. The extension ships with Postgres;
-- CREATE EXTENSION needs the database owner, which the app role is in this
-- deployment.
--
-- `traffic_token` is the unguessable handle for a publisher's own traffic page.
-- Generated on demand, unique per source, never derived from the id.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS ix_articles_title_trgm
    ON articles USING gin (title gin_trgm_ops);

ALTER TABLE sources ADD COLUMN IF NOT EXISTS traffic_token TEXT UNIQUE;
