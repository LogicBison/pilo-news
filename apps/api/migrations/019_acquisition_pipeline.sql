-- Acquisition pipeline and per-source fetch history.
--
-- `source_candidates` is the queue between "a feed looks promising" and "the
-- profile says we read it": discovery writes rows, an operator decides, and the
-- decision keeps its note and date. The profile stays the publishing record;
-- this table is the working trail.
--
-- `source_fetch_stats` is one row per source per day, written by the ingest
-- path. Articles alone cannot tell a refused feed from a quiet one; attempts,
-- successes and refusals can.

CREATE TABLE IF NOT EXISTS source_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feed_url TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    industry_id UUID REFERENCES industries (id) ON DELETE SET NULL,
    language TEXT NOT NULL DEFAULT '',
    grade TEXT,
    overlap NUMERIC(4, 3),
    verdict TEXT NOT NULL DEFAULT 'review'
        CHECK (verdict IN ('accept', 'review', 'reject')),
    status TEXT NOT NULL DEFAULT 'new'
        CHECK (status IN ('new', 'shortlisted', 'accepted', 'dismissed')),
    note TEXT NOT NULL DEFAULT '',
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at TIMESTAMPTZ,
    CONSTRAINT uq_source_candidates_feed UNIQUE (feed_url)
);

CREATE INDEX IF NOT EXISTS ix_source_candidates_status
    ON source_candidates (status, discovered_at DESC);

CREATE TABLE IF NOT EXISTS source_fetch_stats (
    source_id UUID NOT NULL REFERENCES sources (id) ON DELETE CASCADE,
    day DATE NOT NULL DEFAULT CURRENT_DATE,
    attempts INTEGER NOT NULL DEFAULT 0,
    ok INTEGER NOT NULL DEFAULT 0,
    blocked INTEGER NOT NULL DEFAULT 0,
    denied INTEGER NOT NULL DEFAULT 0,
    items INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (source_id, day)
);
