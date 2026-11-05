# System News - Foundation and architecture (proposal)

**Doc:** foundation **04** · **Created:** 2026-11-05
**What it is:** the architecture foundation - bounded contexts, stack, repo layout, NFRs, decisions register, and the foundation gate.
**Status:** proposal (2026-11-05) - owner approval of the §11 checklist requested before broad implementation.
**Status gate:** foundation-complete when the §11 checklist passes.

**References:**

- Doc 01 - `.work/plans/foundation/20261105-01-system-news-initial-scope.md`
- Doc 02 - `.work/plans/foundation/20261105-02-integration-resources.md`
- Doc 03 - `.work/plans/foundation/20261105-03-product-adjacency-phased-modules.md`
- `.cursorrules` · `DOCS_TECH_STACK.md` · `.work/standards/*`

---

## 1. First principles (binding)

1. **One deployment, many channels.** Industry isolation is enforced by `industry_id` on every read path, not by separate deployments.
2. **Evidence over memory.** External claims cite doc 02 / the integration mirror; internal claims cite a file path.
3. **Published content is a contract.** Once an item is served by `/v1`, its shape changes only additively within a major version.
4. **Fail open, never fail silent.** Ingestion and AI failures degrade the page, never break it; every degradation is observable.
5. **Cache is disposable.** Postgres is the source of truth; Redis loss changes latency, not correctness.
6. **Copyright-safe by construction.** No full article text or media rehosting; attribution and link-out are structural.
7. **Boring, pinned, replaceable infrastructure.** Prefer proven components with clear upgrade paths over bespoke systems.

---

## 2. Bounded contexts (proposed)

| Context | Responsibility | Owns | Talks via |
|---------|----------------|------|-----------|
| `news_api.platform` | Cross-cutting platform | settings, structured logging, DB pool, Redis client, migration runner, clock, i18n helpers, security primitives | imported by all contexts |
| `channels` | Industry/channel registry | `industries`, theme tokens, locale set, disclaimers, channel enablement | `ThemePort` (read DTOs) |
| `sources` | Feed catalog and fetch health | `sources`, fetch state (etag/last_modified/status) | `SourceHealthPort` |
| `articles` | Ingestion, scoring, dedupe, summaries, retention, search | `articles`, `topics`, `article_topics`, `pins`, `refresh_runs` | `ArticleQueryPort`, `ArticleEvents` |
| `publishing` | Public read surface | read DTOs, cursor encoding, cache policy, contact messages, sitemaps | HTTP `/v1` |
| `editorial` | Admin surface | `api_keys`, `audit_events`, admin sessions, moderation commands | HTTP `/v1/admin` |
| `web` (Next.js) | Public UI | pages, theming render, SEO, locale switch | calls `/v1` server-side |

**Dependency direction (binding):**

```
web ──HTTP──▶ publishing ──▶ articles/channels/sources (ports)
editorial ──HTTP──▶ articles/channels/sources (ports)
articles ──▶ sources.ports, channels.ports, platform
channels/sources ──▶ platform only
```

Rules: no context imports another context's `infrastructure/` or `http/`; cross-context data flows through `ports/` DTOs or events; `platform` imports nothing from contexts.

---

## 3. Highest-risk path

**Public article read + channel isolation.** A wrong filter or a stale cache can show one industry's article on another channel, or serve hidden/expired content - visible, trust-damaging, and potentially legal-sensitive.

- **Read path:** request → locale/tz negotiation → `publishing` query → `articles.ArticleQueryPort` (filters: `industry_id`, `status = published`, `published_at >= now - retention`) → DTO → cache (ETag + TTL) → response.
- **Invariants:** every article row has exactly one `industry_id`; hidden/expired items never enter a response; cached entries are keyed by `(industry, locale, query, cursor)`.
- **Idempotency:** ingestion upserts by `canonical_url`; refresh runs are single-flight via a Redis lock; re-running publishes nothing twice.
- **Callbacks/polling:** outbound feed polling only; no inbound webhooks in v1.

---

## 4. Data model and ownership

| Table | Owner | Key columns | Notes |
|-------|-------|-------------|-------|
| `industries` | channels | `id`, `slug` UNIQUE, `code`, `name`, `theme` JSONB, `locales` TEXT[], `disclaimers` JSONB, `enabled` | Seed from `data.json` |
| `industry_locales` | channels | `industry_id`, `locale`, `name`, `tagline` | Optional per-locale copy |
| `sources` | sources | `id`, `industry_id`, `name`, `feed_url`, `language`, `trust` NUMERIC(3,2), `enabled`, `last_fetched_at`, `etag`, `last_modified`, `status` | `feed_url` UNIQUE per industry |
| `topics` | articles | `id`, `industry_id`, `slug`, `label` JSONB, `weight`, `keywords` JSONB | Keywords per locale |
| `articles` | articles | `id` UUID, `industry_id`, `source_id`, `canonical_url` UNIQUE, `title`, `summary`, `language`, `published_at`, `fetched_at`, `score`, `corroboration`, `verification`, `status`, `summary_source`, `summary_language`, `summary_version`, `search_vector` | `summary_language = language`; `search_vector` generated tsvector (title + summary) |
| `article_topics` | articles | `article_id`, `topic_id` | M:N |
| `pins` | articles | `article_id`, `industry_id`, `position`, `weight` | Editorial override |
| `api_keys` | editorial | `id`, `label`, `key_hash`, `scopes` TEXT[], `rate_limit`, `enabled`, `last_used_at` | SHA-256 + pepper |
| `contact_messages` | publishing | `id`, `industry_id`, `name`, `email`, `phone`, `message`, `locale`, `status`, `created_at` | PII; 90-day retention |
| `partners` | publishing | `id`, `industry_id`, `name`, `contact_email`, `status`, `weight`, `regions` JSONB | Lead routing (ADR 013) |
| `leads` | publishing | `id`, `industry_id`, `partner_id`, `kind`, `name`, `email`, `phone`, `company`, `message`, `locale`, `source_page`, `article_id`, `utm` JSONB, `consent_version`, `consent_at`, `ip_hash`, `ua_hash`, `status`, `created_at`, `updated_at` | PII; 24-month retention |
| `lead_events` | publishing | `id`, `lead_id`, `actor`, `action`, `payload` JSONB, `created_at` | Append-only audit |
| `cta_events` | publishing | `id`, `industry_id`, `event`, `placement`, `article_id`, `locale`, `created_at`, `session_hash` | No PII; 90-day retention |
| `refresh_runs` | articles | `id`, `started_at`, `finished_at`, `status`, `stats` JSONB | Pipeline telemetry |
| `audit_events` | editorial | `id`, `actor`, `action`, `entity`, `entity_id`, `payload` JSONB, `created_at` | Append-only |

**Volumes:** articles **M** (10k-1M, 7-day hot window retained 30 days), sources/topics **K**, contact/leads **K/day**, CTA events **10K/day**, audit **K/day**. No PHI/FERPA/PCI payloads; see `.work/standards/20261105-data-classification.md`.

---

## 5. Non-functional requirements (quantified)

| ID | Area | Target | Basis |
|----|------|--------|-------|
| NFR-1 | API latency | p95 < 250 ms cached, < 600 ms uncached; p99 < 1.2 s | assumed baseline for content API |
| NFR-2 | Page performance | LCP p75 < 2.0 s; CLS < 0.1; INP < 200 ms | Core Web Vitals "good" |
| NFR-3 | Availability | 99.9% monthly; RPO 24 h; RTO 4 h | single-VPS posture |
| NFR-4 | Throughput | 1,000 req/min sustained per node; 10k feed items/day/channel ceiling | assumed |
| NFR-5 | Freshness | scheduled: new item visible ≤ 12 h (default cadence, `REFRESH_INTERVAL_MINUTES=720`); manual force: ≤ 60 s after run completes | ADR 010; configurable cadence |
| NFR-6 | Security | TLS 1.2+; HSTS; OWASP ASVS L2 intent; no secrets in repo | standard |
| NFR-7 | Privacy | no PII in logs; contact PII 90 days; export/erase on request | GDPR-style |
| NFR-8 | i18n | EN + ES complete; locale switch persisted; adding a locale ≤ 1 day | brief |
| NFR-9 | Accessibility | WCAG 2.2 AA | standard |
| NFR-10 | Cost | ≤ USD 40/month infra + `AI_MONTHLY_BUDGET_USD` AI cap (default 20) | assumption (HANDOFF O3) |
| NFR-11 | SEO | Lighthouse SEO ≥ 95; canonical + hreflang + JSON-LD on all public pages | standard |
| NFR-12 | Operability | one-command dev stack; migrations idempotent; restore drill documented | team size |

**Ratification:** all targets above were **owner-ratified on 2026-11-05**; later adjustments are recorded verbatim in this table.

---

## 6. Security summary

- **Trust boundaries:** browser → Caddy → web/API; API → Postgres/Redis; API → publisher feeds; API → AI provider.
- **Controls:** hashed API keys with scopes; Argon2id admin password + 15-min JWT; Redis rate limits; strict input validation (Pydantic); HTML sanitization + escaping; CSP; SSRF-safe fetcher; secrets via env only.
- **Threats and mitigations:** `.work/standards/20261105-threat-model.md` (T1-T12).
- **Data classes:** `.work/standards/20261105-data-classification.md`.
- **Backups:** nightly `pg_dump` to off-site object storage, 30-day retention, monthly restore drill.

---

## 7. Observability summary

Spec: `.work/standards/20261105-observability-spec.md`.

- **Metrics (namespaced):** `http_requests_total`, `http_request_duration_seconds`, `ingest_fetch_total{source,status}`, `ingest_lag_seconds`, `articles_scored_total`, `summaries_generated_total{locale,status}`, `cache_hits_total`, `rate_limited_total`, `db_pool_in_use`.
- **Logs:** JSON, one line per request (`request_id`, route, status, duration_ms) and per pipeline stage; never PII.
- **Traces:** OpenTelemetry spans for HTTP and refresh-run stages (optional in v1, cheap to add).
- **SLOs/alerts:** availability burn, p95 latency, stale channel (no success in 2 intervals), AI error rate, disk > 80%, backup age > 26 h.

---

## 8. Testing strategy

| Layer | Tooling | Gate |
|-------|---------|------|
| Unit (API) | `pytest`, `pytest-asyncio` | every PR |
| Contract (API) | `pytest` + `httpx.ASGITransport` snapshot tests of `/v1` responses | every PR |
| Integration (DB) | `testcontainers-postgres` or compose Postgres, migrations run twice | every PR |
| E2E (web) | Playwright (home, article, locale switch, contact) | milestone |
| Accessibility | axe-core in Playwright | milestone |
| Performance | k6 smoke (100 rps, 5 min) | pre-release |
| Security | dependency audit (`pip-audit`, `npm audit`), secret scan | every PR |

---

## 9. Repository layout

```
system-news/
├── apps/
│   ├── api/                      # Python 3.12 + FastAPI
│   │   ├── config/               # scoring.json, seeds.json, prompts
│   │   ├── migrations/           # numbered idempotent SQL
│   │   ├── scripts/              # one-off operational scripts
│   │   ├── src/news_api/
│   │   │   ├── main.py           # app factory + lifespan (migrations, clients)
│   │   │   ├── worker.py         # Redis Streams consumer + scheduler entrypoint
│   │   │   ├── cli.py            # admin CLI (refresh --force, status)
│   │   │   ├── platform/         # settings, db, cache, migrations, i18n, clock, security
│   │   │   ├── channels/        # domain, application, infrastructure, http, ports
│   │   │   ├── sources/
│   │   │   ├── articles/
│   │   │   ├── publishing/
│   │   │   └── editorial/
│   │   └── tests/{unit,integration,contract}
│   └── web/                      # Next.js 15 + React 19 + Tailwind 4
│       └── src/{app,components,lib,messages}
├── bin/                          # start.sh (dev stack control)
├── docs/                         # public API docs, integration guide
├── docker-compose.dev.yml
├── docker-compose.prd.yml
├── .work/                        # plans, SPECs, ADRs, standards, HANDOFF
├── DOCS_TECH_STACK.md
└── .cursorrules
```

Boundary rule enforced by review + import lint: `apps/api/src/news_api/<context>/domain` imports only stdlib + `platform`; no context imports another's `infrastructure`/`http`.

---

## 10. Recommended technology stack

| Layer | Choice | Pin | ADR |
|-------|--------|-----|-----|
| Backend | Python + FastAPI | 3.12 · fastapi 0.115.6 · uvicorn 0.34.0 | 001 |
| Validation | Pydantic | 2.10.5 | 001 |
| Database | PostgreSQL | 16-alpine | 002 |
| DB access | SQLAlchemy async + asyncpg | 2.0.x · 0.30.x | 002 |
| Cache / locks / rate limit | Redis | 7-alpine | 003 |
| Queue | Redis Streams (worker) | redis-py 5.x | 003 |
| Search | PostgreSQL full-text (`tsvector`) | built-in | 003 |
| Frontend | Next.js + React + Tailwind | 15.1.8 · 19.1.0 · 4.1.6 | 004 |
| i18n | Custom typed catalogs + middleware | in-repo | 007 |
| AI summaries | DeepSeek `deepseek-flash` (V4.1 Flash) | OpenAI-compatible API | 010 |
| Auth | API keys (public) + JWT (admin) | in-repo | 011 |
| Hosting | Single VPS + Docker Compose + Caddy | compose v2 | 005 |
| CI | GitHub Actions | - | 012 |

**Deferred:** object storage, dedicated search engine, managed cloud (UNKNOWNS U13-U15).

---

## 11. Foundation gate checklist

- [x] Docs 01-04 consistent and cross-linked
- [x] Registries seeded (`ASSUMPTIONS`, `RISK_REGISTRY`, `UNKNOWNS`)
- [x] High-risk SPECs drafted (news-api, ingestion-pipeline, industry-sites, editorial-console)
- [x] `DOCS_TECH_STACK.md` pins versions
- [x] Directory map updated (`.work/standards/20261105-DIRECTORY_MAP.md`)
- [x] No application code required for **plan-master-ready** (skeleton starts after certify)
- [x] ADRs 001-012 Decided (owner ratification of O1-O3 tracked in HANDOFF)
- [x] NFRs quantified (§5) and data model drafted (§4)
- [x] Threat model + data classification + observability + API guide exist
- [x] Personas documented
- [x] No unresolved architectural contradictions

---

## 12. ADR register

| ADR | Topic | Status |
|-----|-------|--------|
| 001 | Backend stack (Python + FastAPI) | Decided |
| 002 | Primary database (PostgreSQL 16) | Decided |
| 003 | Supporting data services (Redis + Postgres FTS) | Decided |
| 004 | Frontend (Next.js 15 + Tailwind 4) | Decided |
| 005 | Hosting and deployment (VPS + Compose + Caddy) | Decided |
| 006 | Tenancy and channel model (single deployment, multi-channel) | Decided |
| 007 | Internationalization (EN unprefixed, `/es`, language-partitioned content) | Decided |
| 008 | Public API contract and versioning | Decided |
| 009 | Industry theming model | Decided |
| 010 | Ingestion and AI summary pipeline | Decided |
| 011 | Auth and access control | Decided |
| 012 | CI/CD and release flow | Decided |
| 013 | Lead capture and CTA architecture | Decided |

**Rule:** ADR headers win on conflict with this register.

---

## 13. Explicit deferrals

| Item | Deferred to | Owner | Trigger |
|------|-------------|-------|---------|
| Dedicated search engine | Phase B | eng | > 100k articles |
| Object storage / CDN | Phase B | eng | media feature |
| Webhooks / push API | Phase B | eng | client request |
| Newsletter | Phase B | owner | retention goal |
| Managed cloud / multi-node | post-GA | owner | > 100k daily sessions |
| MFA for admin | post-GA | owner | multi-editor team |

---

## 14. Next action

`@plan-foundation certify plan-master-ready` (after owner ratification of O1-O3 in HANDOFF) - or run it now; ratification is a review action, not a certification blocker.
