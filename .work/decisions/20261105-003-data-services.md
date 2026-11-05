# ADR 003 - Supporting data services: Redis 7 + Postgres FTS

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** cache, queue, search, and object-storage needs beyond the primary store.

## Context

Evidence driving each service class:

- **Cache:** public API has repeated identical reads across many consumers; NFR-1 p95 < 250 ms; publisher feeds must not be hit per reader; rate limits need a fast counter store. Redis is justified (`stated` targets + `assumed` traffic).
- **Queue/async:** ingestion and AI summarization run outside the request path; refresh must be single-flight; retries and dead-letter behavior are needed. A lightweight queue on existing Redis avoids a second broker at v1 volume.
- **Search:** article corpus is M rows with FTS over title+summary; Postgres `tsvector` + GIN covers it with zero new infra. Dedicated engine deferred (UNKNOWNS U13).
- **Object storage:** no user uploads, no media rehosting, no exports in v1 → **none** (UNKNOWNS U14).

## Decision

- **Redis 7** for: response cache (TTL 30-60 s, ETag support), distributed locks (refresh single-flight), rate-limit counters, and **Redis Streams** as the job queue (`news:jobs` stream + consumer group `worker`).
- **PostgreSQL full-text search** (`search_vector` generated column, GIN, `ts_rank_cd` + `websearch_to_tsquery`) behind a `SearchPort` so it can be swapped later.
- **No object storage** in v1. Backups are volume `.tar.gz` snapshots uploaded to an off-site bucket (provider decided in O3); that is a backup destination, not an application storage dependency.
- **No dedicated broker** (RabbitMQ/SQS) in v1.

## Consequences

- **Positive:** one extra service; cache and queue share Redis; simple operational model; search has no new service; swap paths exist (`SearchPort`, queue abstraction).
- **Negative:** Redis is a SPOF for latency and rate limiting (degrade to uncached/deny-safe); Streams lack broker-grade retention guarantees; FTS relevance tuning is limited.
- **Neutral:** when article volume or search SLA grows, add Meilisearch/Typesense behind `SearchPort` (no API change).

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| No cache / no queue | NFR-1 and single-flight refresh would be violated; per-request feed fetches are abusive |
| RabbitMQ / SQS | More durable, but another service and cost for v1 volume |
| Meilisearch / Elasticsearch | Faster search, but extra service + ops; not justified at M rows |
| MinIO / S3 | No file workload in v1 |

## References

- Doc 04 §5 (NFRs), §10 (stack)
- Doc 02 §4 (rate limits)
- `UNKNOWNS.md` U13, U14

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
