-- 001_init.sql - System News durable schema.
-- Idempotent: safe to run on every application start (runner records checksums).

CREATE TABLE IF NOT EXISTS industries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    theme JSONB NOT NULL DEFAULT '{}'::jsonb,
    locales TEXT[] NOT NULL DEFAULT ARRAY['en']::TEXT[],
    disclaimers JSONB NOT NULL DEFAULT '{}'::jsonb,
    cta JSONB NOT NULL DEFAULT '{}'::jsonb,
    timezone TEXT NOT NULL DEFAULT 'America/El_Salvador',
    retention_days INTEGER NOT NULL DEFAULT 7 CHECK (retention_days BETWEEN 1 AND 90),
    sort_order INTEGER NOT NULL DEFAULT 0,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_industries_enabled_sort
    ON industries (enabled, sort_order, slug);

CREATE TABLE IF NOT EXISTS industry_locales (
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    locale TEXT NOT NULL,
    name TEXT NOT NULL,
    tagline TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (industry_id, locale)
);

CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    feed_url TEXT NOT NULL,
    language TEXT NOT NULL,
    trust NUMERIC(3, 2) NOT NULL DEFAULT 0.70 CHECK (trust >= 0 AND trust <= 1),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    allow_http BOOLEAN NOT NULL DEFAULT FALSE,
    poll_interval_min INTEGER NOT NULL DEFAULT 720 CHECK (poll_interval_min BETWEEN 5 AND 1440),
    terms_checked_at TIMESTAMPTZ,
    terms_url TEXT,
    etag TEXT,
    last_modified TEXT,
    last_fetched_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'blocked')),
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_sources_industry_feed UNIQUE (industry_id, feed_url)
);

CREATE INDEX IF NOT EXISTS ix_sources_industry_enabled
    ON sources (industry_id, enabled, language);

CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    label JSONB NOT NULL DEFAULT '{}'::jsonb,
    weight NUMERIC(4, 2) NOT NULL DEFAULT 1.00 CHECK (weight > 0 AND weight <= 10),
    keywords JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_topics_industry_slug UNIQUE (industry_id, slug)
);

CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY,
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources (id) ON DELETE SET NULL,
    canonical_url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    excerpt TEXT,
    summary TEXT,
    publisher TEXT NOT NULL DEFAULT '',
    language TEXT NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    score DOUBLE PRECISION NOT NULL DEFAULT 0,
    corroboration INTEGER NOT NULL DEFAULT 1 CHECK (corroboration >= 1),
    corroborating_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    verification TEXT NOT NULL DEFAULT 'trusted-source'
        CHECK (verification IN ('corroborated', 'trusted-source', 'single-source')),
    status TEXT NOT NULL DEFAULT 'published'
        CHECK (status IN ('draft', 'published', 'hidden', 'archived')),
    summary_source TEXT CHECK (summary_source IN ('ai', 'editor')),
    summary_language TEXT,
    summary_version INTEGER NOT NULL DEFAULT 1,
    is_seed BOOLEAN NOT NULL DEFAULT FALSE,
    hidden_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector(
            'simple',
            coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(excerpt, '')
        )
    ) STORED,
    CONSTRAINT ck_articles_summary_language
        CHECK (summary_language IS NULL OR summary_language = language)
);

CREATE INDEX IF NOT EXISTS ix_articles_industry_language_status_published
    ON articles (industry_id, language, status, published_at DESC);
CREATE INDEX IF NOT EXISTS ix_articles_order
    ON articles (industry_id, language, score DESC, published_at DESC, id);
CREATE INDEX IF NOT EXISTS ix_articles_search_vector
    ON articles USING gin (search_vector);
CREATE INDEX IF NOT EXISTS ix_articles_source
    ON articles (source_id);

CREATE TABLE IF NOT EXISTS article_topics (
    article_id UUID NOT NULL REFERENCES articles (id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES topics (id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, topic_id)
);

CREATE INDEX IF NOT EXISTS ix_article_topics_topic_article
    ON article_topics (topic_id, article_id);

CREATE TABLE IF NOT EXISTS pins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles (id) ON DELETE CASCADE,
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position BETWEEN 1 AND 5),
    weight NUMERIC(4, 2) NOT NULL DEFAULT 1.00,
    pin_expires_at TIMESTAMPTZ NOT NULL DEFAULT now() + INTERVAL '72 hours',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_pins_industry_position UNIQUE (industry_id, position)
);

CREATE INDEX IF NOT EXISTS ix_pins_article ON pins (article_id);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    key_prefix TEXT NOT NULL,
    scopes TEXT[] NOT NULL DEFAULT ARRAY['read']::TEXT[],
    rate_limit INTEGER NOT NULL DEFAULT 600 CHECK (rate_limit > 0),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_api_keys_hash ON api_keys (key_hash);

CREATE TABLE IF NOT EXISTS contact_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID REFERENCES industries (id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    message TEXT NOT NULL,
    locale TEXT NOT NULL DEFAULT 'en',
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'read', 'closed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_contact_messages_created ON contact_messages (created_at DESC);

CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'disabled')),
    weight NUMERIC(4, 2) NOT NULL DEFAULT 1.00,
    regions JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_partners_industry UNIQUE (industry_id)
);

CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    partner_id UUID REFERENCES partners (id) ON DELETE SET NULL,
    kind TEXT NOT NULL CHECK (kind IN ('consultation', 'brief')),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    message TEXT,
    locale TEXT NOT NULL DEFAULT 'en',
    source_page TEXT,
    article_id UUID REFERENCES articles (id) ON DELETE SET NULL,
    utm JSONB NOT NULL DEFAULT '{}'::jsonb,
    consent_version TEXT NOT NULL,
    consent_at TIMESTAMPTZ NOT NULL,
    ip_hash TEXT NOT NULL,
    ua_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new'
        CHECK (status IN ('new', 'routed', 'contacted', 'qualified', 'closed', 'spam')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_leads_industry_status_created
    ON leads (industry_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_leads_created ON leads (created_at DESC);

CREATE TABLE IF NOT EXISTS lead_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads (id) ON DELETE CASCADE,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_lead_events_lead ON lead_events (lead_id, created_at DESC);

CREATE TABLE IF NOT EXISTS cta_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID NOT NULL REFERENCES industries (id) ON DELETE CASCADE,
    event TEXT NOT NULL CHECK (event IN ('cta_impression', 'cta_click', 'lead_form_start', 'lead_submit')),
    placement TEXT NOT NULL DEFAULT '',
    article_id UUID REFERENCES articles (id) ON DELETE SET NULL,
    locale TEXT NOT NULL DEFAULT 'en',
    session_hash TEXT NOT NULL DEFAULT '',
    result TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_cta_events_industry_created
    ON cta_events (industry_id, created_at DESC);

CREATE TABLE IF NOT EXISTS refresh_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_id UUID REFERENCES industries (id) ON DELETE CASCADE,
    trigger TEXT NOT NULL DEFAULT 'manual' CHECK (trigger IN ('schedule', 'manual', 'reset')),
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'ok', 'partial', 'failed')),
    requested_by TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    stats JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_refresh_runs_industry_started
    ON refresh_runs (industry_id, started_at DESC);
CREATE INDEX IF NOT EXISTS ix_refresh_runs_status ON refresh_runs (status);

CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_audit_events_created ON audit_events (created_at DESC);
CREATE INDEX IF NOT EXISTS ix_audit_events_action ON audit_events (action, created_at DESC);
