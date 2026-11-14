-- M22: the AI usage ledger, durable and provider-shaped.
--
-- One row per bucket - a UTC day and a UTC month - counting what the provider
-- actually bills (requests, tokens) next to the dollar estimate this stack
-- derives from config/scoring.json. Before this the cap lived only in Redis:
-- a volume loss, a `destroy`, or a dev->prd restore started the month at zero
-- spent, and nothing bounded a single day inside it.
--
-- `halted_reason` is the kill switch. An auth rejection (401/403) or an open
-- circuit breaker writes a reason here, and every later call is denied without
-- touching the network until an operator resumes from /admin or, for the
-- breaker, `halted_until` passes.

CREATE TABLE IF NOT EXISTS ai_usage (
    bucket_kind TEXT NOT NULL,
    bucket TEXT NOT NULL,
    requests BIGINT NOT NULL DEFAULT 0,
    requests_held BIGINT NOT NULL DEFAULT 0,
    tokens_prompt BIGINT NOT NULL DEFAULT 0,
    tokens_completion BIGINT NOT NULL DEFAULT 0,
    tokens_cache_hit BIGINT NOT NULL DEFAULT 0,
    tokens_held BIGINT NOT NULL DEFAULT 0,
    cost_usd NUMERIC(16, 8) NOT NULL DEFAULT 0,
    cost_held_usd NUMERIC(16, 8) NOT NULL DEFAULT 0,
    halted_reason TEXT,
    halted_until TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ai_usage_pk PRIMARY KEY (bucket_kind, bucket),
    CONSTRAINT ai_usage_bucket_kind_check CHECK (bucket_kind IN ('day', 'month'))
);

CREATE INDEX IF NOT EXISTS ix_ai_usage_bucket ON ai_usage (bucket);
