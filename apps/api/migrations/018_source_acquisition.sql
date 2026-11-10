-- Source acquisition: what we are allowed to read, and what we send back.
--
-- `permission_state` records whether the publisher lets us in; `licence_type`
-- records why we may republish a headline and an excerpt. Outreach history is
-- operational data, so it lives here rather than in the deployment profile.
--
-- `outbound_clicks` is the return traffic: one integer per article, no reader
-- identifier. It is the number that answers "what do you send us" in a
-- publisher conversation.

ALTER TABLE sources ADD COLUMN IF NOT EXISTS licence_type TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE sources ADD COLUMN IF NOT EXISTS contacted_at TIMESTAMPTZ;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS outreach_note TEXT;

ALTER TABLE sources DROP CONSTRAINT IF EXISTS sources_licence_type_check;
ALTER TABLE sources
    ADD CONSTRAINT sources_licence_type_check
    CHECK (
        licence_type IN (
            'unknown',
            'public-domain',
            'cc-by',
            'cc-by-sa',
            'syndication',
            'licensed',
            'proprietary'
        )
    );

ALTER TABLE articles ADD COLUMN IF NOT EXISTS outbound_clicks INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS ix_articles_source_created
    ON articles (source_id, created_at DESC);
