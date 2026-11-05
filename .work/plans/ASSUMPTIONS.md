# ASSUMPTIONS - planning registry

**Updated:** 2026-11-05 · **Maintained by:** plan-foundation / plan-master

Label every entry: **Confirmed** | **Inference** | **Unverified** | **Rejected**

| ID | Assumption | Label | Source | Notes |
|----|------------|-------|--------|-------|
| A1 | System News is a centralized, multi-industry news + landing-page platform with a public API | Confirmed | `.work/plans/foundation/20261105-01-system-news-initial-scope.md` (Founder intent) | Quotes the reference brief verbatim |
| A2 | Five v1 industries: behavioral health, education, legal, financial, logistics | Confirmed | `tmp/references/industries/data.json` (v1.1.0, 5 entries) | Mirrored at `.work/docs/integration/industries-v1.1.0/data.json` |
| A3 | English and Spanish are required at launch; more locales must be additive | Confirmed | reference brief § initial pointers | ADR 007 |
| A4 | Client sites (e.g. LogicBison) consume news through the API, not scraped HTML | Confirmed | reference brief § CODE REFERENCE | ADR 008 |
| A5 | Python 3.12 + FastAPI backend matches the reference implementation and available skills | Confirmed | `/mnt/work/Projects/LogicBison/api/requirements.txt` (fastapi 0.115.6, uvicorn 0.34.0); owner approved 2026-11-05 | ADR 001 |
| A6 | Next.js + React frontend matches the reference implementation | Confirmed | `/mnt/work/Projects/LogicBison/frontend/package.json` (next 15.1.8, react 19.1.0); owner approved 2026-11-05 | ADR 004 |
| A7 | PostgreSQL 16 is required for durable sources/articles/API keys; a JSON cache is insufficient for a centralized service | Inference | Reference stores bundles in a JSON file; multi-industry API needs durable relational state | ADR 002 |
| A8 | Redis 7 is justified for cache, refresh locks, and rate limiting | Inference | NFR p95 targets + multi-client fan-out (doc 04 §5) | ADR 003 |
| A9 | Single VPS + Docker Compose is sufficient for v1; managed cloud is deferred | Confirmed | Sibling projects deploy with compose; owner approved 2026-11-05 | ADR 005 |
| A10 | One deployment serves multiple industry channels (not per-customer tenancy) | Inference | Product is one operator publishing many channels; no per-customer isolation requirement stated | ADR 006 |
| A11 | AI summaries use DeepSeek `deepseek-flash` (V4.1 Flash) over the OpenAI-compatible API and must fail open | Confirmed | Owner instruction 2026-11-05; DeepSeek model list | ADR 010; base `https://api.deepseek.com` |
| A12 | No full-text republication of third-party articles; headlines + short original summaries + link-out only | Inference | Copyright-safe default; not yet legal-reviewed | RISK R1 |
| A13 | Infrastructure budget ≤ USD 40/month for v1 | Confirmed | Owner approved 2026-11-05 | ADR 005 |
| A14 | Editorial team is 1-3 people at launch, so the console must be lightweight | Unverified | No staffing evidence | Personas v1 |
| A15 | Content is language-partitioned (one summary per article in its own language); no translation in v1 | Confirmed | Owner delegated the choice ("best recommendation"); ADR 007 | Revisit if Spanish coverage (R17) blocks launch |
| A16 | Refresh cadence is configurable and defaults to twice a day; manual force is always available | Confirmed | Owner instruction 2026-11-05 | ADR 010; `REFRESH_INTERVAL_MINUTES=720` |
| A17 | Lead generation is a primary business goal; every channel carries one primary CTA and a consent-based lead form | Confirmed | Owner instruction 2026-11-05 | ADR 013 |

## Rejected

| ID | Assumption | Reason |
|----|------------|--------|
| - | Per-customer schema-per-tenant isolation | There are no customer tenants; channels are rows in one deployment (ADR 006) |
| - | Copying LogicBison's JSON-file cache as the primary store | No durability, no cross-instance consistency, no query/search (ADR 002) |

## Review log

| Date | Reviewer | Action |
|------|----------|--------|
| 2026-11-05 | plan-foundation | Seeded from foundation doc 01 + probe ledger |
| 2026-11-05 | plan-foundation | A11/A15/A16 confirmed by owner direction; ADR-007/010 amended |
| 2026-11-05 | plan-foundation | A5/A6/A9/A13 confirmed: owner ratified ADRs, hosting budget, and NFR targets |

---

## Next action

None - reviewed at every gate; see `.work/plans/NEXT.md`.
