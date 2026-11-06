-- 014_offer_issues.sql - dated offer issues generated from public source adapters.
-- Idempotent: table and indexes use IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS offer_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    offer_slug TEXT NOT NULL,
    issue_date DATE NOT NULL,
    scope TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'building', 'draft', 'empty', 'failed', 'published')),
    title TEXT NOT NULL,
    standfirst TEXT NOT NULL DEFAULT '',
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_version TEXT,
    reviewer TEXT,
    error TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ,
    UNIQUE (industry_id, offer_slug, issue_date)
);

CREATE INDEX IF NOT EXISTS ix_offer_issues_industry_date
    ON offer_issues (industry_id, issue_date DESC);

CREATE INDEX IF NOT EXISTS ix_offer_issues_status
    ON offer_issues (status, generated_at DESC);
