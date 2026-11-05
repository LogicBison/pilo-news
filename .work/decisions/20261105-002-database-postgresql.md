# ADR 002 - Primary database: PostgreSQL 16

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** the durable store for channels, sources, articles, keys, and audit.

## Context

- The reference implementation stores bundles in a JSON file (`api/data/news_cache.json` pattern) with an in-process lock. That cannot support concurrent API + worker writers, ad-hoc filtering, or cursor pagination across channels.
- Entities are relational: industries → sources → articles, topics M:N, pins, API keys, audit events.
- NFRs require p95 read latency, full-text search, and transactional ingestion upserts.
- Volume class **M** rows (10k-1M articles, 7-day hot window, 30-day retention).

## Decision

Use **PostgreSQL 16** with:

- **SQLAlchemy 2.0 async** models, one persistence module per bounded context.
- **Idempotent numbered SQL** under `apps/api/migrations/`, applied by `news_api.platform.migrations` at startup (no Alembic autogenerate as source of truth).
- **`tsvector` generated column + GIN index** for full-text search (see ADR 003).
- **JSONB** for theme tokens, disclaimers, topic keywords/labels, and run stats.
- **`citext`/`lower()` unique** on `industries.slug` and `sources.feed_url` per industry.

## Consequences

- **Positive:** transactional ingestion, cross-channel queries, mature backup/restore (`pg_dump`), full-text search without new infra, easy local dev via Docker.
- **Negative:** one more service to operate; schema changes need disciplined numbered migrations; JSONB needs validation in the application layer.
- **Neutral:** read replicas deferred; single primary is fine for NFR-4.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| SQLite | Single-writer; poor concurrent worker + API story; no FTS ranking parity at scale |
| MongoDB | Flexible documents, but relationships and transactional upserts matter more; weaker operational familiarity here |
| MySQL | Viable, but JSONB/FTS/RLS ergonomics and the team's Postgres familiarity favor Postgres |
| Keep JSON cache | No durability, no query, no partial updates, no multi-process safety |

## References

- Doc 04 §4 (data model)
- `.work/standards/20261105-data-classification.md`
- `.cursorrules` § Database & Schema Rules

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
