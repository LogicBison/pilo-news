# NEXT - planning backlog

**Updated:** 2026-11-05 (session close)

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
| UI foundation | `.work.ui/plans/foundation/01-04` + `tokens.json`; certified screen-spec-ready |
| Ten channel skins | `skins.ts` + `skins.css`: 4 hero variants, 3 balanced coverage rhythms, 10 motifs, 10 emblems |
| Per-channel photography | `apps/web/public/photos/*` + `credits.json`; `next/image` band + article strip |
| Distinct palettes | migration 009 + 3 profiles: 10 schemes incl. dark cybersecurity; 10/10 contrast |
| Lead magnet + qualification | `ProofStrip`, `TrustBlock`, `BriefSignup`; migration 008 qualification select |
| UI v2 editorial conversion | `.work.ui/inputs/references/` intake (3 lead-gen refs) + `editorial-conversion`; open/full-bleed layout, balanced CSS columns, clear filled forms; `e2e/layout.spec.ts` |
| UI v2 verification | production build; 57 e2e passed / 1 skipped; 80 pages 200 + zero overflow; layout 40/40; `pnpm lint/typecheck/check` green; token-lint 0 raw |
| UI direction + bind | `editorial-conversion` Approved 2026-11-05; composition tokens in `tokens.json` (84, schema-valid); 10 SPECs §13/§11 bound; `SCREEN_REFERENCE_MAP.md`; reference audit PASS |
| Three additional channels | `manufacturing`, `energy`, `retail` profiles applied to dev; Forge/Grid/Market skins; original SVG bands; 45/45 sources pass |
| Channel inventory | `docs/channel-inventory.md` generated from `/v1/industries`; `apps/web/scripts/channel-inventory.mjs` + `bin/channels.sh`; checked by `./bin/start.sh test` |
| Channel SPECs | 10 × `.work.ui/screens/channel-home-<slug>/` (all `Review`) |
| SPEC approval | Ten channel-home SPECs operator-approved 2026-11-05 (`Status: Approved`); unblocks component build |
| A11y milestone audit | `@ui-accessibility-audit milestone`: **pass** - 30 URLs, 0 critical/serious, 2 moderate best-practice findings, no waivers; report in `.work.ui/reports/20261105-accessibility-audit-milestone.md` |
| A11y fixes | F1 footer `nav.footer` label + F2 CTA `<aside>` -> `<section>`; re-scan 0 violations; F3 recorded in ten SPEC amendments |
| CATALOG | `.work.ui/design-system/CATALOG.md` rebuilt: 21 rows with token names, behavior source, APG pattern, states |
| S0 primitives | `apps/web/src/components/ui/`: button, card, chip, section-header, text-field, text-area, select-field, consent-field, field-error, trust-line; forms/trust/topic surfaces refactored onto them |
| Imagery | 10/10 photographic bands; retail, energy, manufacturing replaced SVG line-art with CC BY / BY-SA photos; `credits.json` + `.work.ui/reports/20261105-imagery-audit.md` |

---

## Blocked on owner

| # | Item | Notes |
|---|------|-------|
| O5 | Answer U1-U12 | brand/domain, publisher portfolio, pilot, analytics, traffic |

---

## Recommended next

| Priority | Item | Notes |
|----------|------|-------|
| **0** | New-channel content coverage | manufacturing EN 10, retail ES 1; add EN feeds/broaden topics before launch |
| **1** | `@ui-component-build plan - S1` | contact, about, admin screens on the shipped primitives |
| **2** | Verify pending implementations | k6, prd deploy/rollback, remote CI, production image smoke |
| **3** | U9/U10 decisions | analytics/consent, traffic sizing (U8 closed: pilo-mail chosen, deferred) |

---

## Current iteration

*(Complete - M1-M8, deployment profiles, source quality, ten channel skins, lead qualification, editorial-conversion v2, the three new channels, ten approved channel SPECs, the a11y milestone audit with F1/F2 fixes, the S0 catalog primitives, and photographic bands on all ten channels. Next: new-channel content coverage, then S1 screens; prd deploy/rollback and k6 remain.)*

### Concept / NFR registry

| Concept | Applies | Output |
|---------|---------|--------|
| MOD-06 (AI amplification) | yes - agent-authored diff | Provisioning now depends on its own ports (`provisioning/ports.py`) with a single composition root (`adapters.py`), so the importer has no context-infrastructure imports and is testable without a database (`tests/unit/test_apply_profile_ports.py`). Human arch review: satisfied by the port seam; remaining coupling is isolated to `adapters.py`. Blast radius: a wrong profile can misconfigure a channel's theme, sources, or partner routing; importer is idempotent and never deletes. `evidence: measured` (tests) |
| MOD-01 (coupling audit) | yes - crosses module boundaries | One adapter module per context, no direct infra imports from application code; adding a context means one adapter, not a refactor. `evidence: measured` (imports) |
