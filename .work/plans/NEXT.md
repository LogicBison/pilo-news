# NEXT - planning backlog

**Updated:** 2026-11-05

---

## Done

| Item | Artifact |
|------|----------|
| Foundation P0-P6 | `.work/plans/foundation/` docs 01-04 |
| Master plan v1.1 | `.work/plans/full/20261105-full-plan.md` |
| M1 scaffold + dev/prd stack | compose, Dockerfiles, `bin/start.sh` |
| M2 schema + channels | `apps/api/migrations/001-003`, `/v1/industries` |
| M3 ingestion | fetcher, normalizer, scoring, dedupe, worker, refresh, sources |
| M4 AI summaries | DeepSeek client, EN/ES prompts, desk briefs, caps, fail-open |
| M5 public API | news/list/detail/splash/bundle/topics/sources/contact/leads/CTA, ETags, keys |
| M6 industry sites | themes, EN/ES routes, SEO, fallback, contact, CTA, lead form |
| M7 editorial console | auth/CSRF, sources/topics/pins/hide, refresh, keys, audit, leads, partners, channels |
| M8 hardening | metrics, alerts, dashboards, runbooks, security review, backup/restore drill, launch checklist |
| Any-industry template | `POST /v1/admin/industries`, admin Channels tab, `docs/adding-an-industry.md`, verification doc |
| prd images | API + web production images build; API migrations/config verified |
| Volume backups | `./bin/start.sh backup/restore` - `.tar.gz` volume snapshots, no `pg_dump`; drill pass |
| Isolation | random host ports, `*-net` + internal `*-data` networks, DB/Redis not published |
| Verification | 77 API tests, ruff/mypy, web lint/type/build, 9/9 Playwright e2e + axe, OpenAPI snapshot |
| Session close 2026-11-05 | HANDOFF/NEXT current; commit + push |
| Deployment profile import | `apps/api/config/deployment.example.json`, `news_api.provisioning`, `apply-profile` CLI, `docs/deployment-profile.md`, 18 tests |
| Provisioning ports | `provisioning/ports.py` + `adapters.py`; no context-infrastructure imports; DB-free unit tests |
| Source quality policy | `sources/application/quality.py` + `verify-sources` CLI; 25/25 feeds pass; `docs/source-quality.md`; ADR 014 |
| Expanded feed portfolio | migrations 004-006: 25 enabled feeds, 4-5 per channel, EN+ES; stale WSJ feed disabled |
| Per-industry templates | `apps/api/config/deployments/*.json` (legal, financial, behavioral-health, education, logistics, cybersecurity) |
| Custom channel proof | `cybersecurity` and `stem-cell` served with zero code changes (profile only) |
| Instant industry switch | `SN_DEFAULT_INDUSTRY` read at request time; `./bin/start.sh industry <slug>`; verified swap legal<->financial |
| Material UI pass | elevation/surface tokens, sticky app bar, cards, chips, buttons, inputs; 6 channels pass contrast |
| Retention coherence | channel retention (30d) authoritative; global scoring cap aligned; migration 007 |
| Stem-cell channel | `config/deployments/stem-cell.json`: 6 verified feeds, 5 topics, 53 articles |
| Channel quick reference | `docs/guides/switching-channels.md`; linked from README |
| UI skin refresh brief | `.work/plans/20261105-ui-skin-refresh.md` with 14 reference sites |

---

## Blocked on owner

| # | Item | Notes |
|---|------|-------|
| O5 | Answer U1-U12 | brand/domain, publisher portfolio, pilot, analytics, traffic |

---

## Recommended next

| Priority | Item | Notes |
|----------|------|-------|
| **0** | Per-channel UI skin refresh | `@ui-design-foundation greenfield`, then specs; references in `.work/plans/20261105-ui-skin-refresh.md` |
| **1** | Verify pending implementations | k6, prd deploy/rollback, remote CI, production image smoke |
| **2** | U9/U8/U10 decisions | analytics/consent, email delivery, traffic sizing |
| **3** | Third content language | extension point documented in `docs/customization.md` §3 |

---

## Current iteration

*(Complete - M1-M8 + deployment profile import + source quality + two custom channels + material UI pass + channel quick reference. Next: per-channel UI skin refresh, then pending ops verification.)*

### Concept / NFR registry

| Concept | Applies | Output |
|---------|---------|--------|
| MOD-06 (AI amplification) | yes - agent-authored diff | Provisioning now depends on its own ports (`provisioning/ports.py`) with a single composition root (`adapters.py`), so the importer has no context-infrastructure imports and is testable without a database (`tests/unit/test_apply_profile_ports.py`). Human arch review: satisfied by the port seam; remaining coupling is isolated to `adapters.py`. Blast radius: a wrong profile can misconfigure a channel's theme, sources, or partner routing; importer is idempotent and never deletes. `evidence: measured` (tests) |
| MOD-01 (coupling audit) | yes - crosses module boundaries | One adapter module per context, no direct infra imports from application code; adding a context means one adapter, not a refactor. `evidence: measured` (imports) |
