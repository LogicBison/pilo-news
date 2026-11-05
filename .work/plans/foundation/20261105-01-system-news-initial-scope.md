# System News - Initial exploration and scope

**Doc:** foundation **01** (P0 product intent) · **Created:** 2026-11-05
**What it is:** the canonical product-intent and scope record for System News; every later foundation artifact traces back here.
**Status:** Draft (2026-11-05) · **Needs:** owner review of the assumptions labelled *Unverified*, and answers to UNKNOWNS U1–U12.

## Audience and document purpose

| Layer | Audience | What they need |
|-------|----------|----------------|
| **Development** | Engineers and coding agents | Boundaries, invariants, capability list, explicit unknowns, testable success criteria |
| **Business / editorial** | Owner, editors | What ships in v1, which industries, what is deliberately excluded |
| **Shipped product** | End readers | Out of scope here - UX direction lives in `20261105-personas-v1.md` and the industry-sites SPEC |

**Terminology:** `{PLANS_ROOT}/foundation/` documents are **inputs** to plan-master. Doc 04 is the **architecture foundation**, not the master implementation plan (`*-full-plan.md`).

---

## Assumption ledger

### Founder intent (verbatim - P0 capture)

> ## URL:
> https://www.accidentinjurynews.com/
>
> ## CODE REFERENCE:
> copy same functionality from:
> /mnt/work/Projects/LogicBison
> And serve the contents through an API - this means eventually logicbison will be feeding from this centralized news site.
>
> ## IDEAL GOAL:
> to be able to deploy these sites for any of the industries supported by the system, as originally sourced from this list of industries:
> tmp/references/industries/data.json
>
> ## initial pointers:
> - Each news site/landing-page must be single-themed, and professionally suited (UI+UIX+SKIN+STYLING+CSS+LOOKS) for each specific industry
> - English and Spanish must be supported, default language on entry is the system's (browser's/environment's) setting, but can be changed manually by the user on a click. This must extensible to other languages.
> - API is mandatory in order to allow any sites to integrate: any client site should be able to integrate news functionality reliably and consistently, API documentation must be included for easy consumption and integration by developers and agentic coding assistants.

### Confirmed facts (repository evidence)

- The repo is a thin-client Agent OS workspace: `.cursorrules` (front-matter rules), `.work/` planning tree present; no application source yet (`apps/` absent).
- `tmp/references/landing-pages-n-news/url-sample-reference.md` contains the brief above and points at `https://www.accidentinjurynews.com/`.
- `tmp/references/landing-pages-n-news/url-sample-reference-image.png` shows the reference site: top nav (Home / About / News / Contact), search, contact form, long legal disclaimer block, cookie notice, sitemap link.
- `tmp/references/industries/data.json` is version **1.1.0** and defines **5** industries: `psychiatry_psychology`, `education_academics`, `legal_compliance`, `financial_banking`, `logistics_supply_chain`. Each carries `industryId`, `code`, compliance frameworks, terminology, custom fields, workflow states, and integrations.
- The reference implementation `/mnt/work/Projects/LogicBison` has a Python FastAPI API (`api/requirements.txt`: fastapi, uvicorn, pydantic, httpx) with a news aggregation module (`api/src/news/aggregator.py`, `summary.py`) and a Next.js 15 frontend (`frontend/package.json`) with `[locale]` routing and EN/ES content.
- `.gitignore` already anticipates `apps/web/.next` and `apps/api/.venv`, fixing the monorepo layout convention.
- No master plan exists yet (`.work/plans/full/` empty); plan-foundation is the correct entry point.

### Inferences (plausible, not proven)

- **A5/A6:** the project should reuse the reference implementation's stack (FastAPI + Next.js) to shorten delivery and reuse tested logic.
- **A7:** a durable relational store is needed because the product serves many channels and clients; the reference's JSON cache cannot support concurrent writers or ad-hoc queries.
- **A8:** Redis is needed for cache, refresh locks, and rate limiting at the API edge.
- **A9:** a single VPS with Docker Compose is the right v1 hosting posture; managed cloud is a scale-out option.
- **A10:** "multi-industry" means **multiple channels in one deployment**, not per-customer tenancy.
- **A12:** copyright-safe aggregation (headline + original short summary + link-out) is the only defensible default until each publisher's terms are reviewed.

### Unknowns (decide with stakeholders)

| # | Unknown | Impact |
|---|---------|--------|
| U1 | Final brand name | Domain, legal entity, all copy |
| U2 | URL shape (single domain with paths vs per-industry domains) | SEO, routing, Caddy |
| U5 | Which publishers per industry are contractually usable | Legal risk R1, source seeding |
| U6 | Which industry launches first | Editorial workload, first acceptance test |
| U7 | Editorial roles/review depth | Console scope |
| U9/U12 | Analytics/consent posture; sponsored placements | Privacy copy, content model |

Full register: `.work/plans/UNKNOWNS.md`.

---

## Product scope (v1)

### Product statement

System News is a **centralized news aggregation and publishing platform**. It ingests industry-relevant news from approved RSS/Atom sources, normalizes, scores, de-duplicates, and summarizes items (EN/ES), then serves them through (a) a themed, responsive landing-page/news site per industry and (b) a versioned public REST API that any client site can consume - LogicBison first.

### In scope (v1)

1. **Channel registry** for the 5 industries in `data.json`, each with theme tokens, display name, compliance disclaimers, and enabled locales.
2. **Ingestion pipeline**: scheduled feed polling, ETag/Last-Modified, parse/normalize, 7-day retention window, topic scoring, near-duplicate clustering, corroboration markers, manual pins.
3. **AI summaries**: per-article 2-4 sentence summary and a 5-line channel desk brief, EN and ES, generated only for new/changed items, fail-open.
4. **Public read API** `/v1`: industries, news list/detail, splash, topics, sources, search, sitemaps data; envelope + cursor pagination; cache headers; rate limits; OpenAPI at `/v1/openapi.json` and human docs at `/docs/api`.
5. **Industry sites**: `/{locale}/{industry}` home (splash + columns), article detail, about, contact; server-rendered, ISR-cached; per-industry skin; SEO metadata, JSON-LD, hreflang, sitemap.
6. **i18n**: English + Spanish UI and summaries; locale derived from browser `Accept-Language` on first visit, switchable in one click, persisted in a cookie; adding a locale is a data/catalog change, not a rewrite.
7. **Editorial console** (minimal): API-key management, source CRUD + enable/disable, pins, hide article, trigger refresh; audit trail.
8. **Contact form** per channel: validates, rate-limits, stores with 90-day retention, notifies by email.
9. **Operations**: Docker Compose dev/prd, `bin/start.sh`, numbered idempotent migrations, health endpoints, backups, restore runbook.

### Out of scope (v1)

- Full-text republication of third-party articles or images.
- User accounts, comments, newsletters, paywalls, subscriptions, payments.
- Per-customer tenancy / white-label deployments (single deployment, many channels).
- Native mobile apps.
- Dedicated search engine, object storage/CDN, multi-region.
- CMS-grade editorial workflow (approval chains, scheduling).
- Automated social posting.

### Success criteria (measurable)

| # | Criterion | Target | How measured |
|---|-----------|--------|--------------|
| S1 | Five channels live with distinct themes | 5/5 | Manual + screenshot review |
| S2 | EN and ES fully available for UI + summaries | 100% of UI keys; ≥ 95% of visible articles per channel have a summary in the active locale | CI catalog check + API coverage query |
| S3 | API contract usable by a third party without reading source | Docs + OpenAPI complete; a sample curl per endpoint | `docs/api` review; contract tests |
| S4 | Freshness | New item visible ≤ 15 min after feed publication (p95) | `ingest_lag_seconds` metric |
| S5 | Public API latency (stated as assumed target) | p95 < 250 ms cached / < 600 ms uncached; p99 < 1.2 s | Load test + prod metric |
| S6 | Availability | 99.9% monthly | Uptime check |
| S7 | Accessibility | WCAG 2.2 AA on home + article pages | axe audit, zero criticals |
| S8 | Core Web Vitals | LCP p75 < 2.0 s, CLS < 0.1, INP < 200 ms | Field data / Lighthouse CI |
| S9 | Copyright safety | No full article text stored; every item links to the publisher | Schema review + spot audit |
| S10 | Client integration | LogicBison can switch its news source to this API without UI changes | Integration test app |

---

## Personas (summary)

| Persona | Need | Primary surface |
|---------|------|-----------------|
| **Industry reader** | Trustworthy, current, skimmable news for their profession; language of choice | Industry site (home, article) |
| **Editor / operator** | Control sources, pin stories, hide bad items, see pipeline health | Editorial console |
| **Client developer / agent** | Stable contract, typed responses, examples, predictable errors | `/v1` API + `/docs/api` |
| **Site owner** | Add a new industry without redesigning the platform | Channel registry + theme tokens |

Full detail: `.work/plans/20261105-personas-v1.md`.

---

## Functional capabilities (C1-C8)

| ID | Capability | Bounded context | SPEC |
|----|------------|-----------------|------|
| C1 | Register and theme industry channels | `channels` | industry-sites |
| C2 | Manage feed sources and topics | `sources` | ingestion-pipeline, editorial-console |
| C3 | Ingest, normalize, score, dedupe, retain articles | `articles` | ingestion-pipeline |
| C4 | Generate and cache EN/ES summaries and desk briefs | `articles` | ingestion-pipeline |
| C5 | Serve public read API with caching, pagination, rate limits | `publishing` | news-api |
| C6 | Render per-industry landing pages, article pages, search | `web` (Next.js) | industry-sites |
| C7 | Administer sources, pins, hidden items, API keys | `editorial` | editorial-console |
| C8 | Capture contact messages with retention + notification | `publishing` | industry-sites |

---

## Data model (provisional - detail in doc 04 §4)

| Entity | Key fields | Sensitivity |
|--------|-----------|-------------|
| `industries` | slug, name, code, theme JSONB, locales, disclaimers, enabled | Public |
| `sources` | industry_id, name, feed_url, language, trust, enabled, last_fetched_at | Internal |
| `articles` | id, industry_id, source_id, canonical_url, title, summary, language, published_at, score, corroboration, status | Public |
| `topics` | industry_id, slug, label JSONB, weight, keywords JSONB | Public |
| `pins` | article_id, industry_id, position, weight | Internal |
| `api_keys` | label, key_hash, scopes, rate_limit, last_used_at | Restricted |
| `contact_messages` | industry_id, name, email, phone, message, locale, status | Confidential (PII) |
| `refresh_runs` | started_at, finished_at, status, stats JSONB | Internal |
| `audit_events` | actor, action, entity, entity_id, payload JSONB | Internal |

Volume class: **M rows** for articles (10k-1M total across channels; 7-day hot window), **K rows** for sources/topics/pins, **K rows/day** for contact messages. No PHI/FERPA/PCI data is ingested; industry compliance labels are editorial context only (see data-classification).

---

## Non-functional expectations (summary - quantified in doc 04 §5)

| Area | Requirement |
|------|-------------|
| Availability | 99.9% monthly; RPO 24 h; RTO 4 h |
| Performance | API p95 < 250 ms cached / < 600 ms uncached; LCP p75 < 2.0 s |
| Security | TLS 1.2+, OWASP ASVS L2 intent, no secrets in repo, hashed API keys |
| Privacy | No PII in logs; contact PII 90-day retention; GDPR-style erasure |
| i18n | EN + ES at launch; locale switch persisted; additive locales |
| a11y | WCAG 2.2 AA |
| Cost | ≤ USD 40/month infrastructure for v1 (assumption, HANDOFF O3) |

---

## Risks (top 6)

| ID | Risk | Mitigation |
|----|------|------------|
| R1 | Copyright exposure | Headline + original summary + link-out only; per-source ToS review; takedown path |
| R2 | AI hallucination | Constrained prompts, labels, editor hide, fail-open |
| R4 | Single-VPS SPOF | Nightly off-site backup; 4 h restore runbook |
| R5 | Feed breakage | Per-source health, stale-channel alert, manual seeds |
| R7 | Cross-channel leakage | `industry_id` on every read; isolation contract tests |
| R13 | Prompt injection | Feed content treated as data; no tool use in summarizer |

Full register: `.work/plans/RISK_REGISTRY.md`.

---

## Architecture directions (non-prescriptive - architecture foundation in doc 04)

These are directions, not decisions; binding choices live in ADRs and doc 04.

- **Modular monolith** in one FastAPI process + one worker process: simpler than microservices for a 1-3 person team, still bounded-context clean.
- **Postgres as source of truth**, Redis as ephemeral acceleration only; a cold Redis must never change correctness.
- **Read API shaped for consumers** (stable envelope, cursor pagination, ETags) - independent of the internal ingestion model.
- **Next.js server components + ISR** for public pages, calling the API server-side; no client-side data fetching for first paint.
- **Channel-as-data theming**: CSS custom properties generated from a channel's `theme` JSONB, so a new industry ships without a redesign.
- **Fail-open AI**: publication never depends on the model; missing summaries degrade to headline-only.

**Architecture foundation (doc 04):** `.work/plans/foundation/20261105-04-foundation-architecture.md` - bounded contexts, stack, repo layout, decisions register. **Not** the master implementation plan (`*-full-plan.md`).

---

## Traceability

| Artifact | Path |
|----------|------|
| Integration catalog | `.work/plans/foundation/20261105-02-integration-resources.md` |
| Product adjacency | `.work/plans/foundation/20261105-03-product-adjacency-phased-modules.md` |
| Architecture foundation | `.work/plans/foundation/20261105-04-foundation-architecture.md` |
| Registries | `.work/plans/ASSUMPTIONS.md`, `RISK_REGISTRY.md`, `UNKNOWNS.md` |
| Probe ledger | `.work/plans/foundation/PROBE_LEDGER.md` |
| Personas | `.work/plans/20261105-personas-v1.md` |
| Feature SPECs | `.work/features/*/20261105-SPEC.md` |

### Success-criteria traceability

| Goal | SPEC rule(s) | ADR | Verification |
|------|--------------|-----|--------------|
| S1 five themed channels | industry-sites R4-R6 | 009 | theme/contrast tests + visual review |
| S2 EN/ES completeness | industry-sites R3, ingestion R11/R15 | 007 | catalog CI + summary coverage query |
| S3 consumable API docs | news-api R15 | 008 | OpenAPI snapshot + docs review |
| S4 freshness ≤ 15 min | ingestion R1 | 010 | `ingest_lag_seconds` p95 |
| S5 API latency | news-api R9-R10 | 003, 008 | load test + p95 metric |
| S6 availability 99.9% | (ops) | 005 | uptime check, RTO drill |
| S7 WCAG 2.2 AA | industry-sites R13 | 004 | axe CI |
| S8 Core Web Vitals | industry-sites R9 | 004 | Lighthouse CI |
| S9 copyright safety | ingestion R14 | 010 | schema review + takedown drill |
| S10 LogicBison integration | news-api R15, R3-R4 | 008 | sandbox integration test |

## Next action

`@plan-foundation continue` (P1 gate review, then P2 ADR ratification) - owner review of U1-U12 is requested, not blocking.
