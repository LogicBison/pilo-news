# NEXT - planning backlog

**Updated:** 2026-11-06 (offer generation, public reference pages, lead/contact attribution; 143 API tests)

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
| Digital-tech topics (M10) | three topics on cybersecurity, `placement="topic"` attribution, migration 012 + unit test |
| Digital-technology channel (M11) | profile, `datacenter` skin + art + CC BY-SA photo, 6/6 grade-A feeds, 26 EN + 1 ES items |
| Channel inventory | `docs/channel-inventory.md` regenerated: **11 channels** |
| S1 screens | `contact`, `about`, `admin-console` implemented from approved SPECs; 80 Playwright tests pass on a production build with admin credentials |
| Channel RSS | `/{industry}/feed.xml` + `/es/...` (RSS 2.0, 40-item cap), discovery link in the channel head and a footer link; README + domain SPEC R1 updated |
| Form primitives a11y | `TextField`/`TextArea` moved the hint and error outside the label, so the accessible name is the label only |
| Funnel proxy fix | `api/proxy` returned a false 503 for every 204 (the write still happened); `cta-events` now answers 204 and stops logging failures |
| About copy fix | "seven-day window" replaced by "rolling window" in EN/ES — every channel runs 30-day retention and the API does not expose the value |
| Channel cadence (M12) | migration 013 (`fetch_interval_minutes`, `auto_fetch_enabled`); scheduler override + pause; admin API + Channels tab controls |
| Free-offer controls (M12) | `industries.offers` for consultation/brief/question/asset; legacy-compatible defaults; brief/asset exclusivity enforced; public payload carries effective offers |
| Offer rendering (M12) | every public page renders only active offers; CTA links no longer point at hidden sections |
| M12 docs + tests | SPEC `.work/features/channel-automation/20261106-SPEC.md`, OpenAPI snapshot, API 124 tests, 87 Playwright green, admin save verified end to end |

---

## Blocked on owner

| # | Item | Notes |
|---|------|-------|
| O5 | Answer U1-U12 | brand/domain, publisher portfolio, pilot, analytics, traffic |

---

## Recommended next

| Priority | Item | Notes |
|----------|------|-------|
| **0** | Read the digital-technology window | closes **2026-11-27**; topic placements (`placement="topic"`) + channel inquiries against the rule in `.work.biz/plans/plan_digital-technology-channel.md` §11 (D-014 keep/kill) |
| **1** | Read the 14-day asset test | closes **2026-11-20**; `asset_interest` vs CTA impressions per `plan_kev-digest.md` §11 |
| **1b** | Name the digest reviewer (D-005) | the generator cannot publish an issue without a named signer |
| **2** | Channel content refresh | coverage is real in both locales (lowest digital-technology ES 16); the stale "EN 10 / ES 1" notes are retired |
| **3** | UI S4 SPECs + P1 primitives | `search`, `privacy`, `terms`; `Skeleton`, `Toc` |
| **4** | Verify pending implementations | k6, prd deploy/rollback, remote CI, production image smoke |
| **5** | U9/U10 decisions | analytics/consent, traffic sizing (U8 closed: pilo-mail chosen, deferred) |

---

## Completed iteration - M14: lead and contact attribution (2026-11-06)

**Milestone ref:** `.work/features/lead-attribution/20261106-SPEC.md`
**Status:** complete 2026-11-06 - 5/5 tasks
**Started:** 2026-11-06

### In scope
- contact attribution parity: source page, UTM, hashed IP/UA, country, session hash
- leads: country and session hash, normalized UTM
- country only from a configured trusted edge header
- admin Contacts tab with list, status, and DSAR erase
- privacy copy updated; raw IP still never stored

### Out of scope
- raw IP storage or IP geolocation
- marketing consent change; contact consent remains an owner/legal decision
- cross-device identity
- paid data enrichment

### Tasks
| ID | Description | Status |
|----|-------------|--------|
| M14-T1 | Migration 015 + UTM normalizer + country helper | done |
| M14-T2 | Lead and contact writers accept attribution | done |
| M14-T3 | Admin contacts API + Contacts tab | done |
| M14-T4 | Forms send session hash; contact sends source/UTM | done |
| M14-T5 | Privacy copy + tests/docs | done |

### Verification
- `./bin/start.sh --env dev test` -> api **143 passed**, web checks green (415 keys, 11/11 contrast)
- admin e2e **7/7**, including Contacts
- migration 015 applied; contact/lead attribution tests assert country, normalized UTM, hashed session
- production build passes

### Residual
- `GEO_COUNTRY_HEADER` is empty by default; country stays blank until the edge overwrites a configured header.
- Contact consent for marketing is not changed; that remains an owner/legal decision.
- No raw IP is stored, by design.

---

## Completed iteration - M13: offer issue generation (2026-11-06)

**Milestone ref:** `.work/features/offer-generation/20261106-SPEC.md`
**Status:** complete 2026-11-06 - 9/9 tasks
**Started:** 2026-11-06

### In scope
- US-first jurisdiction policy; scope is explicit on every issue
- `offer_issues` storage (migration 014)
- generic builder: fetch, normalize, AI draft with fallback, validate, persist draft
- Federal Register (legal, US) and CISA KEV (cybersecurity, global) adapters
- automatic draft generation from the worker scheduler
- CLI + admin read/build/publish API; public reference pages; no email

### Out of scope (explicit)
- email delivery, double opt-in, unsubscribe
- the actual editorial review work (the gate exists; a human still has to read)
- EU/Asia adapters
- the other six reference offers

### Tasks
| ID | Description | Files | Status | Notes |
|----|-------------|-------|--------|-------|
| M13-T1 | Jurisdiction policy + storage | `migrations/014_offer_issues.sql`, `offers/domain/*`, SPEC §2 | done | US for Federal Register, global for KEV |
| M13-T2 | Source adapters | `offers/infrastructure/{federal_register,kev,fetch,adapters}.py` | done | fixtures cover parsing; live dry-runs pass |
| M13-T3 | AI draft + fallback | `offers/application/draft.py`, `AiClient.complete_json` | done | 8k token cap; fallback on invalid JSON |
| M13-T4 | Builder + repo | `offers/application/build.py`, `offers/infrastructure/repo.py` | done | idempotent per date; empty/failed states |
| M13-T5 | Automatic scheduler + worker | `offers/application/scheduler.py`, `worker.py`, `queue.py` | done | queued via the existing stream; never publishes |
| M13-T6 | CLI + admin API + tests/docs | `cli.py`, `offers/http/routes.py`, `bin/offers.sh`, docs, tests | done | `offer build/list/show/publish/unpublish`; 139 API tests |
| M13-T7 | Admin Offers tab | `AdminConsole.tsx`, messages, e2e | done | list, expand rows, build now, publish/unpublish |
| M13-T8 | Reviewer-gated publish + public API | `offers/http/routes.py`, `offers/http/public.py`, `repo.py`, CLI | done | publish requires reviewer; unpublished 404 |
| M13-T9 | Public reference pages | `app/[locale]/[industry]/references/**`, asset card, sitemap | done | list/detail, EN content on ES with notice; channel card links |

### Acceptance criteria
- [x] a legal issue can be generated from Federal Register and stored as a draft
- [x] a cybersecurity issue can be generated from CISA KEV and stored as a draft
- [x] the worker queues due offers automatically; no duplicate issue per date
- [x] every issue carries an explicit scope; no `US + EU` claim in v1
- [x] publish is reviewer-gated and public; email is not built
- [x] migration idempotent; full checks green

### Verification
- `./bin/start.sh --env dev test` -> api 139 passed, ruff/format/mypy clean; web checks green
- live dry-runs: legal 12 rows, cyber 12 rows, both `drafted_by=ai`
- live drafts: legal `2026-11-03`, cyber `2026-11-04`
- admin API: list, detail, dry-run 200, queued 202
- worker restart clean with the offer scheduler

### Residual risks
- reviewer sign-off, publish, and email are not built
- EU/Asia are not built; the next jurisdiction is a new adapter and scope
- live link checking of every row is a publish-gate task, not a build-gate task
- AI can return invalid JSON; the builder falls back to source rows rather than failing the issue

---

## Completed iteration - M12: channel automation and free-offer controls (2026-11-06)

**Milestone ref:** `.work/features/channel-automation/20261106-SPEC.md`
**Status:** complete 2026-11-06 - 5/5 tasks
**Started:** 2026-11-06

### In scope
- per-channel fetch cadence that overrides `REFRESH_INTERVAL_MINUTES` when set
- automatic-fetch pause per channel; manual refresh stays available
- operator switches for the four free offers: consultation, weekly brief, ask-one-question, gated asset
- an intuitive Channels tab: deployment default, effective cadence, offers, inline editor
- public rendering that never links to a disabled offer

### Out of scope (explicit)
- per-source polling schedules (`sources.poll_interval_min` stays declarative)
- new offer kinds, new assets, or editing offer copy from the console
- editing the deployment default from the console
- weekly-brief delivery (U8)

### Tasks
| ID | Description | Files | Status | Notes |
|----|-------------|-------|--------|-------|
| M12-T1 | Schema + domain: nullable cadence, auto-fetch flag, offers map, defaults, validation | `migrations/013_channel_automation.sql`, `channels/domain/offers.py`, `theme.py` | done | idempotent migration applied twice (`applied: 0` on re-run) |
| M12-T2 | Scheduler honors the channel override and pause | `articles/application/queue.py` | done | unit tests cover override, default, pause, window |
| M12-T3 | Admin API + public effective offers | `editorial/http/industries.py`, `channels/http/routes.py`, `publishing/application/read_models.py` | done | validation rejects unknown keys, <5 min, brief+asset, asset without slug |
| M12-T4 | Intuitive Channels tab and web offer gating | `admin/AdminConsole.tsx`, channel pages, `CtaCard`, `Hero`, catalogs | done | save verified in a browser against the dev API; restored after the check |
| M12-T5 | Tests + docs + OpenAPI snapshot | API/web tests, `docs/api/*`, this file | done | 124 API tests; 87 Playwright production; `pnpm build` clean; final dev rerun had one navigation flake (passes in isolation) |

### Acceptance criteria
- [x] a set channel cadence wins over the deployment default
- [x] paused channels skip scheduled runs; manual refresh still works
- [x] at most one of brief/asset is active; asset requires `cta.asset`
- [x] public pages render only active offers and expose `offers` in the payload
- [x] admin shows the deployment default, the channel override, and the effective cadence
- [x] migration is idempotent; full checks green

### Verification
- `./bin/start.sh --env dev test` -> api 124 passed, ruff/format/mypy clean; web lint/type/check (364 keys, 11/11 contrast); inventory ok
- `pnpm build` -> production build passes
- Playwright on the production build -> **87 passed** (pre-polish); after the final hint/link edits the dev rerun was 84 passed / 2 flaky / 1 navigation flake that passes in isolation, with no offer-logic failure
- Browser save check: question offer off -> public `offers.question=false`; restored -> `true`

### Residual risks
- Scheduler override is proven by fake-clock unit tests, not by waiting for a live 12-hour tick.
- The web asset registry (`lib/assets.ts`) is not visible to the API; an unknown slug can be enabled in the admin but renders no card. Known channels use registry slugs.
- `auto_fetch_enabled=false` does not cancel an already-queued run.

---

## Completed iteration - M11: digital-technology channel

**Milestone ref:** M11 · `.work/plans/full/20261105-full-plan.md` §19 (v1.4, 2026-11-06). Scope: `.work.biz/plans/plan_digital-technology-channel.md` §4. Decisions: D-011 (name), D-013 (skin), D-014 (build now).
**Status:** complete 2026-11-06 — 6/6 tasks
**Started:** 2026-11-06

### In scope
- a live `digital-technology` channel: EN + ES, own theme, five topics, six graded feeds
- its own skin and art, or the GRID skin if no licensed photo clears
- a refreshed `docs/channel-inventory.md` (11 channels) that passes `--check`
- e2e, contrast, and full-suite coverage for the eleventh channel

### Out of scope (explicit)
- the asset card (`cta.asset`) — D-012 is open; a slug with no registry entry would silently drop the card
- partner routing and the readiness-review inquiry for this channel (U18)
- a second skin family; Asia sources; translation beyond EN/ES
- the keep/kill read-out itself (2026-11-27, M10 window)

### Tasks
| ID | Description | Files | Status | Notes |
|----|-------------|-------|--------|-------|
| M11-T1 | Profile: theme, locales, disclaimers, CTA, 5 topics, 6 sources | `apps/api/config/deployments/digital-technology.json` | done | M. violet-on-white theme (radius 2px, mono headings), 5 topics, 6 sources (4 EN + 2 ES), `cta.qualify` with three options, no `cta.asset`. Dry-run: 14 created, 0 warnings. SC1: (1) no drift, one new file; (2) failure = someone applies the profile expecting the site default to move — `default_industry` is reported, not written (`apply.py:121-131`); (3) assumed deployment-level fields are report-only, verified; (4) theme contrast is checked by my own ratios (min 5.19) and by the API on create (T3) — `pnpm check` cannot see an unapplied profile; (5) 0 warnings | M. square corners, mono headings; topics `ai-infrastructure`, `chips-supply`, `ai-rules`, `datacenter-power`, `platform-pricing`; 6 sources (4 EN + 2 ES) from the probed list; no `cta.asset` |
| M11-T2 | Skin `datacenter` + motif/scene + licensed photo + credit | `apps/web/src/lib/skins.ts`, `apps/web/public/skins/digital-technology/motif.svg`, `…/scene.svg`, `apps/web/public/photos/digital-technology/*`, `apps/web/public/photos/credits.json` | done | M. paths follow the channel, not the skin key (as energy/grid does). photo: Wikimedia Foundation servers, **CC BY-SA 3.0**, Victorgrigas, cropped to 1600×640 + 800×320, credit in `credits.json` and in the skin. SC1: (1) no drift beyond the asset directory name, declared; (2) failure = BY-SA share-alike on a cropped band — the in-page credit must stay rendered or the licence is breached (same risk the other four BY/BY-SA channels carry); (3) assumed `credits.json` needs a full-width JSON rewrite, verified by re-parsing (11 entries); (4) assets serve 200, but the skin's **visual render is unverified until the channel exists** — T3 confirms it; (5) 0 warnings |
| M11-T3 | Grade the feeds, apply, ingest to 14 items | `verify-sources`, `apply-profile`, `refresh` | done | M. **6/6 sources grade A**, 0 failures, 0 coverage warnings; applied (14 created), second apply 0 created / 0 updated; **26 EN + 1 ES** items on the first refresh. SC1: (1) no drift, config only; (2) failure = ES coverage stays at 1 until the Spanish feeds publish more — the channel is EN-heavy on day one, same as retail; (3) assumed the two ES feeds cover chips/AI, they are general technology; (4) `verify-sources` is the test; (5) 0 warnings |
| M11-T4 | Regenerate the channel inventory and prove it fresh | `docs/channel-inventory.md` | done | S. regenerated from the live API: **11 channels**, EN/ES URLs, default channel unchanged; `--check` green and it runs inside `./bin/start.sh test`. SC1: (1) no drift; (2) failure = the file is generated from the dev base, so a prd inventory needs its own regeneration (`ENV_FILE`/`APP_BASE_URL`); (3) assumed the generator enumerates `/v1/industries`, confirmed; (4) `--check` is the test; (5) 0 warnings |
| M11-T5 | Tests: 11 channels in the e2e loops, contrast, full suite | `apps/web/e2e/layout.spec.ts`, `apps/web/e2e/public.spec.ts` | done | S. slug added to the layout loop (4 tests) and a public test asserts the `datacenter` skin div, the brief rung, the absence of another channel's card, and the CC BY-SA credit. SC1: (1) drift = the public spec, declared; (2) failure = the test asserts a credit line that only exists because the photo needs it — if the photo is replaced with a CC0 file the assertion should drop with it; (3) assumed `data-skin` is on `<html>`, **wrong** — it is on the channel wrapper div, test fixed after the first run failed; (4) yes, the four assertions; (5) 1 self-inflicted test bug, fixed and re-run |
| M11-T6 | Docs: channel guide and README mention | `docs/guides/switching-channels.md`, `README.md` | done | S. channel added to the guide's current set and a `Live channels` row in the README. SC1: (1) no drift; (2) failure = the guide's list drifts again on the twelfth channel — the inventory file is the canonical list and the guide points to it; (3) assumed no other doc lists channels exhaustively, spot-checked `docs/`; (4) n-a, documentation; (5) 0 warnings |

### Acceptance criteria
- [ ] `/digital-technology` and `/es/digital-technology` return 200 with a bundle, sitemap lists both
- [ ] every enabled source grades A or B; zero coverage warnings
- [ ] `docs/channel-inventory.md` says 11 channels and `./bin/channels.sh --check` passes
- [ ] `pnpm check` passes contrast for 11 channels; layout + public + axe green
- [ ] ≥14 published items before the channel is enabled

### Validation steps
- [ ] `./bin/start.sh --env dev test`
- [ ] `docker compose --env-file .env.dev -f docker-compose.dev.yml exec api bash -c "cd /app && python -m news_api.cli verify-sources --industry digital-technology"`
- [ ] `./bin/channels.sh --check`
- [ ] full Playwright on a production build

### Owner blockers
- **D-013 (skin):** no answer yet. Default in this plan: new `datacenter` skin, GRID fallback if no licensed photo clears.
- **D-011 (name):** default "Digital Technology" / `digital-technology` / "Tecnología Digital".

### Concept / NFR registry (this iteration)
| Concept id | Applies | Status | Evidence / trigger |
|------------|---------|--------|-------------------|
| MOD-01 | no | n-a | a new channel is data; no boundary moves |
| MOD-02 | no | n-a | no new network hop (same API, same worker) |
| MOD-03 | **yes** | pending | one more channel polled on the existing cadence; measure first-week article count against the AI cap |
| MOD-04 | no | n-a | no new operational surface |
| MOD-05 | no | n-a | no deployable change |
| MOD-06 | **yes** | pending | agent-authored profile, skin, and test edits; blast radius is one channel page and the inventory |
| MOD-07 | no | n-a | no prompt change |
| MOD-08 | no | n-a | no IaC change |

### Cross-LLM verification
- Triggered: no — channel-as-data with existing gates

### Done this iteration
| Task | Completed | Notes |
|------|-----------|-------|
| M11-T1 | 2026-11-06 | profile written and validated (14 entities on dry-run) |
| M11-T2 | 2026-11-06 | `datacenter` skin, two SVGs, CC BY-SA photo with credit |
| M11-T3 | 2026-11-06 | 6/6 feeds grade A; applied; 26 EN + 1 ES items |
| M11-T4 | 2026-11-06 | inventory at 11 channels, `--check` green |
| M11-T5 | 2026-11-06 | 11 channels in the layout loop; skin/credit asserted |
| M11-T6 | 2026-11-06 | guide + README mention |

---

## Completed iteration - S1: contact, about, admin-console (2026-11-06)

**Milestone ref:** S1 · `.work.ui/plans/foundation/20261105-04-screen-map.md` (revised 2026-11-06) · SPECs under `.work.ui/screens/{contact,about,admin-console}/`.
**Status:** complete 2026-11-06 — 3/3 screens implemented and verified

### Tasks
| ID | Description | Files | Status |
|----|-------------|-------|--------|
| S1-T1 | Contact screen: config address, client validation, failure states with the desk email, success panel | `contact/page.tsx`, `ContactForm.tsx`, messages | done |
| S1-T2 | About screen: measure, rolling-window copy, brief suppression on `cta.asset` | `about/page.tsx`, messages | done |
| S1-T3 | Admin console: session states, APG tabs, inline hide/pin, confirmations, audit filter, default channel | `admin/AdminConsole.tsx`, `admin/page.tsx` | done |
| S1-T4 | Field primitives: error/hint outside the label; e2e + axe for the new screens | `ui/text-field.tsx`, `ui/text-area.tsx`, `e2e/*` | done |

### Verification
- `pnpm build` on the production bundle; `pnpm test` → **78 passed, 0 failed** (admin tests run with credentials).
- axe: 0 critical or serious on the 15 scanned URLs, including `/legal/contact`, `/es/legal/contact`, `/legal/about`, `/es/legal/about`, `/en/admin`.
- `pnpm check`: 328 catalog keys in EN and ES; 11/11 channels pass contrast.

---

## Completed iteration - M10: digital-technology topic test (2026-11-06)

**Milestone ref:** M10 · `.work/plans/full/20261105-full-plan.md` §19 (added v1.3, 2026-11-06). Source of scope: `.work.biz/plans/plan_digital-technology-channel.md` §11; decision D-010.
**Status:** complete 2026-11-06 — 4/4 tasks, window open to 2026-11-27
**Started:** 2026-11-06

### In scope
- three digital-technology topics on the cybersecurity profile, with EN/ES keywords and weights
- topic-page CTAs attributed as `placement="topic"` so the funnel read-out can answer the question
- a contract assertion that the topics are seeded
- the 21-day window and decision rule pre-registered before any result exists

### Out of scope (explicit)
- the `digital-technology` channel profile, its skin, art, or sources — **moved to M11 by D-014**; this iteration only measures
- any change to the other nine channels' topics
- new routes or components — topic hubs already ship
- the asset (`ai-rules-calendar`) and its reviewer

### Tasks
| ID | Description | Files | Status | Notes |
|----|-------------|-------|--------|-------|
| M10-T1 | Three topics on the cybersecurity profile | `apps/api/config/deployments/cybersecurity.json` | done | S. `ai-infrastructure` 1.3, `chips-supply` 1.25, `ai-rules` 1.2, EN/ES keywords; existing four untouched (apply #2: 0 created, 0 updated). SC1: (1) no drift, one file; (2) failure = a broad keyword (`datacenter`) pulls real-estate or utility stories into the cyber channel — the read-out is what catches it; (3) assumed the four existing topics keep their values, confirmed by the second apply reporting 0 updated; (4) keyword precision has no unit test; T4 records the read-out as the test; (5) 0 warnings |
| M10-T2 | Attribute topic-page CTAs | `apps/web/src/app/[locale]/[industry]/topic/[slug]/page.tsx`, `apps/web/src/components/CtaCard.tsx` | done | S. `"topic"` added to the CtaCard union; the page passes it; the brief rung keeps `brief-topic`. SC1: (1) drift = the union in `CtaCard.tsx` had to open up, now declared; (2) failure = a placement string is untyped at the analytics boundary, so a typo would silently create a funnel row — the union narrows it to compile time; (3) assumed `CtaButton` takes a plain string, verified at `Cta.tsx:18`; (4) no permanent test asserts the placement (the probe was removed) — coverage gap recorded here, T3 covers the topic seed not the placement; (5) 0 warnings |
| M10-T3 | Contract assertion for the seeded topics | `apps/api/tests/unit/test_digital_topics_profile.py`, `apps/api/migrations/012_seed_digital_technology_topics.sql` | done | S. **File list changed during the task:** the contract test cannot work — `cybersecurity` is not seeded into the test database (only the five 002 seeds are), so the bundle returns 404 there. Instead: migration 012 seeds the topics for every environment (idempotent via the unique slug constraint), and a unit test guards the profile so a topic cannot be dropped silently. SC1: (1) drift = migration + unit test instead of the contract file, declared; (2) failure = the migration and the profile carry the same topic data and can drift — the unit test pins the profile, nothing pins the SQL; (3) assumed the test DB runs migrations only, confirmed in `tests/conftest.py:52`; (4) yes, two unit assertions; (5) 1 ruff SIM300 fixed and re-gated |
| M10-T4 | Pre-register the 21-day window and rule | `.work.biz/plans/plan_digital-technology-channel.md`, `.work.biz/decisions/DECISIONS.md` | done | S. window **2026-11-06 → 2026-11-27**; denominator = CTA impressions with `placement="topic"` (or sessions when U10 lands); numerator = `cta_click` + `brief-topic` starts; rule retargeted from build/kill to keep/kill by **D-014**. SC1: (1) drift = the decisions ledger and the plan doc, declared; (2) failure = the window is read against a denominator that U10 may never supply — the rule names the fallback and marks the result `estimated`; (3) assumed the funnel keeps emitting `topic` rows, verified by the T2 probe; (4) n-a, documentation; (5) 0 warnings |

### Acceptance criteria
- [ ] `/cybersecurity/topic/ai-infrastructure`, `/chips-supply`, `/ai-rules` render in EN and ES (empty state is acceptable until stories match)
- [ ] `/v1/admin/funnel` reports a `topic` placement row
- [ ] `apply-profile --only-industry cybersecurity` is idempotent (second run: 0 created / 0 updated)
- [ ] the window and decision rule are written before any result is read

### Validation steps
- [x] `./bin/start.sh --env dev test` → api 113 passed, web checks, inventory ok
- [x] migration 012 applied (`applied: 1`), re-run `applied: 0`; cybersecurity bundle still returns 7 topics
- [ ] `docker compose --env-file .env.dev -f docker-compose.dev.yml exec api bash -c "cd /app && python -m news_api.cli apply-profile --file config/deployments/cybersecurity.json --only-industry cybersecurity --dry-run"`
- [ ] manual: the six topic URLs (3 topics × 2 locales) plus `/en/admin` funnel tab
- [x] full Playwright on a production build → 59 passed, 1 skipped (probe confirmed `placement: "topic"` on impression + click)
- [ ] playwright system libs: re-run `pnpm exec playwright install-deps chromium` after any container recreate — the Dockerfile.dev does not install them (found this session)

### Owner blockers
- **U10 (traffic baseline):** without sessions, the rule falls back to CTA impressions as the denominator; mark the result `estimated`.
- D-011/D-012/D-013 are not needed until the channel decision.

### Concept / NFR registry (this iteration)
| Concept id | Applies | Status | Evidence / trigger |
|------------|---------|--------|-------------------|
| MOD-01 | no | n-a | no boundary moves |
| MOD-02 | no | n-a | no new network hop |
| MOD-03 | no | n-a | no new line item |
| MOD-04 | no | n-a | no new operational surface |
| MOD-05 | no | n-a | no deployable change |
| MOD-06 | **yes** | pending | agent-authored one-line placement change + fixture data; blast radius is one CTA attribution string; tested by the funnel read-out |
| MOD-07 | no | n-a | no prompt change |
| MOD-08 | no | n-a | no IaC change |

### Cross-LLM verification
- Triggered: no — three-file change with a contract test

### Done this iteration
| Task | Completed | Notes |
|------|-----------|-------|
| M10-T1 | 2026-11-06 | three topics on the cybersecurity profile; applied and idempotent |
| M10-T2 | 2026-11-06 | topic CTAs report `placement="topic"` (probe-confirmed) |
| M10-T3 | 2026-11-06 | migration 012 seeds the topics; unit test pins the profile |
| M10-T4 | 2026-11-06 | 21-day window pre-registered; D-014 turns it into a keep/kill check |

---

## Completed iteration - M9: asset card test (2026-11-06)

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
