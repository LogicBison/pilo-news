# HANDOFF - session boundary

## Session status

**Closed:** 2026-11-10 — M15–M20 delivered and verified: brand surfaces, polite fetching, content fixes, source availability, acquisition, pipeline and quality. Gates at close: api **233 passed**, web **584 keys**, build **RC=0**, Playwright **124 passed / 0 failed / 5 skipped**, `verify-sources` **52/52**, migrations **017–020** applied. `3a2a8b2` (M19) was already on origin; M20 is in the close commit. Open owner lane: **O9** production TLS, **O15** `SMTP_FROM`, and the prd deploy itself.

**Open (2026-11-10, M20 shipped):** acquisition quality per the owner's "implement all 7": a `proprietary` source is now stored as headline + link only (no excerpt, no generated summary) at ingestion; discovery's overlap runs through Postgres `pg_trgm` with the token matcher as fallback; each source can issue an unguessable `/traffic/<token>` page showing its own 30-day items, clicks, requests and success rate; `candidates refresh` re-grades the queue without touching decisions; `sources health` adds `value_score` and retirement proposals; JSON Feed 1.x parses. 233 api tests, web build green. Uncommitted.

**Open (2026-11-10, M19 shipped):** the acquisition funnel gained its trail: `discover --save` fills a candidate queue, `candidates list/decide` records the call (never reopened by a later discovery), `source_fetch_stats` records attempts/successes/refusals/items/latency per source per day from the ingest path, `sources health` derives `success_rate_30d` and `avg_ms_30d` from it, `verify-sources` warns when a source's robots text changed since the last check, `sources export` prints OPML that `discover` reads back, and `sources report` names any desk missing a configured locale. Uncommitted.

**Open (2026-11-10, M18 shipped):** source acquisition built per the owner's "build the whole thing": `sources discover` grades a URL list or OPML (permission → quality → overlap → fit) without writing anything; `licence_type` and outreach are recorded per source and shown in admin; every outbound story link now goes through `/go/{id}` → `/v1/outbound/{id}`, which counts one click and 302s to the publisher (aggregate only, no reader identifier); `sources report`/`health` show the portfolio and return traffic. The two added primary feeds are kept (O17 answered). Uncommitted.

**Open (2026-11-10, M17 shipped):** source availability implemented per the owner's "implement all" instruction: `401`/`403` now produce `denied` with a seven-day cooldown, a `403` WAF body is classified `challenge`, robots redirects are followed and validated per hop, a permission ledger records state/hash/date/delay for every source, licensed feeds can carry credentials from the environment (never in the database), `verify-sources` gates the four-healthy-source availability floor, CISA News and SEC Press Releases were added, and `/bot` now explains allowlisting. The honest crawler UA is unchanged by design; a publisher-requested UA is a per-source header, not browser impersonation. Caddy keys were commented in all three env files at the owner's request and `env-sync verify` passes. Uncommitted.

**Open (2026-11-10, C+D verified):** the interrupted 2026-11-09 C+D session was resumed, verified and finished. Fetch safety (full plan **M16**) and the content fixes pass every gate: api **209 tests**, web lint/tsc/check **579 keys**, build **RC=0**, Playwright **124 passed / 0 failed / 5 skipped** on the production build, `hosts` all 14 invariants, `verify-sources` **50/50, 0 warnings**. Six defects were found while verifying and fixed: retail parser (bare `&`), financial below the 4-source minimum (Federal Reserve feed added), cooldown gauge not reset, admin Sources not rendering the new cooldown/last-error fields, the article-404 home link empty on channel hosts, and plan drift (NEXT said `pending`; the full plan had no M16). **Committed 2026-11-10 as `c6ce202`** (53 files: M15 brand surfaces + M16 fetch safety/content) and pushed to `origin/main`, with owner approval in the same message, after `@code-verify uncommitted` returned *pass with conditions* (blast radius high, acknowledged by the owner).

**Open:** 2026-11-09 - goal: proceed to implement all plans until all is full and complete (`@x-director`)

**Open (2026-11-09, M15 shipped):** brand surfaces implemented and verified end to end —
`@code-verify milestone - M15` verdict **pass with gaps**, `@code-implementation complete - M15`
run. Emblem/lockup/tile/favicon/icon/apple derived, masthead + footer marks wired, per-host icon
check green on dev (4 hosts), gates green (lint/tsc/check/build RC=0, **Playwright 120 passed /
0 failed / 5 skipped** on the production build, axe 0 critical/serious, CLS 0.0000 at 360/1440 px).
Full plan → **v1.7**. Next in this session: `.work/plans/20261109-next-improvement.md` Tracks **C**
(fetch safety, decision 1 answered) and **D** (content fixes D1–D5, D7–D10).
Changes are **uncommitted** — `@code-verify uncommitted` before any commit.

**Closed:** 2026-11-09 — `@x-director` plan-drift pass: M15 plans verified and corrected (full plan v1.6 gains the M15-T8 row and G1 `M15-T1..T8`; brand-assets plan header, tracked-art claim and derivation block fixed), derivation smoke-tested, MOD-06 → merge_ok. M15 implementation itself is still pending.

**Closed:** 2026-11-09 — four-request analysis, M15 planned and approved, apex responsive fix, READY TO IMPLEMENT.
Analysed the logo, the missing favicons, the fetcher's access posture and the generated content against the 2026-11-07 bundle (676 articles, 52 sources, 78 runs). Produced `.work/plans/20261109-next-improvement.md` (four tracks), `.work/features/fetch-safety/20261109-SPEC.md`, `.work.ui/plans/20261109-brand-assets.md`. Added **M15 brand surfaces** to the approved plan (v1.5, owner-approved 2026-11-09) and wrote the `## Current iteration` block. Fixed the owner-reported apex defects: the desk board kept three columns (languages dropped) and stopped clipping its last column at 1024-1440 px, and the masthead wraps under 720 px so a 390 px document no longer scrolls sideways. Verified: lobby e2e 13/13, layout 58 passed (1 flaky, green on retry), axe 29/29, lint/tsc/check/build clean.

**Closed:** 2026-11-07 — email through the pilo-mail gateway, a drilled dev→prd restore, the production stack on `169.58.4.85`, and the LogicBison credit.
Email leaves through `smtp.iterwire.com:2525` as `info@links.heraldfox.com`; a real message reached the owner's gmail with DKIM/DMARC pass. `init-env` now generates Postgres/Redis passwords, `preflight` resolves the email lane, the menu restore can apply config/media/nginx, and the bundle restored 11 channels / 676 articles / 52 sources into a clean Postgres 16. Production is up on `vmi3435240` with the data restored; HTTPS is the remaining step (the TLS template's duplicate session directives were found and fixed). Every public footer now carries the LogicBison mark and wordmark.

**Prior close — 2026-11-06:** offer generation, reviewer-gated public references, and lead/contact attribution.
Per-channel cadence and offer switches shipped; legal/cyber drafts generate automatically; public reference pages and publish/unpublish shipped; contact and lead attribution now store source/UTM/session/country with hashed network identifiers. 143 API tests, admin e2e 7/7, production build green. Remaining: email delivery, named reviewers, `GEO_COUNTRY_HEADER` edge value, and marketing-consent confirmation.

**2026-11-06 (channel automation):** the worker already fetched automatically on a
12-hour deployment default. Added a per-channel cadence that overrides it (`NULL` =
default), an automatic-fetch pause, and operator switches for the four free offers
(consultation, weekly brief, ask-one-question, gated asset). Migration 013; admin
Channels tab rewritten as a managed list with an inline editor; public pages render
only active offers. Verified: 124 API tests, 87 Playwright on a production build,
and a browser save/restore check against the dev API. SPEC:
`.work/features/channel-automation/20261106-SPEC.md`.

**Closed:** 2026-11-06 - S1 screens shipped: contact, about and admin-console implemented from approved SPECs. 80 Playwright tests pass on a production build (admin sign-in included); axe 0 critical/serious on 21 URLs; 329 catalog keys; 11/11 contrast. Every channel now publishes an RSS 2.0 feed in both locales. Along the way: the funnel proxy no longer returns a false 503 on 204, and the about page stopped claiming a seven-day window while every channel runs 30 days.

**Updated:** 2026-11-10

**Prior session (closed 2026-11-06):** eleven channels. M9 shipped config-driven asset cards and one secondary rung; M10 added the digital-technology demand test (three topics, `placement="topic"`, migration 012); M11 built the eleventh channel (`digital-technology`): its own `datacenter` skin with a CC BY-SA photo, six grade-A feeds, 26 EN + 1 ES items, and the channel inventory regenerated. 113 api tests; web checks; 64 Playwright passed / 1 skipped; 11/11 contrast.

**Prior session (closed 2026-11-05):** lead-generation offer rungs built after the UI close: ask-one-question and gated-asset leads (migration 010), funnel read-out + admin tab, UTM capture, briefs archive, topic hubs, disposable-domain rejection; plus the biz offer brief and the product-feasibility verification. 108 API tests; 57 e2e / 1 skipped on a production build; axe 0 violations on 11 URLs; build + lint + typecheck + check green.

**Prior session (closed 2026-11-05, earlier):** SPEC approvals, a11y milestone audit (+F1/F2), S0 catalog primitives, photographic bands on all ten channels. Then the earlier close: editorial-conversion v2 + ten channels + inventory/QA gates. 108 API tests; 57 e2e / 1 skipped; 40/40 layout; axe 11/11; 80 pages; 10/10 contrast. Ten SPECs in `Review`; visual verify **pass with gaps**.

## Fresh start - what the next session should do first

1. Run **`@session-control start`**.
2. Read `.cursorrules`, this file, `.work/plans/NEXT.md`.
3. ~~**Implement M15**~~ done 2026-11-09. ~~**Track C+D**~~ **done and verified 2026-11-10**
   (full plan **M16**): no plan work is open. Next is the owner lane — **O9** production TLS
   (`./bin/start.sh --env prd domains --write`, `nginx -t`, reload, `certs --check`, `hosts`),
   then the D-trial read of the next natural refresh.
4. **Apex:** the lobby lives in `apps/web/src/components/lobby/`; its copy is
   `.work.biz/strategy/20261107-lobby-copy.md` (140 keys, EN/ES). Change copy there
   first, then in `apps/web/src/messages/`.
5. After any channel add/remove: `./bin/channels.sh --write` and commit the inventory.
6. Re-run `python -m news_api.cli verify-sources --industry all` after any portfolio
   change; it must exit 0.
7. Still pending from M8: k6 (`tests/perf/k6-smoke.js`), remote CI, CATALOG init.
8. For launch: answer U1 brand, U9 analytics, U10 traffic, then run
   `.work/plans/operations/20261105-launch.md`.
9. **Deploy the footer credit:** `git pull` on the host, `./bin/start.sh --env prd up`,
   then check the channel, lobby and admin footers on the live hosts.

### Conditional reads

| If the task touches… | Read first |
|----------------------|------------|
| Any code or new feature | `.work/standards/20261105-CONVENTIONS.md`, `20261105-DIRECTORY_MAP.md` |
| Public API | `.work/standards/20261105-api-style-guide.md`, `docs/api/README.md` |
| Adding an industry | `docs/adding-an-industry.md` |
| Ingestion/AI | `.work/features/ingestion-pipeline/20261105-SPEC.md`, `apps/api/config/` |
| Web/UI | `.work/features/industry-sites/20261105-SPEC.md`, `apps/web/src/` |
| Backups/restore | `.work/plans/operations/20261105-backup-restore.md` |
| Security | `.work/standards/20261105-threat-model.md`, `20261105-data-classification.md` |
| Any prose/chat | `.work/voice/README.md` |

---

## Gate snapshot

| Phase | Status | Evidence |
|-------|--------|----------|
| P0-P6 foundation | done | docs 01-04, ADRs 001-013, SPECs, standards |
| M1 scaffold | done | compose dev/prd, Dockerfiles, `bin/start.sh` |
| M2 schema/channels | done | migrations 001-003 run twice; 5 channels |
| M3 ingestion | done | fixture tests + live feeds + worker scheduler + refresh runs |
| M4 AI summaries | done | DeepSeek `deepseek-flash`; 19 legal summaries stored; fail-open tested |
| M5 public API | done | contract tests, ETag/304, bundle/fallback, rate limits, leads |
| M6 sites | done | lint/type/build, Playwright public + axe, EN/ES routes |
| M7 console | done | auth/CSRF contract tests, sources/pins/keys/audit/leads |
| M8 hardening | done (prd deploy pending) | metrics/alerts/dashboards, runbooks, security review, backup drill |
| Any-industry template | done | create-channel endpoint + web + docs + tests |
| Isolation | done | random host ports; `*-net`/`*-data`; DB/Redis internal |
| Backups | done | volume archive + 2026-11-05 drill; pg_dump bundle drill 2026-11-07 |
| CI | written, not run on GitHub | `.github/workflows/ci.yml` |
| k6 / Lighthouse CI | scripts written, not run in prd | `tests/perf/k6-smoke.js` |
| prd deploy | stack up on 169.58.4.85, data restored; TLS pending | owner O9 |
| deployment profile | done | `apply-profile` CLI, `config/deployments/*.json` (6), `docs/deployment-profile.md`; ports/adapters seam |
| source quality | done | `verify-sources` CLI, 26/26 feeds grade A, 0 coverage warnings, ADR 014, `docs/source-quality.md` |
| custom industry proof | done | `cybersecurity` and `stem-cell` created from profiles only, serving content |
| stem-cell channel | done | `config/deployments/stem-cell.json`: 6 feeds (4 EN + 2 ES), 5 topics, 53 articles after first refresh |
| instant industry switch | done | `./bin/start.sh industry financial` -> `/` redirects to `/financial`, no rebuild |

| channel subdomains | done | ADR 015, `middleware.ts` + `lib/url.ts`, `start.sh hosts` 14/14 |
| host nginx edge | HTTP answers; TLS template fixed, cert/reload pending | `ops/nginx/`, `start.sh domains`/`certs`, `docs/domains.md` |
| dev→prd migration | done and drilled | `start.sh backup`/`restore`; restored into fresh postgres and into the prd stack |
| apex site | done | ADR 016, lobby + services + legal pages, `GET /v1/desks`, `e2e/lobby.spec.ts` |
| channel inventory | gated | environment-free block, live/profile fallback, CI check |
| request logging | outcome-based | probes silent, 0 lines per 30 s idle |
| fetch safety (M16) | done | politeness 18 tests, fetcher outcome tests, `verify-sources` 50/50, `hosts` 14/14, bots page live in EN/ES |
| source availability (M17) | done | permission ledger, denied/challenge outcomes, licensed-feed auth, availability gate 52/52, `/bot` allowlist block |
| source acquisition (M18) | done | discovery + overlap, licence/outreach register, outbound click counting, portfolio health |
| acquisition pipeline (M19) | done | candidate queue, per-source fetch history, robots-change warning, OPML round-trip, language gaps |
| acquisition quality (M20) | done | licence enforcement, pg_trgm overlap, traffic page, queue refresh, value/retirement, JSON Feed |

**Integrity:** no known waivers. Dev stack running (`system-news-dev`).

---

## Verification evidence (this session)

| Gate | Command | Result |
|---|---|---|
| M15 code gates (2026-11-09) | `pnpm lint` · `tsc --noEmit` · `pnpm check` · `pnpm build` | ✔ · ✔ · ✔ (567 keys, 11/11 contrast) · **BUILD_RC=0** |
| Playwright (2026-11-09, production build) | `pnpm build` + `next start` in a throwaway container (`.next` on `system-news-dev_web_next_prod_v2`) | **120 passed / 0 failed / 5 skipped, exit 0** |
| axe (2026-11-09) | `e2e/accessibility.spec.ts` incl. new brand assertions | 0 critical/serious |
| Layout/CLS (2026-11-09) | measured `/`, `/es`, `/services` × 360 & 1440 px | overflow **0**, **CLS 0.0000** (6/6), emblem 28 px @360 / 32 px @1440 |
| Icons per host (2026-11-09) | curl matrix: apex EN/ES + `stem-cell.`, `financial.`, `legal.localhost` | `favicon.ico` 200 `image/x-icon` everywhere; exactly **1** `rel="icon" href="/favicon.ico"` per doc; apex vs subdomain bytes identical |
| Assets (2026-11-09) | `identify` on `src/app/*` | favicon 48/32/16 (16 px non-blank), icon 512, apple 180 **100 % opaque** (corner `srgb(11,18,32)`) |
| Routing (2026-11-09) | `./bin/start.sh hosts` | **14/14** incl. *the lobby carries the brand* (asserts HeraldFox) |
| MOD-06 + scope (2026-11-09) | `mod06-output-check.sh` · `touch-scope-verify.sh` · `traceability-verify.sh` · `blast-radius-check.sh` | pass · pass · **17/17 FR** · warn (files=21, lines≈189, areas `apps bin .work .work.ui`, all declared) |
| api notify fixture (2026-11-09) | `pytest tests/unit/test_notify.py` | 12 passed |
| Plan drift (2026-11-09) | `touch-scope-verify.sh` / `traceability-verify.sh` / `mod06-output-check.sh` / `blast-radius-check.sh` | pass · 17/17 FR · pass · medium = docs only, MOD-06 merge_ok |
| Derivation smoke test (2026-11-09) | six `convert` commands in `tmp/` (removed after) | emblem 700×700 transparent, lockup 1265×921, tile 512×512, favicon 48/32/16, icon 512, apple 180 opaque |
| Lobby e2e (2026-11-09) | `pnpm exec playwright test e2e/lobby.spec.ts` | 13 passed |
| Layout e2e (2026-11-09) | `pnpm exec playwright test e2e/layout.spec.ts` | 58 passed, 1 flaky (green on retry) |
| Accessibility (2026-11-09) | `pnpm exec playwright test e2e/accessibility.spec.ts` | 29 passed |
| Web gates (2026-11-09) | `pnpm lint`, `tsc --noEmit`, `pnpm check`, `pnpm build` | clean, 567 keys, 11/11 contrast |
| Board fit (2026-11-09) | rendered sweep 320-1440 px | 33 cells, 0 clipped, 0 page overflow |
| API (2026-11-07) | `pytest -q` in the dev api | 164 passed |
| Web (2026-11-07) | `pnpm lint`, `tsc --noEmit`, `pnpm check` | clean, 567 keys |
| Email (2026-11-07) | live send through the gateway | delivered; `dkim=pass d=links.heraldfox.com`, `dmarc=pass` |
| Restore drill (2026-11-07) | bundle replayed into a clean Postgres 16 | 11 channels / 676 articles / 52 sources / 16 migrations |
| Footer (2026-11-07) | rendered `/`, `/legal`, `/es`, `/admin` | LogicBison mark and link present |
| API (prior) | `./bin/start.sh dev test` (ruff, format, mypy, pytest) | 152 passed, no issues |
| Web | lint, `tsc --noEmit`, catalogue/theme check | clean, 566 keys in EN and ES |
| OpenAPI | `python scripts/export_openapi.py` + diff | snapshot current (`/v1/desks`, cta `surface`) |
| Inventory | `./bin/channels.sh --check` (live API and profile fallback) | ok both ways, 11 rows |
| Routing | `./bin/start.sh dev hosts` | 14/14 |
| Production image | `docker compose -f docker-compose.prd.yml build web` + serve | built, all apex routes 200, 11 plates |
| Playwright (prod) | lobby + accessibility + public + layout | 111 passed; lobby + axe alone 41 passed |
| Playwright (dev) | full suite incl. admin | 115 passed, 0 failed (3 flaky, retried green) |
| Contrast | every text node on six apex pages | 0 failures below 4.5:1 (dev and prod) |
| Links | every internal href on six apex pages | 26/26 return 200 |
| Logs | 30 s idle after the change | api 0, web 0, worker 0 lines |
| Migration | 016 applied on dev and on the restored prd copy | `applied: 0, total: 16` |
| C+D gates (2026-11-10) | api `ruff`/`format`/`mypy`/`pytest`; web `lint`/`tsc`/`check`; `pnpm build` | **209 passed** · **579 keys**, 11/11 contrast · **RC=0** |
| Playwright (2026-11-10) | full suite on the rebuilt production bundle | **124 passed / 0 failed / 5 skipped** |
| Sources (2026-11-10) | `verify-sources --industry all` | **50 sources, 50 passed, 0 warnings** |
| Hosts (2026-11-10) | `./bin/start.sh --env dev hosts` | **all checks passed** (14 invariants) |
| Parser repairs (2026-11-10) | `test_normalize.py` (bare `&`, CDATA untouched) | 2 new tests pass |
| Politeness (2026-11-10) | `test_politeness.py` (fake clock, no network) | 18 passed |
| M17 gates (2026-11-10) | api `ruff`/`format`/`mypy`/`pytest`; web `lint`/`tsc`/`check`; `pnpm build` | **218 passed** · **583 keys**, 11/11 · **RC=0** |
| M17 Playwright (2026-11-10) | full suite on the rebuilt production bundle | **124 passed / 0 failed / 5 skipped** |
| M17 sources (2026-11-10) | `verify-sources --industry all` | **52/52, unavailable 0, rc=0**; all 52 recorded `allowed` |
| M17 migration (2026-11-10) | migrations run twice | `applied: 0, total: 17` on re-run |
| M18 gates (2026-11-10) | api `ruff`/`format`/`mypy`/`pytest`; web `lint`/`tsc`/`check`; `pnpm build` | **222 passed** · **584 keys**, 11/11 · **RC=0** |
| M18 discovery (2026-11-10) | `sources discover` on three real feeds | BBC business **accept** (47 items, overlap 0.0); CISA + The Register **reject** (configured); robots + quality paths exercised |
| M18 outbound (2026-11-10) | `GET /v1/outbound/{id}` | **302** + publisher URL + `no-store`; unknown id **404**; `outbound_clicks` 0 → 1 |
| M18 health/report (2026-11-10) | `sources health --industry legal`, `sources report` | rows with `items_7d`/`items_30d`/`clicks_30d`; portfolio by desk |
| M19 gates (2026-11-10) | api `ruff`/`format`/`mypy`/`pytest` | clean · **224 passed** |
| M19 queue (2026-11-10) | discover `--save` → `candidates list` → `decide` | saved 1, decided `accepted` with note, snippet returned |
| M19 export (2026-11-10) | `sources export` → `parse_candidates` | OPML round-trip test; 52 enabled sources exported |
| M19 migration (2026-11-10) | migrations twice | `applied: 0, total: 19` on re-run |
| M20 gates (2026-11-10) | api `ruff`/`format`/`mypy`/`pytest`; web `lint`/`tsc`/`check`; `pnpm build` | **233 passed** · 584 keys · **RC=0** |
| M20 pg_trgm (2026-11-10) | `overlap_share` on a real legal title | same title **1.0**, unrelated **0.0** |
| M20 traffic (2026-11-10) | token + `GET /v1/traffic/<token>` + built page | 200; page renders `Reading record`, source name, clicks |
| M20 refresh (2026-11-10) | NIST candidate saved then refreshed | re-graded `accept`, status untouched |
| M20 health (2026-11-10) | `sources health --industry legal` | `value_score` present; no retirement proposals |
| M20 migration (2026-11-10) | migration 020 | `applied: 1` then re-run `applied: 0, total: 20` |

Not verified: production HTTPS after the duplicate-directive fix (`nginx -t`, reload, `certs --check`); the footer credit on the live hosts; R10's seeded-cooldown render (no cooldown seeded in dev — lint/tsc/build only); D1–D5 on live output (waits for the next natural refresh, decision 3); the prd shadow week for pacing.

## Open owner actions

| # | Action | Blocks | Owner | Where |
|---|--------|--------|-------|-------|
| O1 | ~~Ratify ADRs 001-013~~ approved | - | owner | `.work/decisions/` |
| O2 | ~~VPS provider/budget~~ approved | - | owner | ADR 005 |
| O3 | ~~NFR targets~~ approved | - | owner | doc 04 §5 |
| O4 | ~~Stack files~~ approved/created | - | owner | operations proposal |
| O5 | Fill remaining unknowns: U1 brand, U7 roles, U9 analytics, U10 traffic, U11 legal review, U12 sponsored (U8 closed: gateway integrated and tested) | launch | owner | `.work/plans/UNKNOWNS.md` |
| O6 | ~~Master plan~~ approved | - | owner | full plan v1.1 |
| O7 | prd domain/DNS + provider | prd deploy | owner | launch checklist |
| O8 | CDN/off-site backup bucket (optional) | RPO | owner | backup doc |
| O9 | Finish production TLS on `169.58.4.85`: pull the template fix, `domains --write`, `nginx -t`, reload, `certs --check`, `hosts` | public HTTPS | owner | `docs/domains.md` |
| O10 | Approve the `.github/workflows/ci.yml` inventory gate before it runs on a PR | CI | owner | workflow file |
| O11 | Delete the now-unused `Caddyfile` (ADR 015 replaced the edge) | tidiness | owner | repo root |
| O12 | Decide the brand string across surfaces (D-018 covers the apex; channel footers still say System News) | consistency | owner | `.work.biz/decisions/` |
| O13 | Deploy the footer credit: `git pull` + `./bin/start.sh --env prd up` on the host | live attribution | owner | `apps/web/src/components/DevelopedBy.tsx` |
| O14 | Reconcile the host's local TLS template edit before pulling; the repo now carries the fix | clean pull | owner | `ops/nginx/site.conf.template` |
| O15 | Approve the `SMTP_FROM` spelling change to **HeraldFox** in `.env.example` / `.env.dev` / `.env.prd` (protected surfaces — needs same-message approval) | brand consistency in outgoing mail | owner | `.env.example` (`SMTP_FROM` block) |
| O16 | ~~Approve the `BOT_*`/`FETCH_*` keys in `.env.example`~~ approved 2026-11-10, keys added under "crawler identity and pacing" | - | owner | `.env.example` |
| O17 | ~~Confirm CISA News and SEC Press Releases~~ answered 2026-11-10: keep both | - | owner | `apps/api/config/deployments/` |

---

## What this cycle produced

| Date | Session | Artifacts |
|------|---------|-----------|
| 2026-11-09 | **M15 brand surfaces (complete)** | `apps/web/public/brand/{heraldfox-emblem,heraldfox-lockup,icon-tile}.png`; `apps/web/src/app/{favicon.ico,icon.png,apple-icon.png}` (file-based metadata); `components/lobby/shell.tsx` + `lobby.css` masthead/footer marks (32/28/24 px, `.lb-brand-mark` retired); `e2e/accessibility.spec.ts` brand assertions; `middleware.ts` matcher excludes `brand/`, `icon.png`, `apple-icon.png`; "HeraldFox" one word in `messages/{en,es}.json`, `bin/start.sh`, `apps/api/tests/unit/test_notify.py`; full plan **v1.7** (M15 T1..T7 done), NEXT iteration closed with MOD-06 code output |
| 2026-11-09 | plan-drift fixes (@x-director) | full plan **v1.6** (missing `M15-T8` row added, G1 → `M15-T1..T8`); brand-assets plan corrected (decision-1 header, tracked-art claim, `convert` + `-fuzz 2%` derivation, lockup 1265×921); NEXT gained the plan-verification block and the MOD-06 output; HANDOFF + HANDOFF_UI x-director records |
| 2026-11-09 | responsive fix (M15-T8) | lobby desk board kept three columns (languages column dropped by the owner) and stopped clipping its last column at 1024-1440 px; masthead wraps under 720 px so a 390 px document no longer scrolls sideways; regression test in `e2e/lobby.spec.ts` |
| 2026-11-09 | improvement planning | `.work/plans/20261109-next-improvement.md` (4 tracks), `.work/features/fetch-safety/20261109-SPEC.md`, `.work.ui/plans/20261109-brand-assets.md`; content audit of 676 articles from the 2026-11-07 bundle; M15 planned in the full plan + `## Current iteration` in NEXT |
| 2026-11-07 | email | pilo-mail gateway transport lanes, `info@links.heraldfox.com`, DKIM/DMARC pass, real delivery |
| 2026-11-07 | restore hardening | `init-env` DB/Redis passwords + URL sync, preflight email lane, menu restore `--all`, bundle drill |
| 2026-11-07 | production deploy | `vmi3435240` (169.58.4.85): stack up, data restored, HTTP-only nginx; TLS template fix |
| 2026-11-07 | footer credit | LogicBison mark + wordmark on channel, lobby and admin footers |
| 2026-11-07 | production edge | channel subdomains behind host nginx (ADR 015), `start.sh` domains/certs/preflight/hosts, dev→prd bundle backup+restore, `docs/domains.md`, `docs/guides/migrate-dev-to-prod.md` |
| 2026-11-07 | apex site | lobby + services + network legal pages (ADR 016), `GET /v1/desks`, migration 016 (`surface`, `desk_enter`), 140 `lobby.*` keys, `e2e/lobby.spec.ts`, apex sitemap/robots |
| 2026-11-07 | lobby review | four defects fixed from owner screenshots (anchor-colour specificity, page-relative section links, `{desks}` placeholder, form-field contrast), contact form added (D-020), "no ads" claims replaced (D-021) |
| 2026-11-07 | operational gates | channel inventory made environment-free and CI-gated, outcome-based request logging, dev log rotation, Playwright libs baked into `Dockerfile.dev` |
| 2026-11-05 | implementation | `apps/api` full service: platform, channels, sources, articles, publishing, editorial, worker, CLI; migrations 001-003; config scoring/seeds/prompts |
| 2026-11-05 | implementation | `apps/web` full Next app: themes, EN/ES, SEO, public pages, admin console, lead/contact forms, proxy, middleware |
| 2026-11-05 | verification | API 77 tests, web lint/type/build, Playwright public/axe, OpenAPI snapshot, AI smoke, backup/restore drill |
| 2026-11-05 | template | `POST /v1/admin/industries`, channels admin tab, `docs/adding-an-industry.md`, verification doc |
| 2026-11-05 | ops | runbooks, launch checklist, security review, restore drill, Prometheus alerts, Grafana dashboards, k6 |
| 2026-11-05 | isolation | random host ports, per-project `*-net`/`*-data`, DB/Redis internal-only |
| 2026-11-05 | custom subjects | `cybersecurity` + `stem-cell` channels from profiles only; 32 verified feeds |
| 2026-11-05 | docs | `docs/guides/switching-channels.md` quick reference; UI skin refresh brief |
| 2026-11-05 | lead magnet | `ProofStrip`, `TrustBlock`, `BriefSignup` components wired to channel home + article (all 7 channels, EN/ES); recommendations in `.work.biz/strategy/20261105-lead-magnet-recommendations.md` |
| 2026-11-05 | lead qualification | migration 008 (`leads.qualification` + per-channel `cta.qualify`), API field, `LeadForm` select, deployment profiles synced, 1 new contract test |
| 2026-11-05 | ui foundation | `.work.ui/plans/foundation/01-04`, `tokens.json` (74 DTCG), certified screen-spec-ready; 7 channel-home SPECs |
| 2026-11-05 | skins | `skins.ts` + `skins.css` + 7 motifs + 7 emblems + 7 photos; four coverage rhythms; dark scheme |
| 2026-11-05 | ui v2 | lead-gen reference intake (`ellevest`, `hubspot`, `leadpages`) + `editorial-conversion` build; direction **Approved**; 10 SPECs bound; all ten reviewed/amended → `Review`; open/full-bleed layout, balanced CSS columns, clear filled forms; `e2e/layout.spec.ts`; 57 e2e / 1 skipped, 80 pages zero overflow, token-lint 0 raw literals |
| 2026-11-05 | channel expansion | manufacturing, energy, retail profiles + 5/4/4 sources; Forge/Grid/Market skins + SVG bands + emblems; 10-row reference map; 45/45 sources verified; `pnpm check` 10/10 |
| 2026-11-05 | channel inventory | `docs/channel-inventory.md` generated from `/v1/industries` (10 channels, EN/ES URLs, layout, default); `apps/web/scripts/channel-inventory.mjs` + `bin/channels.sh`; `./bin/start.sh test` fails when stale |
| 2026-11-05 | visual verify | `@ui-visual-verify milestone`: **pass with gaps** on 10 channels; UIS-07/10 done; 57 e2e / 1 skipped; axe 11/11; report in `.work.ui/reports/20261105-visual-verify-milestone.md` |
| 2026-11-05 | session close | commit + push; handoff/next refreshed |
| 2026-11-05 | lead-gen rungs | migration 010 (`question`/`asset` kinds, 3 funnel events); `AskQuestion` rung on articles; `AssetOffer` waitlist (legal regulatory calendar); `/{industry}/briefs` archive; `/{industry}/topic/{slug}` hubs; UTM capture on all lead forms; disposable-domain rejection |
| 2026-11-05 | funnel read-out | `GET /v1/admin/funnel` (stages, rates, per-channel, placement mix) + admin Funnel tab; OpenAPI snapshot regenerated; contract tests added |
| 2026-11-05 | biz offers | `.work.biz/strategy/20261105-offer-and-leadgen-brief.md` (S1-S4, I1-I5, R1-R12, packages for ai/ui) + `20261105-product-feasibility-verification.md` (per-channel feasibility, jurisdiction matrix, V1-V10 claim audit) |
| 2026-11-05 | spec approval | operator approved all ten channel-home SPECs (`Review` -> `Approved`); SPEC headers + `HANDOFF_UI`/`NEXT_UI` updated |
| 2026-11-05 | a11y audit | `@ui-accessibility-audit milestone`: **pass** on 30 URLs (10 channels EN/ES + flows + articles); 0 critical/serious; 2 moderate best-practice (nav labels, CTA landmark); report + `HANDOFF_UI`/`NEXT_UI` updated |
| 2026-11-05 | a11y fixes | F1 footer `nav.footer` label (en/es catalogs, 269 keys) + F2 CTA `<aside>` -> `<section>`; axe re-scan 8 pages 0 violations (incl. best-practice); F3 in ten SPEC amendments; F4/F5 left as debt |
| 2026-11-05 | CATALOG init | `.work.ui/design-system/CATALOG.md` rebuilt from foundation doc 03: 21 rows, DTCG token names, behavior sources, APG patterns, states, a11y notes |
| 2026-11-05 | S0 primitives | 10 files under `apps/web/src/components/ui/`; LeadForm/ContactForm/BriefSignup/TrustBlock/TopicRail/Notices refactored; field errors wired via `aria-invalid`/`aria-describedby` |
| 2026-11-05 | imagery | 10/10 photographic bands; retail/energy/manufacturing replaced SVG line-art with CC BY/BY-SA photos (credits.json); report `.work.ui/reports/20261105-imagery-audit.md` |
| 2026-11-06 | M9 asset card test | `cta.asset` in channel config (migration 011 + profiles), card resolved from config, brief rung suppressed where an asset exists, SPEC amendment 01, e2e coverage; D-008/D-009 recorded |
| 2026-11-06 | M9 gap fixes + repair | plan v1.2 with M9; coverage card clamp (energy 330px -> 85px, worst channel 178px); full suite 59 passed / 1 skipped |
| 2026-11-06 | biz scope | `.work.biz/plans/plan_kev-digest.md` (KEV digest MVP scope), D-003…D-009, 14-day window pre-registered |
| 2026-11-06 | M10 topics | three digital-tech topics on the cybersecurity profile, `placement="topic"` attribution, migration 012 + unit test, D-010/D-014 |
| 2026-11-06 | M11 channel | `digital-technology` profile, `datacenter` skin (motif/scene/CC BY-SA photo), 6 grade-A feeds, 26 EN + 1 ES items, inventory at 11 channels, e2e + docs |
| 2026-11-06 | M12 channel automation | migration 013; per-channel fetch cadence + pause; four free-offer switches; admin Channels editor; public offer gating; 124 API tests, 87 Playwright |
| 2026-11-06 | M14 lead attribution | migration 015; contact/lead country + session + UTM; Contacts tab; privacy copy; 143 API tests |
| 2026-11-06 | M13 offer generation | migration 014; Federal Register + CISA KEV adapters; AI draft with fallback; automatic scheduling; CLI + admin API + Offers tab; reviewer-gated publish; public reference pages; 139 API tests; email remains |

---

## Explicit unknowns (promoted from UNKNOWNS)

| # | Unknown | Blocks | Owner |
|---|---|---|---|
| U1 | Brand name across surfaces (apex ratified as **HeraldFox**, one word, per owner 2026-11-09; channels unchanged) | consistency | owner |
| U8 / U20 | Email delivery — integrated and tested through the gateway; the weekly-brief campaign is still unbuilt | brief campaign, G1 | owner |
| D-005 / U19 | Named reviewers — holds the reviewer signature line in the services copy | content-generation claim, G2 | owner |
| U9 | Analytics/consent vendor | lobby funnel depth beyond first-party | owner |
| U10 | Traffic baseline | lobby keep/kill thresholds | owner |
| U32 | Who takes the service scope call, and what reply is committed to | services band | owner |
| U33 | Service pricing shape (per desk, per issue, per audience) | pilot SKU | owner |
| U34 | Whether `www` should serve the lobby or 301 to the apex | edge config | owner |

## Cross-framework action (@x-director)

Lead generation remains integrated (ADR 013, FR-17): one primary CTA per page,
consent-first lead form, partner routing, DSAR export/erase, funnel events, and
lead dashboards/alerts. UI foundation and biz strategy docs remain in
`.work.ui/` and `.work.biz/`.

### 2026-11-05 — UI v2 via lead-generation reference intake

**Request:** "use x-director to improve the UI with the recently updated UI Agent OS Framework, using the lead-generation references/skills now available in 'ui' os" → "too many boxes, too many rounded corners... forms confusing... unbalanced columns".
**Frameworks involved:** `.ai`, `.ai.ui`
**Classified bucket(s):** cross-framework (ui primary; engineering for build/verify)
**Executed:**
1. `@ui-reference-intake scan/dna/synthesize` — `ellevest`, `hubspot`, `leadpages` → DNA docs + direction `editorial-conversion` (Approved 2026-11-05).
2. `@ui-component-build` (applied under operator's continue instruction) — open editorial layout, full-bleed bands, sharp corners, balanced CSS columns, per-channel CTA placement, filled forms.
3. Verification — production build; Playwright 57 passed / 1 skipped; `e2e/layout.spec.ts` 30 checks; 80 pages 200 + zero overflow; `pnpm lint/typecheck/check` green; token-lint 0 raw.
4. Operator approved the direction + bind package; composition tokens added to `tokens.json` (84, schema-valid); ten SPECs §13/§11 bound with `exampleIds: N/A` waiver; `SCREEN_REFERENCE_MAP.md` created; reference audit PASS.
5. `@ui-screen-spec review` run across all ten channels; 7 SPEC-vs-build mismatches amended in each §3/§4/§5/§8/§11/§12/§13; re-check PASS 10/10; all statuses `Review` (approval still operator’s).
6. Added `manufacturing`, `energy`, `retail`: profiles applied to dev, 45/45 sources verified, Forge/Grid/Market skins, three bound/reviewed SPECs; 57 e2e / 1 skipped; 80 pages 200 + no overflow.
7. Channel inventory is generated from the API (`docs/channel-inventory.md`, `bin/channels.sh`); `./bin/start.sh test` runs `--check` and fails on a stale list.
8. Visual fix after review: Sanctuary CTA opened (transparent, accent rule), skin-level hero/story radius+shadow removed, proof/conversion borders removed, health coverage moved to 2 balanced columns, Sentinel dark-scheme link/eyebrow contrast fixed; axe 11/11.
9. Visual verify milestone: pass with gaps; UIS-07 (ship_with_notes) + UIS-10 (ship) done; 40 layout checks, 11 axe pages; square-surface + no-motif regressions enforced.
**Coordination notes:** UI + channel data; no API/schema code changes. `.work.ui/` artifacts + `apps/web` code + `apps/api/config/deployments/*.json`; no protected files edited.
**Blockers:** none for the build; all ten SPECs are in `Review` pending operator approval.
**Next recommended:** approve the ten `Review` SPECs; close the new channels' content gaps; then `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-06
**Request:** "resolve all gaps"
**Frameworks involved:** .ai, .ai.ui (delegated to .ai; no ui-director run — the design rule was an operator decision, D-008)
**Classified framework bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc yes (unused) | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. `@ai-director` — R16 literal: `industries.cta.asset` (channel config) seeded by `apps/api/migrations/011_seed_asset_offers.sql`, profiles updated, `/v1/news/bundle` passthrough asserted in `test_bundle.py`; web resolves the card from `channel.cta.asset`. Decision D-009 supersedes D-007.
2. `@ai-director` (ui rule by operator decision D-008) — one secondary rung: the brief signup no longer renders where `cta.asset` is set; SPEC R16 amended; e2e asserts the rule on four channels.
3. `@ai-director` — plan traceability: M9 added to `.work/plans/full/20261105-full-plan.md` §19 (v1.2) with a traceability row; the waiver is now retired.
4. Re-verified: api 111 passed, web lint/type/check clean, migration 011 `applied: 1` then `applied: 0`, full Playwright 58 passed / 1 skipped / 1 failed.
**User correction:** none
**Coordination notes:** the design rule was taken natively (single-model) rather than routed to `@ui-director`; recorded so the routing is auditable.
**Blockers:** `layout.spec.ts:31` energy coverage balance fails on new content (330px vs 260) — not caused by M9 (ingestion at 16:03, after the 15:58 green run; energy renders neither card nor asset). Needs a separate layout decision.
**Next recommended:** `@code-implementation complete`, then `@session-control close commit` split in two (apps/, then `.work*`).

---

## Known residual risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| TLS reload not re-verified | the host rejected the first 443 config on duplicate session directives; the template is fixed, but `nginx -t`, reload and `certs --check` still need to pass | O9 is the first step next session |
| nginx config validated syntactically only | `nginx -t` passes but no request has gone through the real edge | `start.sh hosts` runs the same contract over HTTP once the host proxy is live |
| CI inventory gate unapproved | the step would run on the next PR before the owner signs off | listed as O10 |
| Brand string split | apex says **HeraldFox** (one word, owner 2026-11-09), channel footers still say System News | D-018 with a 2026-12-15 outcome date |
| Scheduler can park a channel | a run stuck in `queued`/`running` blocks that channel until a worker restart; orphan recovery runs only at start (`queue.py:42-63`, `repo.py:285-293`) | cadence verified 2026-11-09 (720 min, all 11 channels); sweep proposed in the M15 block |
| Emblem source PNG is 599 KB | `public/brand/heraldfox-emblem.png` is served raw wherever `next/image` is not used (footer/OG-less paths) | masthead + footer both use `next/image`; measured `naturalWidth=32` at render, so a resized variant is what ships |
| Favicon caching per origin | browsers cache `favicon.ico` per origin, so a re-derived icon needs a hard refresh on each of 11 subdomains | accept; re-check with a cache-busting query during verification |
| Tile colour `#0b1220` assumed | the derived `icon.png`/`apple-icon.png` are flattened on it; UI plan §5 decision 2 is still owner-open | measured corner is `srgb(11,18,32)`; re-derive if the owner picks another colour |
| Playwright output recompiles dev | `apps/web/test-results/` sits inside the bind-mounted `/app`; one write triggers a Next compile + "Fast Refresh had to perform a full reload", which can knock out a running test (pre-existing, gitignored) | clean `test-results/` before a suite run; run the gate suite against a **production** build in a throwaway container |
| `pnpm build` clobbers the dev `.next` | `.next` is the named volume `system-news-dev_web_next_v2` and the dev container's entrypoint is `pnpm dev`; a build inside it overwrites the running build (this happened 2026-11-09 and 404'd every asset until wiped) | never run `pnpm build` in the dev container — use `docker compose run --rm --no-deps -v system-news-dev_web_next_prod_v2:/app/.next web` |

- Single VPS SPOF (R4); volume restore drilled, prd deploy/rollback not drilled.
- Feed licensing/terms (U11) and Spanish coverage (R17) remain owner inputs.
- The UI has ten channels/skins, a verified editorial-conversion v2 build, an **Approved** direction with all ten SPECs **approved**, a passed a11y milestone audit, shipped S0 primitives, and photographic bands on all ten channels. Storybook, the P1 primitives (`Skeleton`, `Toc`) and the vision tier remain open.
- Channel coverage is uneven at the edges, not empty: the thinnest locale is digital-technology ES (16 items), then retail ES (24). All eleven channels use licensed photos; profiles are applied to dev, not prd; legal/terms review (U11) still applies.
- The cybersecurity channel uses a dark scheme; fill/border contrast of the new conversion fields was checked visually, but the matrix is not yet in `check-themes.mjs`.
- Photo licences are recorded per file (`apps/web/public/photos/credits.json`); four channels are CC BY/BY-SA and depend on the in-caption credit staying rendered (financial, cybersecurity, stem-cell, plus retail, energy, manufacturing).
- AI summaries are fail-open; some items are intentionally left without a
  summary when validation rejects output.
- CI is written but has not run on GitHub yet.
- prd stack is up on 169.58.4.85 with the data restored; TLS and a rollback drill remain.
- `k6` and Lighthouse budgets are scripts only; no prd measurement yet.
- E2E runs against a production build; run `pnpm build` before `pnpm test`.
- AI validation intentionally rejects some provider output; those items publish
  without a summary.
- **Brief promise ahead of the system:** the weekly brief copy promises a Monday email; delivery lands before production (owner-owned). Until it exists, capture is ahead of fulfilment.
- **Asset scope is US + EU only.** No Asia source coverage, no JP/KR/ZH translation, and the logistics rate index is not buildable (licensed data) - replaced by a port/customs digest per the feasibility doc.
- **Empty archive on purpose:** `/{industry}/briefs` renders an honest empty state until the first issue publishes.

---

## Next action

Session closed. The tree is committed and pushed. Next is the operator lane: deploy to prd
(`git pull`, `preflight`, `up`, `domains --write`, `nginx -t`, reload, `certs --check`,
`hosts`), with `FETCH_PACING=shadow` for the first week. Then **O9** TLS confirmation and
**O15** `SMTP_FROM`. Agent follow-ups when work resumes: read the next natural refresh for
D1–D5, and flip pacing to `enforce` after the shadow week.

## Cross-framework action (@x-director)

Lead generation remains integrated (ADR 013, FR-17): one primary CTA per page,
consent-first lead form, partner routing, DSAR export/erase, funnel events, and
lead dashboards/alerts. UI foundation and biz strategy docs remain in
`.work.ui/` and `.work.biz/`.

### 2026-11-05 — UI v2 via lead-generation reference intake

**Request:** "use x-director to improve the UI with the recently updated UI Agent OS Framework, using the lead-generation references/skills now available in 'ui' os" → "too many boxes, too many rounded corners... forms confusing... unbalanced columns".
**Frameworks involved:** `.ai`, `.ai.ui`
**Classified bucket(s):** cross-framework (ui primary; engineering for build/verify)
**Executed:**
1. `@ui-reference-intake scan/dna/synthesize` — `ellevest`, `hubspot`, `leadpages` → DNA docs + direction `editorial-conversion` (Approved 2026-11-05).
2. `@ui-component-build` (applied under operator's continue instruction) — open editorial layout, full-bleed bands, sharp corners, balanced CSS columns, per-channel CTA placement, filled forms.
3. Verification — production build; Playwright 57 passed / 1 skipped; `e2e/layout.spec.ts` 30 checks; 80 pages 200 + zero overflow; `pnpm lint/typecheck/check` green; token-lint 0 raw.
4. Operator approved the direction + bind package; composition tokens added to `tokens.json` (84, schema-valid); ten SPECs §13/§11 bound with `exampleIds: N/A` waiver; `SCREEN_REFERENCE_MAP.md` created; reference audit PASS.
5. `@ui-screen-spec review` run across all ten channels; 7 SPEC-vs-build mismatches amended in each §3/§4/§5/§8/§11/§12/§13; re-check PASS 10/10; all statuses `Review` (approval still operator’s).
6. Added `manufacturing`, `energy`, `retail`: profiles applied to dev, 45/45 sources verified, Forge/Grid/Market skins, three bound/reviewed SPECs; 57 e2e / 1 skipped; 80 pages 200 + no overflow.
7. Channel inventory is generated from the API (`docs/channel-inventory.md`, `bin/channels.sh`); `./bin/start.sh test` runs `--check` and fails on a stale list.
8. Visual fix after review: Sanctuary CTA opened (transparent, accent rule), skin-level hero/story radius+shadow removed, proof/conversion borders removed, health coverage moved to 2 balanced columns, Sentinel dark-scheme link/eyebrow contrast fixed; axe 11/11.
9. Visual verify milestone: pass with gaps; UIS-07 (ship_with_notes) + UIS-10 (ship) done; 40 layout checks, 11 axe pages; square-surface + no-motif regressions enforced.
**Coordination notes:** UI + channel data; no API/schema code changes. `.work.ui/` artifacts + `apps/web` code + `apps/api/config/deployments/*.json`; no protected files edited.
**Blockers:** none for the build; all ten SPECs are in `Review` pending operator approval.
**Next recommended:** approve the ten `Review` SPECs; close the new channels' content gaps; then `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-06
**Request:** "resolve all gaps"
**Frameworks involved:** .ai, .ai.ui (delegated to .ai; no ui-director run — the design rule was an operator decision, D-008)
**Classified framework bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc yes (unused) | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. `@ai-director` — R16 literal: `industries.cta.asset` (channel config) seeded by `apps/api/migrations/011_seed_asset_offers.sql`, profiles updated, `/v1/news/bundle` passthrough asserted in `test_bundle.py`; web resolves the card from `channel.cta.asset`. Decision D-009 supersedes D-007.
2. `@ai-director` (ui rule by operator decision D-008) — one secondary rung: the brief signup no longer renders where `cta.asset` is set; SPEC R16 amended; e2e asserts the rule on four channels.
3. `@ai-director` — plan traceability: M9 added to `.work/plans/full/20261105-full-plan.md` §19 (v1.2) with a traceability row; the waiver is now retired.
4. Re-verified: api 111 passed, web lint/type/check clean, migration 011 `applied: 1` then `applied: 0`, full Playwright 58 passed / 1 skipped / 1 failed.
**User correction:** none
**Coordination notes:** the design rule was taken natively (single-model) rather than routed to `@ui-director`; recorded so the routing is auditable.
**Blockers:** `layout.spec.ts:31` energy coverage balance fails on new content (330px vs 260) — not caused by M9 (ingestion at 16:03, after the 15:58 green run; energy renders neither card nor asset). Needs a separate layout decision.
**Next recommended:** `@code-implementation complete`, then `@session-control close commit` split in two (apps/, then `.work*`).

---

## Known residual risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| TLS reload not re-verified | the host rejected the first 443 config on duplicate session directives; the template is fixed, but `nginx -t`, reload and `certs --check` still need to pass | O9 is the first step next session |
| nginx config validated syntactically only | `nginx -t` passes but no request has gone through the real edge | `start.sh hosts` runs the same contract over HTTP once the host proxy is live |
| CI inventory gate unapproved | the step would run on the next PR before the owner signs off | listed as O10 |
| Brand string split | apex says **HeraldFox** (one word, owner 2026-11-09), channel footers still say System News | D-018 with a 2026-12-15 outcome date |
| Scheduler can park a channel | a run stuck in `queued`/`running` blocks that channel until a worker restart; orphan recovery runs only at start (`queue.py:42-63`, `repo.py:285-293`) | cadence verified 2026-11-09 (720 min, all 11 channels); sweep proposed in the M15 block |
| Emblem source PNG is 599 KB | `public/brand/heraldfox-emblem.png` is served raw wherever `next/image` is not used (footer/OG-less paths) | masthead + footer both use `next/image`; measured `naturalWidth=32` at render, so a resized variant is what ships |
| Favicon caching per origin | browsers cache `favicon.ico` per origin, so a re-derived icon needs a hard refresh on each of 11 subdomains | accept; re-check with a cache-busting query during verification |
| Tile colour `#0b1220` assumed | the derived `icon.png`/`apple-icon.png` are flattened on it; UI plan §5 decision 2 is still owner-open | measured corner is `srgb(11,18,32)`; re-derive if the owner picks another colour |
| Playwright output recompiles dev | `apps/web/test-results/` sits inside the bind-mounted `/app`; one write triggers a Next compile + "Fast Refresh had to perform a full reload", which can knock out a running test (pre-existing, gitignored) | clean `test-results/` before a suite run; run the gate suite against a **production** build in a throwaway container |
| `pnpm build` clobbers the dev `.next` | `.next` is the named volume `system-news-dev_web_next_v2` and the dev container's entrypoint is `pnpm dev`; a build inside it overwrites the running build (this happened 2026-11-09 and 404'd every asset until wiped) | never run `pnpm build` in the dev container — use `docker compose run --rm --no-deps -v system-news-dev_web_next_prod_v2:/app/.next web` |

- Single VPS SPOF (R4); volume restore drilled, prd deploy/rollback not drilled.
- Feed licensing/terms (U11) and Spanish coverage (R17) remain owner inputs.
- The UI has ten channels/skins, a verified editorial-conversion v2 build, an **Approved** direction with all ten SPECs **approved**, a passed a11y milestone audit, shipped S0 primitives, and photographic bands on all ten channels. Storybook, the P1 primitives (`Skeleton`, `Toc`) and the vision tier remain open.
- Channel coverage is uneven at the edges, not empty: the thinnest locale is digital-technology ES (16 items), then retail ES (24). All eleven channels use licensed photos; profiles are applied to dev, not prd; legal/terms review (U11) still applies.
- The cybersecurity channel uses a dark scheme; fill/border contrast of the new conversion fields was checked visually, but the matrix is not yet in `check-themes.mjs`.
- Photo licences are recorded per file (`apps/web/public/photos/credits.json`); four channels are CC BY/BY-SA and depend on the in-caption credit staying rendered (financial, cybersecurity, stem-cell, plus retail, energy, manufacturing).
- AI summaries are fail-open; some items are intentionally left without a
  summary when validation rejects output.
- CI is written but has not run on GitHub yet.
- prd stack is up on 169.58.4.85 with the data restored; TLS and a rollback drill remain.
- `k6` and Lighthouse budgets are scripts only; no prd measurement yet.
- E2E runs against a production build; run `pnpm build` before `pnpm test`.
- AI validation intentionally rejects some provider output; those items publish
  without a summary.
- **Brief promise ahead of the system:** the weekly brief copy promises a Monday email; delivery lands before production (owner-owned). Until it exists, capture is ahead of fulfilment.
- **Asset scope is US + EU only.** No Asia source coverage, no JP/KR/ZH translation, and the logistics rate index is not buildable (licensed data) - replaced by a port/customs digest per the feasibility doc.
- **Empty archive on purpose:** `/{industry}/briefs` renders an honest empty state until the first issue publishes.

---

## Next action

M15–M20 are **complete**; M19 is pushed, M20 is **uncommitted**. Run
`@code-verify uncommitted` before committing. Owner lane: **O9** (production TLS on
`169.58.4.85`, also the prd half of M15-T6), **O15** (`SMTP_FROM` spelling), and the prd
migrations 017–020, which apply automatically on the next `up`. Agent follow-ups: the
D-trial read and one week of `FETCH_PACING=shadow` on prd.

## Cross-framework action (@x-director)

Lead generation remains integrated (ADR 013, FR-17): one primary CTA per page,
consent-first lead form, partner routing, DSAR export/erase, funnel events, and
lead dashboards/alerts. UI foundation and biz strategy docs remain in
`.work.ui/` and `.work.biz/`.

### 2026-11-05 — UI v2 via lead-generation reference intake

**Request:** "use x-director to improve the UI with the recently updated UI Agent OS Framework, using the lead-generation references/skills now available in 'ui' os" → "too many boxes, too many rounded corners... forms confusing... unbalanced columns".
**Frameworks involved:** `.ai`, `.ai.ui`
**Classified bucket(s):** cross-framework (ui primary; engineering for build/verify)
**Executed:**
1. `@ui-reference-intake scan/dna/synthesize` — `ellevest`, `hubspot`, `leadpages` → DNA docs + direction `editorial-conversion` (Approved 2026-11-05).
2. `@ui-component-build` (applied under operator's continue instruction) — open editorial layout, full-bleed bands, sharp corners, balanced CSS columns, per-channel CTA placement, filled forms.
3. Verification — production build; Playwright 57 passed / 1 skipped; `e2e/layout.spec.ts` 30 checks; 80 pages 200 + zero overflow; `pnpm lint/typecheck/check` green; token-lint 0 raw.
4. Operator approved the direction + bind package; composition tokens added to `tokens.json` (84, schema-valid); ten SPECs §13/§11 bound with `exampleIds: N/A` waiver; `SCREEN_REFERENCE_MAP.md` created; reference audit PASS.
5. `@ui-screen-spec review` run across all ten channels; 7 SPEC-vs-build mismatches amended in each §3/§4/§5/§8/§11/§12/§13; re-check PASS 10/10; all statuses `Review` (approval still operator’s).
6. Added `manufacturing`, `energy`, `retail`: profiles applied to dev, 45/45 sources verified, Forge/Grid/Market skins, three bound/reviewed SPECs; 57 e2e / 1 skipped; 80 pages 200 + no overflow.
7. Channel inventory is generated from the API (`docs/channel-inventory.md`, `bin/channels.sh`); `./bin/start.sh test` runs `--check` and fails on a stale list.
8. Visual fix after review: Sanctuary CTA opened (transparent, accent rule), skin-level hero/story radius+shadow removed, proof/conversion borders removed, health coverage moved to 2 balanced columns, Sentinel dark-scheme link/eyebrow contrast fixed; axe 11/11.
9. Visual verify milestone: pass with gaps; UIS-07 (ship_with_notes) + UIS-10 (ship) done; 40 layout checks, 11 axe pages; square-surface + no-motif regressions enforced.
**Coordination notes:** UI + channel data; no API/schema code changes. `.work.ui/` artifacts + `apps/web` code + `apps/api/config/deployments/*.json`; no protected files edited.
**Blockers:** none for the build; all ten SPECs are in `Review` pending operator approval.
**Next recommended:** approve the ten `Review` SPECs; close the new channels' content gaps; then `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-06
**Request:** "resolve all gaps"
**Frameworks involved:** .ai, .ai.ui (delegated to .ai; no ui-director run — the design rule was an operator decision, D-008)
**Classified framework bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc yes (unused) | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. `@ai-director` — R16 literal: `industries.cta.asset` (channel config) seeded by `apps/api/migrations/011_seed_asset_offers.sql`, profiles updated, `/v1/news/bundle` passthrough asserted in `test_bundle.py`; web resolves the card from `channel.cta.asset`. Decision D-009 supersedes D-007.
2. `@ai-director` (ui rule by operator decision D-008) — one secondary rung: the brief signup no longer renders where `cta.asset` is set; SPEC R16 amended; e2e asserts the rule on four channels.
3. `@ai-director` — plan traceability: M9 added to `.work/plans/full/20261105-full-plan.md` §19 (v1.2) with a traceability row; the waiver is now retired.
4. Re-verified: api 111 passed, web lint/type/check clean, migration 011 `applied: 1` then `applied: 0`, full Playwright 58 passed / 1 skipped / 1 failed.
**User correction:** none
**Coordination notes:** the design rule was taken natively (single-model) rather than routed to `@ui-director`; recorded so the routing is auditable.
**Blockers:** `layout.spec.ts:31` energy coverage balance fails on new content (330px vs 260) — not caused by M9 (ingestion at 16:03, after the 15:58 green run; energy renders neither card nor asset). Needs a separate layout decision.
**Next recommended:** `@code-implementation complete`, then `@session-control close commit` split in two (apps/, then `.work*`).

---

## Known residual risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| TLS reload not re-verified | the host rejected the first 443 config on duplicate session directives; the template is fixed, but `nginx -t`, reload and `certs --check` still need to pass | O9 is the first step next session |
| nginx config validated syntactically only | `nginx -t` passes but no request has gone through the real edge | `start.sh hosts` runs the same contract over HTTP once the host proxy is live |
| CI inventory gate unapproved | the step would run on the next PR before the owner signs off | listed as O10 |
| Brand string split | apex says **HeraldFox** (one word, owner 2026-11-09), channel footers still say System News | D-018 with a 2026-12-15 outcome date |
| Scheduler can park a channel | a run stuck in `queued`/`running` blocks that channel until a worker restart; orphan recovery runs only at start (`queue.py:42-63`, `repo.py:285-293`) | cadence verified 2026-11-09 (720 min, all 11 channels); sweep proposed in the M15 block |
| Emblem source PNG is 599 KB | `public/brand/heraldfox-emblem.png` is served raw wherever `next/image` is not used (footer/OG-less paths) | masthead + footer both use `next/image`; measured `naturalWidth=32` at render, so a resized variant is what ships |
| Favicon caching per origin | browsers cache `favicon.ico` per origin, so a re-derived icon needs a hard refresh on each of 11 subdomains | accept; re-check with a cache-busting query during verification |
| Tile colour `#0b1220` assumed | the derived `icon.png`/`apple-icon.png` are flattened on it; UI plan §5 decision 2 is still owner-open | measured corner is `srgb(11,18,32)`; re-derive if the owner picks another colour |
| Playwright output recompiles dev | `apps/web/test-results/` sits inside the bind-mounted `/app`; one write triggers a Next compile + "Fast Refresh had to perform a full reload", which can knock out a running test (pre-existing, gitignored) | clean `test-results/` before a suite run; run the gate suite against a **production** build in a throwaway container |
| `pnpm build` clobbers the dev `.next` | `.next` is the named volume `system-news-dev_web_next_v2` and the dev container's entrypoint is `pnpm dev`; a build inside it overwrites the running build (this happened 2026-11-09 and 404'd every asset until wiped) | never run `pnpm build` in the dev container — use `docker compose run --rm --no-deps -v system-news-dev_web_next_prod_v2:/app/.next web` |

- Single VPS SPOF (R4); volume restore drilled, prd deploy/rollback not drilled.
- Feed licensing/terms (U11) and Spanish coverage (R17) remain owner inputs.
- The UI has ten channels/skins, a verified editorial-conversion v2 build, an **Approved** direction with all ten SPECs **approved**, a passed a11y milestone audit, shipped S0 primitives, and photographic bands on all ten channels. Storybook, the P1 primitives (`Skeleton`, `Toc`) and the vision tier remain open.
- Channel coverage is uneven at the edges, not empty: the thinnest locale is digital-technology ES (16 items), then retail ES (24). All eleven channels use licensed photos; profiles are applied to dev, not prd; legal/terms review (U11) still applies.
- The cybersecurity channel uses a dark scheme; fill/border contrast of the new conversion fields was checked visually, but the matrix is not yet in `check-themes.mjs`.
- Photo licences are recorded per file (`apps/web/public/photos/credits.json`); four channels are CC BY/BY-SA and depend on the in-caption credit staying rendered (financial, cybersecurity, stem-cell, plus retail, energy, manufacturing).
- AI summaries are fail-open; some items are intentionally left without a
  summary when validation rejects output.
- CI is written but has not run on GitHub yet.
- prd stack is up on 169.58.4.85 with the data restored; TLS and a rollback drill remain.
- `k6` and Lighthouse budgets are scripts only; no prd measurement yet.
- E2E runs against a production build; run `pnpm build` before `pnpm test`.
- AI validation intentionally rejects some provider output; those items publish
  without a summary.
- **Brief promise ahead of the system:** the weekly brief copy promises a Monday email; delivery lands before production (owner-owned). Until it exists, capture is ahead of fulfilment.
- **Asset scope is US + EU only.** No Asia source coverage, no JP/KR/ZH translation, and the logistics rate index is not buildable (licensed data) - replaced by a port/customs digest per the feasibility doc.
- **Empty archive on purpose:** `/{industry}/briefs` renders an honest empty state until the first issue publishes.

---

## Next action

M15–M18 are **complete**; the tree is verified but **uncommitted**. Run
`@code-verify uncommitted` before any commit. Owner lane: **O9** (production TLS on
`169.58.4.85`, also the prd half of M15-T6) and **O15** (`SMTP_FROM` spelling).
Agent follow-ups: read the next natural refresh for D1–D5 (no forced reset, decision 3)
and run one week of `FETCH_PACING=shadow` on prd.

## Cross-framework action (@x-director)

Lead generation remains integrated (ADR 013, FR-17): one primary CTA per page,
consent-first lead form, partner routing, DSAR export/erase, funnel events, and
lead dashboards/alerts. UI foundation and biz strategy docs remain in
`.work.ui/` and `.work.biz/`.

### 2026-11-05 — UI v2 via lead-generation reference intake

**Request:** "use x-director to improve the UI with the recently updated UI Agent OS Framework, using the lead-generation references/skills now available in 'ui' os" → "too many boxes, too many rounded corners... forms confusing... unbalanced columns".
**Frameworks involved:** `.ai`, `.ai.ui`
**Classified bucket(s):** cross-framework (ui primary; engineering for build/verify)
**Executed:**
1. `@ui-reference-intake scan/dna/synthesize` — `ellevest`, `hubspot`, `leadpages` → DNA docs + direction `editorial-conversion` (Approved 2026-11-05).
2. `@ui-component-build` (applied under operator's continue instruction) — open editorial layout, full-bleed bands, sharp corners, balanced CSS columns, per-channel CTA placement, filled forms.
3. Verification — production build; Playwright 57 passed / 1 skipped; `e2e/layout.spec.ts` 30 checks; 80 pages 200 + zero overflow; `pnpm lint/typecheck/check` green; token-lint 0 raw.
4. Operator approved the direction + bind package; composition tokens added to `tokens.json` (84, schema-valid); ten SPECs §13/§11 bound with `exampleIds: N/A` waiver; `SCREEN_REFERENCE_MAP.md` created; reference audit PASS.
5. `@ui-screen-spec review` run across all ten channels; 7 SPEC-vs-build mismatches amended in each §3/§4/§5/§8/§11/§12/§13; re-check PASS 10/10; all statuses `Review` (approval still operator’s).
6. Added `manufacturing`, `energy`, `retail`: profiles applied to dev, 45/45 sources verified, Forge/Grid/Market skins, three bound/reviewed SPECs; 57 e2e / 1 skipped; 80 pages 200 + no overflow.
7. Channel inventory is generated from the API (`docs/channel-inventory.md`, `bin/channels.sh`); `./bin/start.sh test` runs `--check` and fails on a stale list.
8. Visual fix after review: Sanctuary CTA opened (transparent, accent rule), skin-level hero/story radius+shadow removed, proof/conversion borders removed, health coverage moved to 2 balanced columns, Sentinel dark-scheme link/eyebrow contrast fixed; axe 11/11.
9. Visual verify milestone: pass with gaps; UIS-07 (ship_with_notes) + UIS-10 (ship) done; 40 layout checks, 11 axe pages; square-surface + no-motif regressions enforced.
**Coordination notes:** UI + channel data; no API/schema code changes. `.work.ui/` artifacts + `apps/web` code + `apps/api/config/deployments/*.json`; no protected files edited.
**Blockers:** none for the build; all ten SPECs are in `Review` pending operator approval.
**Next recommended:** approve the ten `Review` SPECs; close the new channels' content gaps; then `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-06
**Request:** "resolve all gaps"
**Frameworks involved:** .ai, .ai.ui (delegated to .ai; no ui-director run — the design rule was an operator decision, D-008)
**Classified framework bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc yes (unused) | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. `@ai-director` — R16 literal: `industries.cta.asset` (channel config) seeded by `apps/api/migrations/011_seed_asset_offers.sql`, profiles updated, `/v1/news/bundle` passthrough asserted in `test_bundle.py`; web resolves the card from `channel.cta.asset`. Decision D-009 supersedes D-007.
2. `@ai-director` (ui rule by operator decision D-008) — one secondary rung: the brief signup no longer renders where `cta.asset` is set; SPEC R16 amended; e2e asserts the rule on four channels.
3. `@ai-director` — plan traceability: M9 added to `.work/plans/full/20261105-full-plan.md` §19 (v1.2) with a traceability row; the waiver is now retired.
4. Re-verified: api 111 passed, web lint/type/check clean, migration 011 `applied: 1` then `applied: 0`, full Playwright 58 passed / 1 skipped / 1 failed.
**User correction:** none
**Coordination notes:** the design rule was taken natively (single-model) rather than routed to `@ui-director`; recorded so the routing is auditable.
**Blockers:** `layout.spec.ts:31` energy coverage balance fails on new content (330px vs 260) — not caused by M9 (ingestion at 16:03, after the 15:58 green run; energy renders neither card nor asset). Needs a separate layout decision.
**Next recommended:** `@code-implementation complete`, then `@session-control close commit` split in two (apps/, then `.work*`).

---

## Known residual risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| TLS reload not re-verified | the host rejected the first 443 config on duplicate session directives; the template is fixed, but `nginx -t`, reload and `certs --check` still need to pass | O9 is the first step next session |
| nginx config validated syntactically only | `nginx -t` passes but no request has gone through the real edge | `start.sh hosts` runs the same contract over HTTP once the host proxy is live |
| CI inventory gate unapproved | the step would run on the next PR before the owner signs off | listed as O10 |
| Brand string split | apex says **HeraldFox** (one word, owner 2026-11-09), channel footers still say System News | D-018 with a 2026-12-15 outcome date |
| Scheduler can park a channel | a run stuck in `queued`/`running` blocks that channel until a worker restart; orphan recovery runs only at start (`queue.py:42-63`, `repo.py:285-293`) | cadence verified 2026-11-09 (720 min, all 11 channels); sweep proposed in the M15 block |
| Emblem source PNG is 599 KB | `public/brand/heraldfox-emblem.png` is served raw wherever `next/image` is not used (footer/OG-less paths) | masthead + footer both use `next/image`; measured `naturalWidth=32` at render, so a resized variant is what ships |
| Favicon caching per origin | browsers cache `favicon.ico` per origin, so a re-derived icon needs a hard refresh on each of 11 subdomains | accept; re-check with a cache-busting query during verification |
| Tile colour `#0b1220` assumed | the derived `icon.png`/`apple-icon.png` are flattened on it; UI plan §5 decision 2 is still owner-open | measured corner is `srgb(11,18,32)`; re-derive if the owner picks another colour |
| Playwright output recompiles dev | `apps/web/test-results/` sits inside the bind-mounted `/app`; one write triggers a Next compile + "Fast Refresh had to perform a full reload", which can knock out a running test (pre-existing, gitignored) | clean `test-results/` before a suite run; run the gate suite against a **production** build in a throwaway container |
| `pnpm build` clobbers the dev `.next` | `.next` is the named volume `system-news-dev_web_next_v2` and the dev container's entrypoint is `pnpm dev`; a build inside it overwrites the running build (this happened 2026-11-09 and 404'd every asset until wiped) | never run `pnpm build` in the dev container — use `docker compose run --rm --no-deps -v system-news-dev_web_next_prod_v2:/app/.next web` |

- Single VPS SPOF (R4); volume restore drilled, prd deploy/rollback not drilled.
- Feed licensing/terms (U11) and Spanish coverage (R17) remain owner inputs.
- The UI has ten channels/skins, a verified editorial-conversion v2 build, an **Approved** direction with all ten SPECs **approved**, a passed a11y milestone audit, shipped S0 primitives, and photographic bands on all ten channels. Storybook, the P1 primitives (`Skeleton`, `Toc`) and the vision tier remain open.
- Channel coverage is uneven at the edges, not empty: the thinnest locale is digital-technology ES (16 items), then retail ES (24). All eleven channels use licensed photos; profiles are applied to dev, not prd; legal/terms review (U11) still applies.
- The cybersecurity channel uses a dark scheme; fill/border contrast of the new conversion fields was checked visually, but the matrix is not yet in `check-themes.mjs`.
- Photo licences are recorded per file (`apps/web/public/photos/credits.json`); four channels are CC BY/BY-SA and depend on the in-caption credit staying rendered (financial, cybersecurity, stem-cell, plus retail, energy, manufacturing).
- AI summaries are fail-open; some items are intentionally left without a
  summary when validation rejects output.
- CI is written but has not run on GitHub yet.
- prd stack is up on 169.58.4.85 with the data restored; TLS and a rollback drill remain.
- `k6` and Lighthouse budgets are scripts only; no prd measurement yet.
- E2E runs against a production build; run `pnpm build` before `pnpm test`.
- AI validation intentionally rejects some provider output; those items publish
  without a summary.
- **Brief promise ahead of the system:** the weekly brief copy promises a Monday email; delivery lands before production (owner-owned). Until it exists, capture is ahead of fulfilment.
- **Asset scope is US + EU only.** No Asia source coverage, no JP/KR/ZH translation, and the logistics rate index is not buildable (licensed data) - replaced by a port/customs digest per the feasibility doc.
- **Empty archive on purpose:** `/{industry}/briefs` renders an honest empty state until the first issue publishes.

---

## Next action

M15, M16 and M17 are **complete**; the tree is verified but **uncommitted**. Run
`@code-verify uncommitted` before any commit. Owner lane: **O9** (production TLS on
`169.58.4.85`, also the prd half of M15-T6), **O15** (`SMTP_FROM` spelling), **O17**
(confirm the two added primary feeds). Agent follow-ups: read the next natural refresh for
D1–D5 (no forced reset, decision 3) and run one week of `FETCH_PACING=shadow` on prd.

## Cross-framework action (@x-director)

Lead generation remains integrated (ADR 013, FR-17): one primary CTA per page,
consent-first lead form, partner routing, DSAR export/erase, funnel events, and
lead dashboards/alerts. UI foundation and biz strategy docs remain in
`.work.ui/` and `.work.biz/`.

### 2026-11-05 — UI v2 via lead-generation reference intake

**Request:** "use x-director to improve the UI with the recently updated UI Agent OS Framework, using the lead-generation references/skills now available in 'ui' os" → "too many boxes, too many rounded corners... forms confusing... unbalanced columns".
**Frameworks involved:** `.ai`, `.ai.ui`
**Classified bucket(s):** cross-framework (ui primary; engineering for build/verify)
**Executed:**
1. `@ui-reference-intake scan/dna/synthesize` — `ellevest`, `hubspot`, `leadpages` → DNA docs + direction `editorial-conversion` (Approved 2026-11-05).
2. `@ui-component-build` (applied under operator's continue instruction) — open editorial layout, full-bleed bands, sharp corners, balanced CSS columns, per-channel CTA placement, filled forms.
3. Verification — production build; Playwright 57 passed / 1 skipped; `e2e/layout.spec.ts` 30 checks; 80 pages 200 + zero overflow; `pnpm lint/typecheck/check` green; token-lint 0 raw.
4. Operator approved the direction + bind package; composition tokens added to `tokens.json` (84, schema-valid); ten SPECs §13/§11 bound with `exampleIds: N/A` waiver; `SCREEN_REFERENCE_MAP.md` created; reference audit PASS.
5. `@ui-screen-spec review` run across all ten channels; 7 SPEC-vs-build mismatches amended in each §3/§4/§5/§8/§11/§12/§13; re-check PASS 10/10; all statuses `Review` (approval still operator’s).
6. Added `manufacturing`, `energy`, `retail`: profiles applied to dev, 45/45 sources verified, Forge/Grid/Market skins, three bound/reviewed SPECs; 57 e2e / 1 skipped; 80 pages 200 + no overflow.
7. Channel inventory is generated from the API (`docs/channel-inventory.md`, `bin/channels.sh`); `./bin/start.sh test` runs `--check` and fails on a stale list.
8. Visual fix after review: Sanctuary CTA opened (transparent, accent rule), skin-level hero/story radius+shadow removed, proof/conversion borders removed, health coverage moved to 2 balanced columns, Sentinel dark-scheme link/eyebrow contrast fixed; axe 11/11.
9. Visual verify milestone: pass with gaps; UIS-07 (ship_with_notes) + UIS-10 (ship) done; 40 layout checks, 11 axe pages; square-surface + no-motif regressions enforced.
**Coordination notes:** UI + channel data; no API/schema code changes. `.work.ui/` artifacts + `apps/web` code + `apps/api/config/deployments/*.json`; no protected files edited.
**Blockers:** none for the build; all ten SPECs are in `Review` pending operator approval.
**Next recommended:** approve the ten `Review` SPECs; close the new channels' content gaps; then `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-06
**Request:** "resolve all gaps"
**Frameworks involved:** .ai, .ai.ui (delegated to .ai; no ui-director run — the design rule was an operator decision, D-008)
**Classified framework bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc yes (unused) | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. `@ai-director` — R16 literal: `industries.cta.asset` (channel config) seeded by `apps/api/migrations/011_seed_asset_offers.sql`, profiles updated, `/v1/news/bundle` passthrough asserted in `test_bundle.py`; web resolves the card from `channel.cta.asset`. Decision D-009 supersedes D-007.
2. `@ai-director` (ui rule by operator decision D-008) — one secondary rung: the brief signup no longer renders where `cta.asset` is set; SPEC R16 amended; e2e asserts the rule on four channels.
3. `@ai-director` — plan traceability: M9 added to `.work/plans/full/20261105-full-plan.md` §19 (v1.2) with a traceability row; the waiver is now retired.
4. Re-verified: api 111 passed, web lint/type/check clean, migration 011 `applied: 1` then `applied: 0`, full Playwright 58 passed / 1 skipped / 1 failed.
**User correction:** none
**Coordination notes:** the design rule was taken natively (single-model) rather than routed to `@ui-director`; recorded so the routing is auditable.
**Blockers:** `layout.spec.ts:31` energy coverage balance fails on new content (330px vs 260) — not caused by M9 (ingestion at 16:03, after the 15:58 green run; energy renders neither card nor asset). Needs a separate layout decision.
**Next recommended:** `@code-implementation complete`, then `@session-control close commit` split in two (apps/, then `.work*`).

---

## Known residual risks

| Risk | Why it matters | Mitigation |
|------|----------------|------------|
| TLS reload not re-verified | the host rejected the first 443 config on duplicate session directives; the template is fixed, but `nginx -t`, reload and `certs --check` still need to pass | O9 is the first step next session |
| nginx config validated syntactically only | `nginx -t` passes but no request has gone through the real edge | `start.sh hosts` runs the same contract over HTTP once the host proxy is live |
| CI inventory gate unapproved | the step would run on the next PR before the owner signs off | listed as O10 |
| Brand string split | apex says **HeraldFox** (one word, owner 2026-11-09), channel footers still say System News | D-018 with a 2026-12-15 outcome date |
| Scheduler can park a channel | a run stuck in `queued`/`running` blocks that channel until a worker restart; orphan recovery runs only at start (`queue.py:42-63`, `repo.py:285-293`) | cadence verified 2026-11-09 (720 min, all 11 channels); sweep proposed in the M15 block |
| Emblem source PNG is 599 KB | `public/brand/heraldfox-emblem.png` is served raw wherever `next/image` is not used (footer/OG-less paths) | masthead + footer both use `next/image`; measured `naturalWidth=32` at render, so a resized variant is what ships |
| Favicon caching per origin | browsers cache `favicon.ico` per origin, so a re-derived icon needs a hard refresh on each of 11 subdomains | accept; re-check with a cache-busting query during verification |
| Tile colour `#0b1220` assumed | the derived `icon.png`/`apple-icon.png` are flattened on it; UI plan §5 decision 2 is still owner-open | measured corner is `srgb(11,18,32)`; re-derive if the owner picks another colour |
| Playwright output recompiles dev | `apps/web/test-results/` sits inside the bind-mounted `/app`; one write triggers a Next compile + "Fast Refresh had to perform a full reload", which can knock out a running test (pre-existing, gitignored) | clean `test-results/` before a suite run; run the gate suite against a **production** build in a throwaway container |
| `pnpm build` clobbers the dev `.next` | `.next` is the named volume `system-news-dev_web_next_v2` and the dev container's entrypoint is `pnpm dev`; a build inside it overwrites the running build (this happened 2026-11-09 and 404'd every asset until wiped) | never run `pnpm build` in the dev container — use `docker compose run --rm --no-deps -v system-news-dev_web_next_prod_v2:/app/.next web` |

- Single VPS SPOF (R4); volume restore drilled, prd deploy/rollback not drilled.
- Feed licensing/terms (U11) and Spanish coverage (R17) remain owner inputs.
- The UI has ten channels/skins, a verified editorial-conversion v2 build, an **Approved** direction with all ten SPECs **approved**, a passed a11y milestone audit, shipped S0 primitives, and photographic bands on all ten channels. Storybook, the P1 primitives (`Skeleton`, `Toc`) and the vision tier remain open.
- Channel coverage is uneven at the edges, not empty: the thinnest locale is digital-technology ES (16 items), then retail ES (24). All eleven channels use licensed photos; profiles are applied to dev, not prd; legal/terms review (U11) still applies.
- The cybersecurity channel uses a dark scheme; fill/border contrast of the new conversion fields was checked visually, but the matrix is not yet in `check-themes.mjs`.
- Photo licences are recorded per file (`apps/web/public/photos/credits.json`); four channels are CC BY/BY-SA and depend on the in-caption credit staying rendered (financial, cybersecurity, stem-cell, plus retail, energy, manufacturing).
- AI summaries are fail-open; some items are intentionally left without a
  summary when validation rejects output.
- CI is written but has not run on GitHub yet.
- prd stack is up on 169.58.4.85 with the data restored; TLS and a rollback drill remain.
- `k6` and Lighthouse budgets are scripts only; no prd measurement yet.
- E2E runs against a production build; run `pnpm build` before `pnpm test`.
- AI validation intentionally rejects some provider output; those items publish
  without a summary.
- **Brief promise ahead of the system:** the weekly brief copy promises a Monday email; delivery lands before production (owner-owned). Until it exists, capture is ahead of fulfilment.
- **Asset scope is US + EU only.** No Asia source coverage, no JP/KR/ZH translation, and the logistics rate index is not buildable (licensed data) - replaced by a port/customs digest per the feasibility doc.
- **Empty archive on purpose:** `/{industry}/briefs` renders an honest empty state until the first issue publishes.

---

## Next action

M15 and M16 are **complete**; the C+D tree is verified but **uncommitted**. Run
`@code-verify uncommitted` before any commit. Then the owner lane: **O9** (production TLS on
`169.58.4.85`, also the prd half of M15-T6), **O15** (`SMTP_FROM` spelling), **O16**
(`BOT_*`/`FETCH_*` in `.env.example`). Agent follow-ups: read the next natural refresh for
D1–D5 (no forced reset, decision 3), the availability gate (done 2026-11-10),
and run one week of `FETCH_PACING=shadow` on prd.

## Cross-framework action (@x-director)

**Date:** 2026-11-06
**Request:** "all approved - any questions you answer them with your recommendations - verify the uncomitted code, provide professional/valuable improvements to the system, make sure all is ready, completed, operational."
**Frameworks involved:** .ai, .ai.ui, .ai.biz
**Classified bucket(s):** engineering + ui + business (cross-framework)
**Executed:**
1. Verified the offer pipeline: 139 API tests, ruff/format/mypy, web lint/type/check, production build, and 6 admin Playwright tests.
2. UI: added the Offers tab (list, expand rows, build now, reviewer-gated publish/unpublish) and the public reference archive/detail pages, with EN/ES copy and e2e coverage.
3. Engineering hardening: invalid offer UUIDs return 404, source records are marked untrusted in the AI prompt, and the offer-inventory check now runs inside `./bin/start.sh test`.
4. Business: wrote the AI product catalog, recorded D-015 (one jurisdiction-tagged dataset, not one calendar per country), and updated the biz NEXT/UNKNOWNS/HANDOFF.
**Coordination notes:** the Offers tab consumes the admin API; publish is reviewer-gated and public pages only show published issues; no email path was added.
**Blockers:** named reviewers and email remain; EU/recall/energy adapters are not built.
**Next recommended:** review the drafts in the Offers tab, then choose the 7-Day Desk Brief or the public reference page as the next build.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-09
**Request:** "fix everything" → acked as "proceed as recommended, fix everything"
**Frameworks involved:** .ai, .ai.ui
**Classified framework bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc yes (framework source only — no `.work.soc/`) | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. `@ai-director - "fix everything"` → full plan §19 M15 gained the missing `M15-T8` row (it was done 2026-11-09 but absent from the plan), G1 traceability moved to `M15-T1..T8`, plan version 1.5 → 1.6 with a changelog line.
2. `@ui-director - "fix everything"` → `.work.ui/plans/20261109-brand-assets.md`: status header records the wordmark decision as answered, the "not tracked by git yet" claim corrected, derivation block ported from `magick` (IM7, not installed) to `convert` (IM6 6.9.11) with `-fuzz 2%` on the lockup trim, §2 lockup size corrected to 1265 × 921.
3. Verified by execution: all six derivation commands ran clean in `tmp/` (removed after use) — emblem 700 × 700 transparent, tile 512 × 512, favicon 48/32/16, icon 512, apple 180 opaque. `touch-scope-verify` pass · `traceability-verify` 17/17 FR · `blast-radius` medium (docs only) → MOD-06 run → **merge_ok**.
**User correction:** none
**Coordination notes:** both directors' domains were executed natively in one model pass (single-model, as on 2026-11-06) after the operator acked the routing plan; no application code touched — three planning files only, all inside `.work/touch-scope`.
**Blockers:** §5 decision 2 (tile colour, assumed `#0b1220`) still owner-open; O9 still blocks the prd half of M15-T6.
**Next recommended:** `@code-implementation start` (M15-T1..T7)

---

## Cross-framework action (@x-director)

**Date:** 2026-11-10
**Request:** "previous session was interrupted, verify the uncomitted changes, resolve any issues and blockers and gaps, starting with the plans: `.work/plans/20261109-next-improvement.md`, `.work/plans/full/20261105-full-plan.md`, `.work.ui/plans/20261109-brand-assets.md`"
**Frameworks involved:** .ai, .ai.ui
**Classified bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc yes (source only, no `.work.soc/`) | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. Plan audit before code: the C+D work existed in the tree while NEXT listed C0–C8/D1–D10 as `pending`, the full plan had no milestone for it, the fetch-safety SPEC still said `Draft` and asked for a decision answered on 2026-11-09, and the brand-assets plan still described M15 as not started. All four corrected; full plan v1.8 gains **M16** plus a traceability row.
2. Verification of the uncommitted tree: api **209 tests** (ruff, format, mypy clean), web **lint/tsc/check** (579 keys, 11/11 contrast), production **build RC=0**, Playwright **124 passed / 0 failed / 5 skipped** on that build, `hosts` **14/14**, `verify-sources` **50/50, 0 warnings**.
3. Six defects found and fixed: retail feed parse error (bare `&` in a title — `normalize.py` now escapes bare ampersands outside CDATA, 3 new tests); financial left at 3 sources after Finextra's robots retirement (Federal Reserve press releases added, profile applied, 4/4); `ingest_host_cooldown_seconds` never reset (R9); admin Sources table did not render the new `last_error`/cooldown fields (R10, +2 catalog keys); article-404 home link was `href=""` on channel hosts; and the plan drift above.
4. MOD-06 rerun for the C+D code: boundaries 4, human review required, **merge_with_conditions** — conditions recorded in `.work/plans/NEXT.md`.
**User correction:** none
**Coordination notes:** UI portion (brand surfaces, admin Sources row, reader copy) was executed natively under the same single-model pass; `.work.ui/plans/20261109-brand-assets.md` and `HANDOFF_UI` were updated to match what shipped. No protected file was edited; `.env*` changes stay with the owner (O15, O16).
**Blockers:** O9 (production TLS), O15 (`SMTP_FROM`), O16 (`BOT_*`/`FETCH_*` in `.env.example`); agent follow-ups are the D-trial read, a real `verify-sources` exit code, and a prd shadow week for pacing.
**Next recommended:** `@code-verify last` on `c6ce202` after the push.
**Delivered:** `c6ce202` — 53 files, M15 + M16, pushed 2026-11-10 with owner approval.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-10
**Request:** "forget about the Caddy-key drift, those keys must remain commented. IMPLEMENT ALL YOUR RECOMMENDATIONS TO INCREASE AVAILABILITY/ACCESSABIILTY/CONTENT-ACQUISITION FROM SOURCES, SHOULD YOU MAKE REQUESTS AS IF THE SYSTEM WAS A BROWSER OPERATED BY A HUMAN AS WELL?"
**Frameworks involved:** .ai, .ai.ui
**Classified bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc source-only | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. Caddy keys commented in `.env.example`, `.env.dev` and `.env.prd`; `env-sync verify` passes (the two lines were the only drift).
2. M17 built: migration 017 (permission + auth columns), `denied` outcome with a seven-day cooldown, 403-challenge detection, robots redirects validated per hop, permission snapshot (state/hash/date/delay) written by verify, per-source credentials and publisher-requested UA from env refs, availability floor in `verify-sources` (exits 1 below four healthy sources), admin Sources row, `/bot` allowlist block, CISA + SEC primary feeds.
3. Gates: api **218 passed**, web **583 keys**, build RC=0, Playwright **124/0/5**, `verify-sources` **52/52 rc=0**, migration re-run `applied: 0`.
4. Corrected a false claim carried since the C+D session: `verify-sources` always exited 1 on a failed source; the "exit 0" reading came from a piped command whose status was the pipe's. Fixed in five documents.
**User correction:** the owner asked whether the system should also present as a human-operated browser. Answer: no — implemented the legitimate alternative instead (per-source `User-Agent`/token from an env ref, publisher allowlisting on `/bot`). Reasoning recorded in the SPEC decisions.
**Coordination notes:** the UI half (admin permission/auth row, `/bot` allowlist copy) was executed natively in the same pass; `HANDOFF_UI` carries the note. `.env*` edits were explicitly requested in the same message.
**Blockers:** O17 (owner confirms the two added feeds); deploy needs the migration (automatic on start).
**Next recommended:** `@code-verify uncommitted`, then commit + push.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-10
**Request:** "Build the whole thing, let's make this awesome!" (the acquisition funnel proposed after "how can we improve the ability to acquire better and more sources")
**Frameworks involved:** .ai, .ai.ui
**Classified bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc source-only | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. M18: migration 018 (licence, outreach, outbound counter + index), discovery service (`discover.py`) and `sources discover`/`report`/`health`/`outreach` with `bin/sources.sh`.
2. Outbound traffic: `GET /v1/outbound/{id}` counts one click and 302s; web `/go/{id}` proxies it; the article link and the e2e assertion moved with it; OpenAPI snapshot regenerated.
3. Licence register: profile field + admin row; Federal Reserve, CISA and SEC set to `public-domain`, the rest stay `unknown`.
4. Gates: api **222 passed**, web **584 keys**, build RC=0, full Playwright on the rebuilt bundle, real discovery on three feeds, 302/404/counter check against Postgres.
5. Docs: `docs/source-acquisition.md`, `docs/source-quality.md`, `docs/deployment-profile.md`, SPEC `.work/features/source-acquisition/20261110-SPEC.md`.
**User correction:** none. O17 answered (keep both primary feeds) and recorded.
**Coordination notes:** the UI half (admin licence row, `/go` link) was executed natively in the same pass. `/go` is the only place the product sends readers off-site; the redirect target comes from the stored canonical URL, never from a query parameter.
**Blockers:** none. Owner lane is O9 (TLS) and O15 (`SMTP_FROM`).
**Next recommended:** `@code-verify uncommitted`, then commit + push M17 + M18.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-10
**Request:** "continue to implement all improvements on source acquisition"
**Frameworks involved:** .ai
**Classified bucket(s):** engineering
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes (untouched) | .ai.biz yes | .ai.soc source-only | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. M19 schema: `source_candidates` (unique feed URL, status, note, decision date) and `source_fetch_stats` (per source per day: attempts/ok/blocked/denied/items/duration).
2. Candidate flow: `discover --save`, `candidates list/decide`, profile snippet for an accepted row; a decided row is never reopened by re-discovery.
3. Similarity overlap: token Jaccard plus overlap coefficient, so a reworded headline counts; exact matches still land at 1.0.
4. Health: ingest writes the daily stat (wrapped so a stat failure cannot fail a fetch); `sources health` derives `success_rate_30d`/`avg_ms_30d` and reports `None` when there were no attempts.
5. `verify-sources` reports `robots_changed` when the stored hash differs; `sources export` prints OPML accepted by `discover`; `sources report` lists `missing_languages` per desk.
6. Verified: api **224 passed**, queue round-trip against dev, OPML round-trip test, migration re-run `applied: 0`.
**User correction:** none
**Coordination notes:** API-only iteration; no web build needed. The candidate queue is deliberately non-authoritative — the deployment profile remains the publishing record.
**Blockers:** none.
**Next recommended:** `@code-verify uncommitted`, then commit + push M19.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-10
**Request:** "PROCEED TO IMPLEMENT ALL OF YOUR 7 RECOMMENDATIONS"
**Frameworks involved:** .ai, .ai.ui
**Classified bucket(s):** cross-framework (engineering + ui)
**Routing confidence:** high
**Preflight (frameworks installed):** .ai yes | .ai.ui yes | .ai.biz yes | .ai.soc source-only | .ai.cto no | .ai.flutter no | .ai.mlt no
**Executed:**
1. Deploy item: `3a2a8b2` is on `origin/main` (push had already landed). prd migrations/TLS were NOT run: they need host access and a certificate; the commands are in `docs/domains.md`, and migrations 017–020 apply on the next `up`.
2. Licence enforcement: `Candidate.headline_only`; proprietary sources store no excerpt and get no summary (R11).
3. Overlap: `pg_trgm` extension + trigram index; `overlap_share` in SQL with the token matcher as fallback (R12).
4. Traffic page: `traffic_token`, `GET /v1/traffic/{token}`, `/traffic/<token>`, `sources traffic --source` (R13).
5. Queue refresh (R14), value/retirement rules (R15), JSON Feed (R16).
6. Verified: api **233 passed**, web build RC=0, live pg_trgm 1.0/0.0, token page 200 on the built app, NIST candidate refreshed, health proposals empty.
**User correction:** none
**Coordination notes:** the traffic page is English-only by design (publisher-facing); the licence rule is the only change that alters stored content.
**Blockers:** prd deploy/TLS remains an owner action; M20 is uncommitted pending approval.
**Next recommended:** `@code-verify uncommitted`, then commit + push M20.
