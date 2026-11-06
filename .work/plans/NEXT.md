# NEXT - planning backlog

**Updated:** 2026-11-06 (M9 complete)

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
| Lead-gen rungs | migration 010 `question`/`asset` lead kinds + 3 funnel events; ask-one-question rung; asset waitlist; briefs archive; topic hubs; UTM capture; disposable-domain rejection |
| Funnel read-out | `GET /v1/admin/funnel` + admin tab; OpenAPI snapshot; contract tests |
| Offer + feasibility | `.work.biz/strategy/20261105-offer-and-leadgen-brief.md` and `20261105-product-feasibility-verification.md` |
| KEV digest scope | `.work.biz/plans/plan_kev-digest.md`: verdict, evidence (1,768 KEV rows, 6.6/week), MVP, 14-day test, kill criteria |
| M9 asset card test | `cta.asset` in channel config + migration 011, channel-config-driven card, one secondary rung, e2e rule, SPEC amendment 01 |
| Coverage balance repair | `skins.css` card clamp: energy 330px -> 85px, worst channel 178px vs the 260 gate |
| Plan v1.2 | M9 added to `.work/plans/full/20261105-full-plan.md` §19 + traceability row |

---

## Blocked on owner

| # | Item | Notes |
|---|------|-------|
| O5 | Answer U1-U12 | brand/domain, publisher portfolio, pilot, analytics, traffic |

---

## Recommended next

| Priority | Item | Notes |
|----------|------|-------|
| **0** | Read the 14-day asset test | window opened 2026-11-06, closes **2026-11-20**; `asset_interest` events vs CTA impressions from `/v1/admin/funnel`, against the pre-registered rule in `.work.biz/plans/plan_kev-digest.md` §11 |
| **1** | Name the digest reviewer (D-005) | the generator cannot publish an issue without a named signer |
| **2** | New-channel content coverage | manufacturing EN 10, retail ES 1; add EN feeds/broaden topics before launch |
| **3** | `@ui-component-build plan - S1` | contact, about, admin screens on the shipped primitives |
| **4** | Verify pending implementations | k6, prd deploy/rollback, remote CI, production image smoke |
| **5** | U9/U10 decisions | analytics/consent, traffic sizing (U8 closed: pilo-mail chosen, deferred) |

---

## Current iteration - M9: asset card test (post-v1 operator scope)

**Milestone ref:** M9 · `.work/plans/full/20261105-full-plan.md` §19 (added v1.2, 2026-11-06). Origin: D-003…D-006 in `.work.biz/plans/plan_kev-digest.md` §15.
**Status:** complete 2026-11-06 — milestone verify pass with gaps (gaps closed the same day)
**Started:** 2026-11-06
**Source of truth for scope:** `.work.biz/plans/plan_kev-digest.md` §11 (14-day card test)

### In scope
- enable the cybersecurity KEV digest card on the cybersecurity channel (home + article), both locales, as a waitlist with no send-date promise
- make the asset registry channel-keyed instead of a hardcoded legal slug
- e2e assertions for three channels (cybersecurity has a card, education does not, legal still does)
- pre-register the 14-day measurement window and its decision rule before any result exists

### Out of scope (explicit)
- any digest generator, KEV/NVD adapter, migration, API endpoint, or issue page (gated behind the card test passing)
- email delivery (D-002 defers `pilo-mail`)
- the legal card's copy or behaviour
- channel-inventory regeneration beyond what `./bin/start.sh test` already enforces

### Tasks
| ID | Description | Files | Status | Notes |
|----|-------------|-------|--------|-------|
| M9-T1 | Asset card resolved from channel config, copy in catalogs | `apps/web/src/lib/assets.ts`, `apps/web/src/lib/api.ts`, `apps/web/src/messages/en.json`, `apps/web/src/messages/es.json`, `apps/web/src/app/[locale]/[industry]/page.tsx`, `apps/web/src/app/[locale]/[industry]/article/[id]/page.tsx` | done | S. File list expanded during the task: copy moved to `messages/{en,es}.json` per CONVENTIONS §10. SC1: (1) drift = the two message catalogs, now declared; (2) 3-month failure = a renamed key renders the raw key string, because `t()` falls back to the key — covered by the new e2e heading assertions; (3) assumed `AssetOffer` props unchanged, re-read this session; (4) yes, e2e asserts exact copy for both assets; (5) 0 lint/type warnings |
| M9-T2 | E2E coverage for the card across channels | `apps/web/e2e/public.spec.ts` | done | S. SC1: (1) no drift; (2) failure = running against `next dev` times out on cold compile (observed twice), e2e must run on a production build; (3) assumed `playwright.config.ts` baseURL, re-read; (4) the test is the coverage; (5) 0 warnings |
| M9-T3 | Pre-register the 14-day test window | `.work.biz/plans/plan_kev-digest.md` | done | S. SC1: (1) no drift; (2) failure = a 0 denominator read as 0% — the rule says report `unknown`; (3) assumed `/v1/admin/funnel` exposes channel impressions, verified earlier this session; (4) n-a, documentation; (5) 0 warnings |
| M9-T4 | `cta.asset` in profiles + idempotent seed | `apps/api/config/deployments/legal.json`, `apps/api/config/deployments/cybersecurity.json`, `apps/api/migrations/011_seed_asset_offers.sql`, `apps/api/tests/contract/test_bundle.py` | done | S. Gap-fix for R16 (D-009). SC1: (1) no drift; (2) failure = a profile apply overwriting an operator's asset choice — the seed uses `cta -> 'asset' IS NULL` and apply-profile reports `skipped`; (3) assumed `apply.py` reconciles `cta`, re-read at `implementation/apply.py:179`; (4) contract test asserts `cta.asset`; (5) 0 warnings |
| M9-T5 | One secondary rung: asset replaces the brief signup | `apps/web/src/app/[locale]/[industry]/page.tsx`, `apps/web/src/app/[locale]/[industry]/article/[id]/page.tsx`, `apps/web/e2e/public.spec.ts`, `.work/features/industry-sites/20261106-SPEC-amendment-01.md` | done | S. Gap-fix for the three-asks finding (D-008). SC1: (1) no drift beyond the SPEC amendment, now declared; (2) failure = a channel that sets `cta.asset` to a slug missing from the registry loses both rungs silently — the card is the only rung there; e2e covers the two real channels, a future typo would need the same assertion; (3) assumed `channel.cta` reaches the page for every channel, verified via `/v1/news/bundle`; (4) yes, `#brief-signup` count assertions; (5) 0 warnings |
| M9-T6 | Fix the energy coverage imbalance (repair) | `apps/web/src/app/skins.css` | done | S. code-repair from milestone. SC1: (1) no drift beyond the stylesheet, declared; (2) failure = a clamp that hides a real excerpt on a narrow desktop — 3 lines at 768px is the floor, mobile keeps full text; (3) assumed the card body is a direct `<p>` child, verified in `StoryCard.tsx:45`; (4) layout.spec.ts:31 is the test; (5) 0 warnings |

### Acceptance criteria
- [x] the KEV card renders on the cybersecurity channel home and article, EN and ES (curl + e2e)
- [x] no card copy promises a send date ("when the first issue is ready" only)
- [x] the legal card renders exactly as today (e2e `/legal`)
- [x] e2e covers render / absence / unchanged on three channels
- [x] measurement window and decision rule recorded before any result is read

### Validation steps
- [x] `pnpm lint && pnpm typecheck && pnpm check` → clean, 310 catalog keys, 10/10 contrast
- [x] `pnpm build`, then the full Playwright suite on the production server → **58 passed, 1 skipped** (admin sign-in needs `E2E_ADMIN_PASSWORD`)
- [x] `./bin/start.sh --env dev test` → api 111 passed (ruff/format/mypy clean), web lint/type/check clean, inventory ok
- [x] migration `011_seed_asset_offers.sql` → `applied: 1`, re-run `applied: 0`; `apply-profile` for legal + cybersecurity reports `skipped` (profile matches DB)
- [x] re-verified 2026-11-06: full Playwright on a production build → **59 passed, 1 skipped, 0 failed** (after the coverage-balance repair)
- [x] manual: `/cybersecurity`, `/es/cybersecurity`, article, `/education` (absent), `/legal` (unchanged)

### Owner blockers
- none for the card test. D-005 (named reviewer) gates the generator, not the card.
- ~~**plan traceability (waived)**~~ resolved 2026-11-06: M9 is now a `§19` row in the master plan (v1.2); the waiver line in `.work/context/HANDOFF.md:26` can be retired at close.
- ~~**SPEC ambiguity (R16)**~~ resolved 2026-11-06 by D-009 (`.work.biz/decisions/DECISIONS.md:30`): the asset a channel offers is `cta.asset` in channel config; D-007 superseded.
- ~~**Open failure, not caused by M9:** energy coverage balance (330px vs 260)~~ **repaired 2026-11-06** (M9-T6): coverage card excerpts clamp to three lines at >=768px; measured spreads now max 178px across ten channels, gate unchanged.

### Concept / NFR registry (this iteration)
| Concept id | Applies | Status | Evidence / trigger |
|------------|---------|--------|-------------------|
| MOD-01 | no | n-a | a registry lookup change; no service split or module boundary moves |
| MOD-02 | no | n-a | no new network hop or synchronous chain |
| MOD-03 | no | n-a | no new infrastructure line item |
| MOD-04 | no | n-a | no new operational surface |
| MOD-05 | no | n-a | no deployable/architecture choice |
| MOD-06 | **yes** | done (output due before `complete`) | agent-authored diff touching 5 files; blast radius is two page renderings, reversible in one commit; reviewable by diff |
| MOD-07 | no | n-a | no prompt composition change |
| MOD-08 | no | n-a | no IaC change |

### Cross-LLM verification
- Triggered: no — four-file UI change with e2e coverage

### Done this iteration
| Task | Completed | Notes |
|------|-----------|-------|
| M9-T1 | 2026-11-06 | `assets.ts` now carries `channel` + message keys; `assetForChannel(slug)`; both pages resolve by channel; `cybersecurity-kev-digest` waitlist card with EN/ES copy in `messages/*.json` |
| M9-T2 | 2026-11-06 | one e2e test covering cyber home/article EN, cyber home ES, legal unchanged, education absent |
| M9-T3 | 2026-11-06 | 14-day window pre-registered in `plan_kev-digest.md` §11 (starts 2026-11-06, ends 2026-11-20) |
| M9-T4 | 2026-11-06 | `cta.asset` seeded by migration 011 + profiles; contract test asserts it; `/v1/news/bundle` exposes it for legal and cybersecurity only |
| M9-T5 | 2026-11-06 | brief rung suppressed where `cta.asset` is set; SPEC R16 amended; e2e asserts the rule on cybersecurity, legal, education, financial |
| M9-T6 | 2026-11-06 | coverage card excerpts clamp to 3 lines at >=768px; energy 330px -> 85px, worst channel 178px; layout gate unchanged |

---

### Concept / NFR registry - previous iteration (M1-M8, complete)



| Concept | Applies | Output |
|---------|---------|--------|
| MOD-06 (AI amplification) | yes - agent-authored diff | Provisioning now depends on its own ports (`provisioning/ports.py`) with a single composition root (`adapters.py`), so the importer has no context-infrastructure imports and is testable without a database (`tests/unit/test_apply_profile_ports.py`). Human arch review: satisfied by the port seam; remaining coupling is isolated to `adapters.py`. Blast radius: a wrong profile can misconfigure a channel's theme, sources, or partner routing; importer is idempotent and never deletes. `evidence: measured` (tests) |
| MOD-01 (coupling audit) | yes - crosses module boundaries | One adapter module per context, no direct infra imports from application code; adding a context means one adapter, not a refactor. `evidence: measured` (imports) |
