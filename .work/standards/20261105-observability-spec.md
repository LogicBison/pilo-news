# Observability Spec - System News v1

**What it is:** the metrics, logs, traces, SLOs, and alerts every context must emit.
**Status:** Approved for implementation (2026-11-05) · **Needs:** nothing.

**Principle:** if a failure would be invisible on a dashboard, it is not done. Every new path adds at least one metric and one log line.

---

## 1. Signals and tooling

| Signal | Tool | Retention |
|--------|------|-----------|
| Metrics | Prometheus (scrape `/metrics` on api/worker) | 30 days |
| Logs | `structlog` JSON → stdout → Docker `json-file` (rotated) | 14 days |
| Traces | OpenTelemetry SDK → OTLP (optional v1; spans instrumented from day one) | 7 days |
| Uptime | External check on `/v1/health` every 60 s | 90 days |
| Dashboards | Grafana (single board per context + one platform board) | - |

## 2. Naming convention

`<subsystem>_<noun>_<unit>` with a `_total` suffix for counters and `_seconds` / `_bytes` for histograms/gauges. Labels are low-cardinality only: `route`, `method`, `status_class`, `industry`, `source`, `locale`, `result`. Never put IDs, URLs, or emails in labels.

## 3. Metrics by context

### platform / HTTP

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `http_requests_total` | counter | route, method, status_class | Traffic + error rate |
| `http_request_duration_seconds` | histogram | route, method | p50/p95/p99 latency (NFR-1) |
| `http_in_flight_requests` | gauge | - | Saturation |
| `rate_limited_total` | counter | scope (`ip`/`key`) | Abuse signal (T8) |
| `db_pool_in_use` / `db_pool_wait_seconds` | gauge/histogram | - | DB saturation |
| `cache_hits_total` / `cache_misses_total` | counter | cache (`api_bundle`, `rate_limit`) | Cache effectiveness |

### articles / ingestion

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `ingest_fetch_total` | counter | source, status (`ok`/`http_error`/`parse_error`/`timeout`) | Source health (R5) |
| `ingest_fetch_duration_seconds` | histogram | source | Slow feeds |
| `ingest_items_total` | counter | industry, result (`new`/`updated`/`skipped`/`duplicate`) | Throughput |
| `ingest_lag_seconds` | histogram | industry | NFR-5 freshness |
| `articles_scored_total` | counter | industry, result (`kept`/`filtered`) | Ranking behavior |
| `refresh_runs_total` | counter | trigger, status | Pipeline reliability; `trigger=schedule|manual|reset` |
| `refresh_duration_seconds` | histogram | industry | Run time |

### articles / AI summaries

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `summaries_generated_total` | counter | language, status (`ok`/`skipped`/`failed`/`invalid`) | Quality/coverage |
| `summary_latency_seconds` | histogram | locale | Provider latency |
| `ai_tokens_total` | counter | model, direction (`prompt`/`completion`) | Cost (R3) |
| `ai_estimated_cost_usd_total` | counter | model | Budget alert |

### publishing

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `news_reads_total` | counter | industry, endpoint, language | Channel usage |
| `refresh_manual_total` | counter | industry | On-demand polling usage |
| `contact_submissions_total` | counter | industry, result | Form health |
| `leads_total` | counter | industry, status | Lead funnel |
| `leads_rate_limited_total` | counter | industry | Abuse signal |
| `lead_route_latency_seconds` | histogram | industry | Partner SLA |
| `cta_events_total` | counter | industry, event, placement | Funnel top |
| `contact_rate_limited_total` | counter | industry | Spam signal |

### editorial

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `admin_auth_total` | counter | result | Login monitoring |
| `admin_mutations_total` | counter | action | Audit volume |
| `api_keys_active` | gauge | - | Key inventory |

## 4. Logs

**Required fields:** `ts`, `level`, `event`, `request_id`, `route`, `method`, `status`, `duration_ms`, `locale`, `industry` (when applicable), `error_code` (when applicable).

**Forbidden:** email, phone, message body, authorization header, API key, feed URL with credentials, full query string.

**Events:** `ingest.fetch`, `ingest.parse_error`, `article.published`, `article.hidden`, `summary.failed`, `admin.login`, `admin.mutation`, `contact.received` (no PII body).

**Request logging is by outcome, not by traffic** (2026-11-07). Volume belongs in
Prometheus; the log carries what a human has to read:

| Outcome | Event | Level |
|---|---|---|
| 5xx | `request.failed` | error |
| 4xx | `request.rejected` | warning |
| 2xx/3xx slower than `LOG_SLOW_REQUEST_MS` (default 1000) | `request.slow` | info |
| any other 2xx/3xx | `request.end` | debug — invisible at `LOG_LEVEL=info` |

`/v1/health`, `/v1/health/ready` and `/metrics` are never logged: they are probes,
they are already counted, and at two probes a minute they were the loudest lines
in the log. Uvicorn runs with `--no-access-log` for the same reason — the
middleware is the single writer of request lines.

## 5. SLOs and alerts

| SLO | Target | Alert |
|-----|--------|-------|
| Availability | 99.9% / 30 d | 5xx rate > 1% for 5 min |
| API latency | p95 < 250 ms cached | p95 > 500 ms for 10 min |
| Freshness | scheduled ≤ 12 h; manual ≤ 60 s | `ingest_lag_seconds` p95 > 43200 s (scheduled) |
| Stale channel | 0 | no successful run for 2 scheduled intervals (24 h) |
| AI health | failure < 10% | `summaries_generated_total{status="failed"}` ratio > 10% for 30 min |
| Backup | daily | backup age > 26 h |
| Disk | < 80% | > 80% for 15 min |
| Error budget | 0.1% | burn rate > 10x for 1 h |

## 6. Health endpoints

| Endpoint | Checks |
|----------|--------|
| `GET /v1/health` | process up; DB `SELECT 1`; Redis `PING`; migrations applied |
| `GET /v1/health/ready` | same + cache warm (optional) |
| `GET /metrics` | Prometheus scrape (internal network only in prd) |

## 7. Dashboards

1. **Platform:** request rate, error rate, latency, saturation, cache hit ratio.
2. **Pipeline:** fetch success per source, items in/out, lag, refresh duration, queue depth.
3. **AI:** summaries ok/failed, tokens, cost, latency.
4. **Content:** reads per channel, contact submissions, top topics.

## 8. Review log

| Date | Reviewer | Change |
|------|----------|--------|
| 2026-11-05 | plan-foundation | Initial spec |

---

## Next action

None - binding as written; amend with a new dated standard when the stack, threat model, or API contract changes.
