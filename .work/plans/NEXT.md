# NEXT - planning backlog

**Updated:** 2026-11-10 (session closed — M15–M20 delivered; deploy is the next move)

---

## Current iteration - Track C+D: fetch safety and content fixes (2026-11-09 → complete 2026-11-10)

**Milestone ref:** `.work/plans/20261109-next-improvement.md` Tracks C + D · full plan §19 **M16** · spec `.work/features/fetch-safety/20261109-SPEC.md` (**Implemented**)
**Status:** complete 2026-11-10 · **Started:** 2026-11-09 · **Scope delivered:** C0–C8 + D1–D5, D7–D10

### In scope

- **C0/R1** one `USER_AGENT` constant from settings, imported by both fetchers, no `example` domain left.
- **C1/R2** robots.txt once per host/day in Redis, `Disallow` → `robots_disallowed` with zero feed requests, `Crawl-delay` raises the floor.
- **C2/R3** per-host ledger in Redis: 5 s floor ±20 % jitter, 20/h cap, cooldown, fail streak, breaker.
- **C3/R4** `429`/`503` honour `Retry-After`, escalate per streak, never retry immediately.
- **C4** one retry for a dead socket only.
- **C5/R6** content-type allow-list + challenge-body detection → `challenge`.
- **C6/R8** pin the validated IP (Host header + `sni_hostname`).
- **C7** retire or fix the broken/stale sources; `verify-sources` clean.
- **C8/R9, R10** counters/gauge, run stats `blocked`/`rate_limited`/`robots_disallowed`, `partial` above 20 % blocked; admin source view carries `fail_streak`, `last_error`, cooldown + reason.
- **D1–D5** summary shape, banned phrases/verbs, opener rule, number preservation — prompt + `validate_summary`.
- **D7–D10** no "see link/URL/notes", human standfirst, one summary block, 404 archive window.

### Tasks

| ID | Description | Files | Status |
|----|-------------|-------|--------|
| C0 | Bot identity constant from settings, both fetchers import it | `platform/settings.py`, `articles/infrastructure/fetcher.py`, `offers/infrastructure/fetch.py` | done 2026-11-10 |
| C1 | robots.txt fetch + Redis cache + `Disallow` gate + `Crawl-delay` floor | `articles/infrastructure/politeness.py` | done 2026-11-10 |
| C2 | Per-host ledger: floor, jitter, hourly cap, streak, breaker | `politeness.py` | done 2026-11-10 |
| C3 | 429/503 cooldown from `Retry-After`, exponential escalation | `politeness.py`, `fetcher.py` | done 2026-11-10 |
| C4 | Retry budget: one retry on a dead socket, none on 429 | `fetcher.py` | done 2026-11-10 |
| C5 | Content-type allow-list + challenge detection | `fetcher.py` | done 2026-11-10 |
| C6 | Pin the approved IP across the request | `fetcher.py` | done 2026-11-10 |
| C7 | Broken/stale sources (repaired two, retired two, replaced one) | `normalize.py`, `config/deployments/{financial,digital-technology}.json` | done 2026-11-10 |
| C8/R9 | Metrics counters, gauge, run stats + `partial` threshold; admin cooldown fields | `ingest.py`, `metrics.py`, `editorial/http/sources.py`, `sources/infrastructure/repo.py`, `AdminConsole.tsx` | done 2026-11-10 |
| D1 | One summary shape in prompt + validator | `ai_client.py`, `config/prompts/{en,es}.json` | done 2026-11-10 |
| D2 | Banned stock phrases (EN+ES) → `retry` | `ai_client.py` | done 2026-11-10 |
| D3 | Opener rule ≤25 words, cap 3 sentences / 520 chars | `ai_client.py` | done 2026-11-10 |
| D4 | Banned vague verbs, require a concrete consequence | `ai_client.py` | done 2026-11-10 |
| D5 | Digit present when the source has one | `ai_client.py` | done 2026-11-10 |
| D7 | Forbid "see link/URL/notes" in generated copy | `ai_client.py` | done 2026-11-10 |
| D8 | Human standfirst, scope as a chip | `offers/application/build.py`, `offers/domain/models.py`, `config/offers.json` | done 2026-11-10 |
| D9 | One summary block, quiet fallback | article page, `messages/{en,es}.json` | done 2026-11-10 |
| D10 | 404 says 30-day archive, not seven days | `article/not-found.tsx`, `messages/{en,es}.json` | done 2026-11-10 |

### Done this iteration (evidence)

| Group | Artifact | Evidence |
|-------|----------|----------|
| Fetch safety | `articles/infrastructure/politeness.py` (new), rewired `fetcher.py`, `settings.py` bot/pacing keys, `offers/infrastructure/fetch.py` | 18 politeness tests (fake clock, no network) + fetcher tests for 429/HTML/rebinding; `verify-sources` 50/50 |
| Metrics + operator view | `platform/metrics.py`, `articles/application/ingest.py`, `editorial/http/sources.py`, `sources/infrastructure/repo.py`, `AdminConsole.tsx` | blocked/cooldown counters, run stats + `partial` >20 %, cooldown line + last error in the Sources table |
| Content | `ai_client.py` (D1–D5, D7), `config/prompts/{en,es}.json`, `offers/application/build.py` (D8), article page (D9), `article.not-found.tsx` (D10), catalogs | `test_summary_validation.py` + `test_standfirst.py`; e2e "a story without a summary…" and "a missing story…" |
| Crawler page | `apps/web/src/app/[locale]/bot/page.tsx` + catalog block | e2e EN + ES; no nav entry |

### Gaps found and fixed during verification (2026-11-10)

1. **Distribución Actualidad (retail) still failed** with `parse_error` after the entity repair: the title carries a bare `&` (`Óptica & Audiología`). `repair_html_entities` now escapes ampersands that do not open a legal reference, and splits CDATA out first so a literal `&` there is never printed as `&amp;`. Two new tests; retail 4/4.
2. **Financial fell below the 4-source policy minimum** after Finextra was retired by its robots file. Added `Federal Reserve Board` (press releases, trust 0.95) and applied the profile; financial 4/4.
3. **R9 gauge was never reset** on recovery — `ingest_host_cooldown_seconds` now sets 0 on success/4xx.
4. **R10 stopped at the API**: the admin Sources table did not render `last_error` or the cooldown. Added both, with `admin.cooldown` / `admin.lastError` keys in EN and ES (579 keys).
5. **Article 404 home link was empty on channel hosts** (`href=""` → back to the 404). Home now targets `/` (`/es` in Spanish); e2e asserts the href.

### Verification (2026-11-10)

| Gate | Command | Result |
|------|---------|--------|
| API lint/type/tests | `ruff check` · `ruff format --check` · `mypy src` · `pytest -q` (api container) | clean · **209 passed** |
| Web static | `pnpm lint` · `tsc --noEmit` · `pnpm check` | clean · **579 keys** · 11/11 contrast |
| Production build | `pnpm build` (throwaway container, `web_next_prod_v2`) | **RC=0** |
| Playwright | `pnpm exec playwright test` against that build | **124 passed / 0 failed / 5 skipped** |
| Routing | `./bin/start.sh --env dev hosts` | **all checks passed** (14 invariants) |
| Sources | `python -m news_api.cli verify-sources --industry all` | **50 sources, 50 passed, 0 failed, 0 warnings** |

Not verified: R10's seeded-cooldown acceptance (no cooldown seeded in dev; the render is covered by lint/tsc/build only), and D1–D5 on live output (the next natural refresh supplies the sample; no forced `--full-reset`).

### Owner blockers

- **O9** — production TLS; also keeps the prd half of M15-T6 open.
- **O15** — `SMTP_FROM` spelling in the protected `.env*` files.
- **O16** — approve `BOT_NAME`/`BOT_VERSION`/`BOT_URL`/`FETCH_PACING`/`FETCH_HOST_FLOOR_S`/`FETCH_HOST_HOURLY_CAP` in `.env.example`. The feature runs on the `settings.py` defaults without it.

### Follow-ups

- **D-trial** — read the first natural refresh batch after D1–D5 (decision 3: no forced reset).
- ~~`verify-sources` exit code~~ corrected 2026-11-10: it always returned 1 on a failed source; the "exit 0" reading came from a piped command. It now also fails below the availability floor.
- **prd shadow week** — `FETCH_PACING=shadow` for one week before trusting the pacing numbers.

### MOD-06 output (2026-11-10, Track C+D code)

## AI change risk summary
- AI-assisted: yes
- Boundaries crossed: 4 — ingestion fetch layer (new `politeness.py` + `fetcher.py`) → every channel's content; AI summary generation (`ai_client.py` + prompts) → every published article; offers builder/config → public reference pages; admin source API → admin console. Web routes (`/bot`, article 404) are additive.
- New cross-boundary deps: `fetcher.py` → `politeness.py` (Redis + httpx); `ingest.py` → `politeness.BLOCK_REASONS`; `AdminConsole` → the new source fields. No new module, RPC, shared model or DB dependency; no schema change.
- Test isolation: ok — pacing/cooldown/breaker: `pytest tests/unit/test_politeness.py` (18, fake clock, no network); fetch outcomes: `tests/unit/test_fetcher.py`; summary rules: `tests/unit/test_summary_validation.py`; standfirst: `tests/unit/test_standfirst.py`; reader copy: `pnpm exec playwright test e2e/public.spec.ts`; catalog parity: `pnpm check`.
- Human architectural review: required — reason: >1 hard boundary (MOD-06 §2). Read `politeness.py` (fail-open paths, lock release, breaker probe) and the `_pin_to_address` hunk in `fetcher.py` first: a mistake there stops every feed rather than one.
- Blast radius: if pacing or pinning is wrong, ingestion stalls across all 11 channels (freshness, no data loss); if `validate_summary` is too strict, summaries fail-open to the excerpt (visible per article); if the bot identity or robots gate is wrong, publishers see the wrong UA or we fetch a disallowed path (legal/relationship risk, invisible in tests); if the 404 href is wrong, dead-end navigation. The admin render only affects operators.

## Recommendation
merge_with_conditions — reason: gates are green (209 api tests, lint/tsc/check, build RC=0, Playwright 124/0/5, `hosts` 14, `verify-sources` 50/50) and each fetch-safety rule has a test with a fake clock; but the diff crosses four boundaries and one of them (pacing) fails site-wide, so MOD-06 routes it to human review rather than self-approval.

## Conditions if merge_with_conditions
- Human architectural review of `politeness.py` and the `_pin_to_address` path in `fetcher.py` before commit.
- One week in `FETCH_PACING=shadow` on prd before trusting the pacing numbers (rollout step 2).
- The D-trial sample is read before D1–D5 is called effective; the existing summaries are unchanged by design.
- `verify-sources` exit code made a real gate before C7 is treated as permanently green.

### Cross-LLM verification

Not run in this session; `@code-verify uncommitted` before any commit.

---

## Completed iteration - M20: acquisition quality (2026-11-10)

**Milestone ref:** full plan §19 **M20** · spec `.work/features/source-acquisition/20261110-SPEC.md` (extended, R11–R16)
**Status:** complete 2026-11-10 · 6/6 tasks

### In scope

- **R11** proprietary sources are headline + link only (excerpt dropped, no summary) at ingestion.
- **R12** overlap via `pg_trgm` with the token matcher as fallback.
- **R13** publisher traffic page: token per source, `GET /v1/traffic/{token}`, `/traffic/<token>`.
- **R14** `candidates refresh` re-grades the queue without touching decisions.
- **R15** `value_score` and `retirement_reason` in `sources health`.
- **R16** JSON Feed 1.x parsing and content types.

### Tasks

| ID | Description | Files | Status |
|----|-------------|-------|--------|
| M20-T1 | Licence enforcement (`headline_only`) | `articles/domain/models.py`, `articles/application/ingest.py` | done 2026-11-10 |
| M20-T2 | pg_trgm overlap + fallback | `migrations/020_acquisition_quality.sql`, `articles/infrastructure/repo.py`, `discover.py` | done 2026-11-10 |
| M20-T3 | Traffic token, summary, API, page, CLI | `sources/infrastructure/repo.py`, `publishing/http/traffic.py`, `app/traffic/[token]/page.tsx`, `cli.py` | done 2026-11-10 |
| M20-T4 | Candidate refresh | `discover.py`, `cli.py` | done 2026-11-10 |
| M20-T5 | Value score + retirement proposals | `sources/application/value.py`, `cli.py` | done 2026-11-10 |
| M20-T6 | JSON Feed + tests + OpenAPI | `normalize.py`, `politeness.py`, `tests/unit/*` | done 2026-11-10 |

### Verification (2026-11-10)

| Gate | Result |
|------|--------|
| api gates | clean · **233 passed** |
| web gates / build | 584 keys · RC=0 |
| pg_trgm | existing legal title `1.0`, unrelated `0.0` |
| traffic | token issued, `GET /v1/traffic/<token>` 200, page renders on the production build (`Reading record`, source name, clicks) |
| refresh | NIST candidate saved, re-graded `accept`, status untouched |
| health | `value_score` present; no retirement proposals on the current portfolio |
| JSON Feed | fixture parses; non-feed object rejected |

### MOD-06 output (2026-11-10, acquisition quality)

## AI change risk summary
- AI-assisted: yes
- Boundaries crossed: 3 — ingestion (licence) → every reader surface; discovery → Postgres (`pg_trgm`); sources repo → a new public route and page.
- New cross-boundary deps: `ingest` → `Candidate.headline_only`; `discover` → `overlap_share`; `traffic` → `sources.traffic_token`. The `pg_trgm` extension is a database capability, not a service.
- Test isolation: ok — licence: `test_licence.py`; JSON Feed: `test_normalize.py`; value rules: `test_value.py`; overlap: live SQL check plus token fallback tests.
- Human architectural review: required — reason: a public tokenised page and a licence rule that changes stored content. Read `traffic_summary` (only own numbers, no ids) and `_feed_candidates` before deploy.
- Blast radius: if the licence rule is wrong, a proprietary source loses its excerpt or keeps one it should not; if the token page leaks, it exposes one source's aggregate counts; if pg_trgm is missing, discovery falls back and stays correct.

## Recommendation
merge_with_conditions — reason: gates green, but the licence rule changes what is stored and the traffic page is public by design.

## Conditions if merge_with_conditions
- Confirm no source is currently `proprietary` that depends on its excerpt (the portfolio sets `public-domain` for three and `unknown` for the rest).
- The traffic page is English-only by design; localise it if publishers ask.

### Cross-LLM verification

Not run in this session.

---

## Completed iteration - M19: acquisition pipeline (2026-11-10)

**Milestone ref:** full plan §19 **M19** · spec `.work/features/source-acquisition/20261110-SPEC.md` (extended, R7–R10)
**Status:** complete 2026-11-10 · 5/5 tasks

### In scope

- **R7** candidate queue: `discover --save`, `candidates list/decide`, decisions never reopened by re-discovery.
- **R8** `source_fetch_stats` per source per day, written by ingest, feeding `success_rate_30d` / `avg_ms_30d`.
- **R9** `robots_changed` warning when a source's robots text differs from the stored hash.
- **R10** `sources export` OPML (round-trips through `discover`); `missing_languages` per desk.

### Tasks

| ID | Description | Files | Status |
|----|-------------|-------|--------|
| M19-T1 | Migration 019: candidate queue + per-source daily stats | `migrations/019_acquisition_pipeline.sql` | done 2026-11-10 |
| M19-T2 | Candidate repo + decide/snippet; discovery `--save` | `sources/infrastructure/repo.py`, `sources/application/discover.py` | done 2026-11-10 |
| M19-T3 | Similarity overlap (Jaccard + containment) | `sources/application/discover.py` | done 2026-11-10 |
| M19-T4 | Ingest writes fetch stats; health derives rates | `articles/application/ingest.py`, `sources/infrastructure/repo.py` | done 2026-11-10 |
| M19-T5 | Robots-change warning, OPML export, language gaps | `sources/application/verify.py`, `sources/application/portfolio.py`, `cli.py` | done 2026-11-10 |

### Verification (2026-11-10)

| Gate | Result |
|------|--------|
| api gates | clean · **224 passed** (6 discovery tests) |
| queue round-trip | save → list → decide → snippet against dev |
| export | OPML printed; `discover` reads it back (unit test) |
| health | `attempts_30d` 0 → `success_rate_30d` `None`, no fake number |
| migrations | 019 applied; re-run `applied: 0, total: 19` |

Web untouched this iteration (no rebuild needed).

### MOD-06 output (2026-11-10, acquisition pipeline)

## AI change risk summary
- AI-assisted: yes
- Boundaries crossed: 2 — sources schema/repo → CLI; ingest → stats table.
- New cross-boundary deps: `ingest._one` → `record_fetch_stat`; `sources health` → `source_fetch_stats`. No new service.
- Test isolation: ok — parsing/overlap/OPML: `tests/unit/test_discover.py`; queue and stats exercised against dev with rollback-free rows.
- Human architectural review: optional — reason: additive tables, no public surface, no credential path.
- Blast radius: a wrong stat write cannot stop a fetch (wrapped and logged); a wrong queue update only affects the candidate list.

## Recommendation
merge_ok — reason: additive schema, no public route change, gates green.

## Conditions if merge_with_conditions
- none — merge_ok.

### Cross-LLM verification

Not run in this session.

---

## Completed iteration - M18: source acquisition (2026-11-10)

**Milestone ref:** full plan §19 **M18** · spec `.work/features/source-acquisition/20261110-SPEC.md` (**Implemented**) · guide `docs/source-acquisition.md`
**Status:** complete 2026-11-10 · 6/6 tasks

### In scope

- **R1** `sources discover`: URL list or OPML, permission → quality → novelty → fit, read-only, prints a profile snippet.
- **R2** overlap: exact-title ratio against the desk's last 30 days; `> 50 %` → `review`.
- **R3** `licence_type` per source, settable from the profile, shown in admin; government feeds set to `public-domain`.
- **R4** outreach: `contacted_at` + `outreach_note` via `sources outreach`, shown in admin.
- **R5** return traffic: `GET /v1/outbound/{article_id}` counts one click and 302s; web `/go/{id}` proxies it.
- **R6** `sources report` (portfolio) and `sources health` (per-source items/clicks/failures, `needs_attention`).

### Tasks

| ID | Description | Files | Status |
|----|-------------|-------|--------|
| M18-T1 | Migration 018: licence, outreach, outbound counter, source index | `migrations/018_source_acquisition.sql` | done 2026-11-10 |
| M18-T2 | Discovery service: parsing, robots, quality, overlap, verdict | `sources/application/discover.py` | done 2026-11-10 |
| M18-T3 | `sources` CLI: discover/report/health/outreach + `bin/sources.sh` | `cli.py`, `bin/sources.sh` | done 2026-11-10 |
| M18-T4 | Outbound endpoint + `/go` route + article link | `publishing/http/outbound.py`, `app/go/[id]/route.ts`, article page | done 2026-11-10 |
| M18-T5 | Licence in profiles + admin row | `provisioning/**`, `AdminConsole.tsx`, catalogs | done 2026-11-10 |
| M18-T6 | Tests, OpenAPI snapshot, docs, `docs/source-acquisition.md` | `tests/unit/test_discover.py`, `docs/api/openapi.v1.json` | done 2026-11-10 |

### Verification (2026-11-10)

| Gate | Result |
|------|--------|
| api gates | clean · **222 passed** |
| web gates | clean · 584 keys |
| `pnpm build` / Playwright | RC=0 · **124 passed / 0 failed / 5 skipped** (outbound assertion added) |
| `sources discover` (real) | BBC business accepted; CISA and The Register rejected as configured; robots/quality paths exercised |
| outbound | 302 to the publisher, `Cache-Control: no-store`, unknown id 404, `outbound_clicks` 0 → 1 |
| OpenAPI | snapshot regenerated; one new path |

### MOD-06 output (2026-11-10, source acquisition)

## AI change risk summary
- AI-assisted: yes
- Boundaries crossed: 3 — sources schema/repo → CLI and admin; publishing HTTP → every outbound link; web route → API.
- New cross-boundary deps: article page → `/go`; `/go` → `/v1/outbound`; discovery → articles repo (`recent_titles`).
- Test isolation: ok — parsing/overlap: `tests/unit/test_discover.py`; outbound: e2e 302 assertion; API route: manual 302/404/counter check.
- Human architectural review: required — reason: a public redirect endpoint and a click counter. Read `record_outbound_click` (status gate, no PII) before deploy.
- Blast radius: if the redirect is wrong, every outbound story link leaves the site to the wrong place; if the counter is wrong, publisher conversations quote a wrong number. No write path to content.

## Recommendation
merge_with_conditions — reason: gates green and the new surfaces are small, but the outbound route is the only place the product sends readers off-site.

## Conditions if merge_with_conditions
- Human read of `publishing/http/outbound.py` and `app/go/[id]/route.ts` (open-redirect surface: only DB-stored canonical URLs are returned).
- Owner confirms the counter wording when quoting traffic to a publisher ("clicks we counted", not "visitors").

### Cross-LLM verification

Not run in this session.

---

## Completed iteration - M17: source availability and permission (2026-11-10)

**Milestone ref:** full plan §19 **M17** · spec `.work/features/source-availability/20261110-SPEC.md` (**Implemented**)
**Status:** complete 2026-11-10 · 7/7 tasks · `verify-sources --industry all` **52/52, unavailable 0**

### In scope

- **R1** `401`/`403` → `denied`, seven-day host cooldown, no fail-streak escalation.
- **R2** a `403` challenge body → `challenge` (one-hour cooldown), not a generic error.
- **R3** permission ledger: `permission_state`, `robots_checked_at`, `robots_hash`, `robots_crawl_delay`.
- **R4** licensed feeds: `auth_type`/`auth_header_name`/`auth_secret_ref` (env name, never the secret); per-source UA when a publisher asks.
- **R5** availability floor: four healthy sources per channel, CLI exits 1 below it.
- **R6** primary sources first: CISA News, SEC Press Releases added.
- **R7** publisher kit on `/bot`: allowlisting and opt-out paths.

### Tasks

| ID | Description | Files | Status |
|----|-------------|-------|--------|
| M17-T1 | Migration 017 + domain + repo permission/auth fields | `migrations/017_source_permissions.sql`, `sources/domain/models.py`, `sources/infrastructure/repo.py` | done 2026-11-10 |
| M17-T2 | Denial outcomes and the 403 challenge check | `fetcher.py`, `politeness.py`, `settings.py` | done 2026-11-10 |
| M17-T3 | Robots redirects validated hop by hop + snapshot hash | `politeness.py` | done 2026-11-10 |
| M17-T4 | Credentials and per-source UA from the environment | `fetcher.py` | done 2026-11-10 |
| M17-T5 | Verify run writes the ledger and gates availability | `sources/application/verify.py`, `cli.py` | done 2026-11-10 |
| M17-T6 | Profiles carry auth; CISA + SEC added; admin shows permission/auth | `provisioning/**`, `config/deployments/{cybersecurity,financial}.json`, `AdminConsole.tsx` | done 2026-11-10 |
| M17-T7 | Publisher allowlist block on `/bot`, EN + ES | `app/[locale]/bot/page.tsx`, catalogs | done 2026-11-10 |

### Verification (2026-11-10)

| Gate | Result |
|------|--------|
| api `ruff`/`format`/`mypy`/`pytest` | clean · **218 passed** |
| web `lint`/`tsc`/`check` | clean · 583 keys · 11/11 contrast |
| `pnpm build` | RC=0 |
| `verify-sources --industry all` | **52 sources, 52 passed, unavailable 0, 0 warnings** |
| migration 017 | applied on start; re-run `applied: 0, total: 17` |
| profiles | both applied; second apply 0 created |
| admin payload | permission/auth fields present (no secret, only the env reference) |

### Gaps found and fixed

1. **The "verify-sources exits 0 on failure" claim was false.** `cli.py` always returned 1 on a failed source; the earlier reading came from a piped command whose exit status was the pipe's last stage. Corrected in the fetch-safety SPEC, the improvement plan, HANDOFF, NEXT and `docs/source-quality.md`. The gate now also fails below the availability floor.
2. **Robots redirects were read as "no rules"** (non-following client). Now followed by hand, max 3 hops, every hop re-validated.
3. **`FETCH_DENIED_COOLDOWN_S`** joins the empty→default guard, so an empty env line cannot break startup.

### MOD-06 output (2026-11-10, source availability)

## AI change risk summary
- AI-assisted: yes
- Boundaries crossed: 4 — sources schema/domain/repo → provisioning and admin; fetcher/ingest → every channel's content; verify CLI → CI gate; web copy → publisher-facing page.
- New cross-boundary deps: `verify.py` → `politeness.robots_snapshot`; `fetcher.py` → `os.environ` by `auth_secret_ref`; `AdminConsole` → the new admin fields. No new service, no new secret store.
- Test isolation: ok — denials/credentials/UA: `tests/unit/test_fetcher.py`; robots redirect + snapshot + denied cooldown: `tests/unit/test_politeness.py`; empty env guard: `tests/unit/test_settings.py`.
- Human architectural review: required — reason: a schema migration plus a credential path. Read `_auth_headers` (env ref handling, no logging of values) and migration 017 before deploy.
- Blast radius: if the migration is wrong, the API cannot start; if `auth_secret_ref` resolution is wrong, licensed feeds break and log the variable name (not the value); if the availability floor is too strict, CI fails while the site is fine.

## Recommendation
merge_with_conditions — reason: gates green and the risky paths are small and tested, but the migration and the credential path deserve a human read before deploy.

## Conditions if merge_with_conditions
- Human review of migration 017 and `_auth_headers` before deploy.
- Owner confirms CISA News and SEC Press Releases as acceptable desks' sources.
- prd needs the migration applied on restart (automatic) and `BOT_*`/`FETCH_*` keys present or empty (defaults now apply).

### Cross-LLM verification

Not run in this session.

---

## Completed iteration - M15: brand surfaces (2026-11-09)

**Milestone ref:** `.work/plans/full/20261105-full-plan.md` §19 M15 · spec `.work.ui/plans/20261109-brand-assets.md`
**Status:** complete 2026-11-09 · **M15-T1..T8 done** (T6 prd half still open on **O9**) · `@code-verify milestone` verdict **pass with gaps**

### In scope

- derive emblem, lockup and icon tile from `.work.ui/references/heraldfox-final.png` (one-off, assets committed).
- apex masthead and footer use the emblem plus the live wordmark; the 10 px CSS square retires.
- `favicon.ico`, `icon.png`, `apple-icon.png` under `apps/web/src/app/`, discovered by the App Router.
- accessible names: decorative marks `aria-hidden`, brand link keeps one label; axe assertion at the apex.
- per-host verification on dev, and on prd once O9 unblocks the https path.

### Out of scope (explicit)

- channel headers (they keep `SkinEmblem`), per-desk favicons, a PWA manifest.
- the brand string itself (D-018: "HeraldFox" on the logo, "Herald Fox" in the lobby copy, "System News" in channel headers). This iteration renders the existing copy, it does not rename anything.
  - **Updated 2026-11-09 (owner):** "HeraldFox" is one word, never "Herald Fox" — applied to the lobby catalogs, `bin/start.sh` and the notify fixture. `SMTP_FROM` in `.env.example`/`.env.dev`/`.env.prd` still reads "Herald Fox" (protected surfaces, needs same-message approval). Channel headers / `meta.siteName` still say "System News" (D6/U1, untouched).
- the OG image, the fetch-safety work, and the ten content fixes (separate tracks).

### Acceptance criteria (measured 2026-11-09)

- [x] logo renders on `/`, `/es`, `/services` at 360 px and 1440 px; no horizontal overflow, **CLS 0.0000** on all six combinations.
- [x] `/favicon.ico` returns 200 `image/x-icon` on apex and every subdomain checked; **`<link rel="icon" href="/favicon.ico">` appears exactly once** per document.
  - *Wording gap (low):* the plan says "exactly one `<link rel="icon">`"; the document carries **2** `rel="icon"` elements (favicon.ico ×1 + icon.png ×1, both auto-emitted, each exactly once). Reported literally, not rounded to pass.
- [x] apple icon opaque (100 %, corner `srgb(11,18,32)`); the 16 px tab icon still reads as the fox (mean 0.28, max 1).
- [x] axe 0 critical/serious on the three apex URLs; the brand link has one accessible name.
- [x] two subdomains serve the same icon — checked on **three** (`stem-cell.`, `financial.`, `legal.localhost`), byte-identical to the apex. prd after O9.

### Validation steps

```bash
docker compose --env-file .env.dev -f docker-compose.dev.yml exec web bash -c "cd /app && pnpm lint && pnpm exec tsc --noEmit && pnpm check"
docker compose --env-file .env.dev -f docker-compose.dev.yml exec web bash -c "cd /app && pnpm build && pnpm test"
docker compose --env-file .env.dev -f docker-compose.dev.yml exec web bash -c "cd /app && pnpm exec playwright test e2e/accessibility.spec.ts"
docker compose --env-file .env.dev -f docker-compose.dev.yml exec web sh -c "wget -S -qO /dev/null http://127.0.0.1:3000/favicon.ico 2>&1 | head -3"
```

### Owner blockers

- **O9** — production TLS is unfinished, so the prd half of M15-T6 cannot run yet. The dev half is unblocked.

### Cadence check (owner instruction 2026-11-09)

All 11 channels refresh twice a day as configured: `refresh_interval_minutes = 720` (`platform/settings.py:43`), no per-channel override (`fetch_interval_minutes` NULL on every row, 2026-11-07 bundle), `auto_fetch_enabled` true on every row, and `scheduler_tick` runs every 30 s (`worker.py:53-56`) with a 0-10 min per-slug stagger (`queue.py:145-147`).
Residual risk, not fixed here: `active_run` treats `queued` and `running` as active (`articles/infrastructure/repo.py:285-293`) and orphan recovery runs only at worker start (`queue.py:42-63`), so a run stuck in either state parks that channel until the worker restarts. Proposed one-liner: sweep runs older than `2 × interval` inside `scheduler_tick` and mark them failed. Not in this iteration — needs a decision.

### Cross-LLM verification

Not run in this session; `@code-verify uncommitted` before any commit.

### Done this iteration

| ID | Description | Completed |
|----|-------------|-----------|
| M15-T1 | Emblem 700×700 transparent, lockup 1265×921 (`convert -fuzz 2%`), tile 512 opaque, from `.work.ui/references/heraldfox-final.png` | 2026-11-09 |
| M15-T2 | Masthead: emblem 32 px (`28 px` < 480 px) + live wordmark; `.lb-brand-mark` CSS square retired (0 leftovers) | 2026-11-09 |
| M15-T3 | Footer emblem 24 px in `LobbyFooter`, same link target, no second landmark | 2026-11-09 |
| M15-T4 | Marks `alt=""` + `aria-hidden="true"`; axe assertions on `/`, `/es`, `/services` (one name, emblem loads, no `footer h1`) | 2026-11-09 |
| M15-T5 | `favicon.ico` (48/32/16), `icon.png` (512), `apple-icon.png` (180, **100 % opaque**) via file-based metadata, no `metadata.icons` | 2026-11-09 |
| M15-T6 (dev) | `start.sh hosts` **14/14** incl. *the lobby carries the brand*; `favicon.ico` 200 `image/x-icon` + exactly one `favicon.ico` link per document on apex EN/ES, `stem-cell.`, `financial.`, `legal.localhost`; apex vs subdomain bytes **identical**. **prd half → O9** | 2026-11-09 |
| M15-T7 | lint ✔ · tsc ✔ · check ✔ (567 keys, 11/11 contrast) · `pnpm build` **RC=0** · Playwright **120 passed / 0 failed / 5 skipped, exit 0** on the production build · axe 0 critical/serious · 360/1440 px × `/`,`/es`,`/services`: overflow 0, **CLS 0.0000** | 2026-11-09 |
| M15-T8 | Responsive fix: desk board keeps three columns (languages dropped by owner), table kept, no clipped cells 320-1440 px; masthead wraps < 720 px; lobby e2e 13/13 | 2026-11-09 |
| Brand spelling | "HeraldFox" is one word everywhere the brand appears (owner instruction 2026-11-09): EN/ES catalogs (5× each), `bin/start.sh:735` brand check, api notify fixture. `SMTP_FROM` in `.env.*` **not** changed (protected surface, needs same-message approval) | 2026-11-09 |

### Plan verification (2026-11-09, @x-director)

Four drifts found and fixed before implementation:

1. Full plan §19 M15 had no `M15-T8` row although NEXT marks T8 done → row added, G1 traceability now `M15-T1..T8`, plan version 1.5 → 1.6.
2. `.work.ui/plans/20261109-brand-assets.md:3` still asked for the wordmark pick → decision 1 recorded as answered (2026-11-09, emblem + live text); §5 decision 2 (tile colour) stays owner-open.
3. The same file claimed the source art was untracked → it is tracked (`.work.ui/references/heraldfox-final.png`, `f71bfd3`).
4. The derivation block used `magick` (absent on this host) and a plain `-trim` (leaves the full 1510 × 1024 canvas) → `convert` + `-fuzz 2%`; all six commands smoke-tested in `tmp/`: emblem 700 × 700 transparent, lockup 1265 × 921, tile 512 × 512, favicon 48/32/16, icon 512, apple 180 opaque.

Gates: `touch-scope-verify` pass · `blast-radius` medium (docs only, 2 areas) · `traceability-verify` 17/17 FR · **MOD-06 → merge_ok** (boundaries 0, deps none, test isolation n/a for docs).

### Concept / NFR registry (this iteration)

| Concept | Applies | Status | Reason |
|---------|---------|--------|--------|
| MOD-01 coupling-audit | no | n/a | lobby presentation → i18n catalog → routing is 3 boundaries, but MOD-06 is the code gate; MOD-01 not triggered by this milestone |
| MOD-02 network-cost | no | n/a | no new network hop; static assets served by the existing origin |
| MOD-03 cost-model | no | n/a | no new billable unit |
| MOD-04 ops-headcount | no | n/a | no new deployable or on-call surface |
| MOD-05 modularity-vs-distribution | no | n/a | no service boundary change |
| MOD-06 ai-amplification | **yes** | **done** | agent-authored code — output below (2 sections: plan-drift docs + M15 code); `mod06-output-check.sh` pass on both |
| MOD-07 prompt-architecture | no | n/a | no prompt change in this iteration (that is the content track) |
| MOD-08 declarative-infra | no | n/a | no infrastructure change |

### MOD-06 output (2026-11-09, plan-drift fixes)

## AI change risk summary
- AI-assisted: yes
- Boundaries crossed: 0 — planning and session artifacts only (`.work/`, `.work.ui/` memory trees; no code module touched)
- New cross-boundary deps: none
- Test isolation: n/a (no code) — command: `bash $AGENT_OS_SOURCE/scripts/traceability-verify.sh` → `17/17 FR ids map to a task`; `touch-scope-verify.sh` → pass
- Human architectural review: optional — reason: documentation-only diff, no module or service boundary moves
- Blast radius: if wrong, the master plan's M15 task table and the G1 traceability row mislead the next iteration, and the brand-asset derivation commands fail at M15-T1 (caught now by the smoke test); no runtime, data or user-facing surface is touched.

## Recommendation
merge_ok — reason: five planning/session files, all inside `.work/touch-scope`; gates green (touch-scope pass, traceability 17/17, blast medium = docs only, all six derivation commands smoke-tested).

## Conditions if merge_with_conditions
- none — the recommendation is `merge_ok`.

### MOD-06 output (2026-11-09, M15 brand surfaces — code)

Inputs: 8 files, +98/−24 (`shell.tsx`, `lobby.css`, `en.json`, `es.json`, `middleware.ts`, `accessibility.spec.ts`, `test_notify.py`, `start.sh`) plus static assets under `public/brand/` and `src/app/`. Boundaries map: lobby presentation (`components/lobby/*`), shared i18n catalog (`messages/*`), request routing (`middleware.ts`), e2e suite, api unit test, ops script. Isolating commands per area below.

## AI change risk summary
- AI-assisted: yes
- Boundaries crossed: 3 — lobby presentation → shared i18n catalog (both locales read by lobby *and* channel chrome); shared i18n catalog → request routing (`middleware.ts` matcher affects every URL on every host); app code → e2e/api-test/ops assertions (`accessibility.spec.ts`, `test_notify.py`, `start.sh` expect the new strings)
- New cross-boundary deps: `shell.tsx` → `next/image` (new import; served via `/_next/image`, excluded from the matcher); no new module, RPC, shared-model or DB dependency
- Test isolation: ok — lobby/brand: `pnpm exec playwright test e2e/accessibility.spec.ts e2e/lobby.spec.ts` (fails only if the mark or its name is wrong); routing: `./bin/start.sh hosts` (14 checks) + curl matrix over 13 paths and 2 hosts; catalog: `pnpm check` (567-key parity, fails on any key drift); notify fixture: `pytest tests/unit/test_notify.py` (12 tests)
- Human architectural review: required — reason: >1 hard boundary (per MOD-06 §2, not waived); the `middleware.ts` matcher is the one to read closely, since a bad negative-lookahead either 404s static assets or rewrites a page into `/en/<path>`
- Blast radius: if the emblem or wordmark is wrong, every apex page in both locales shows a broken mark (cosmetic, no data). If the brand string is wrong it lands in `<title>`, the privacy/terms bodies and the brand link's accessible name — SEO and legal copy, visible immediately. If the matcher is wrong, `/_next/static` and the brand assets 404 and the site renders unstyled on **all** hosts, or a channel route stops resolving. The api fixture and `start.sh` check can only fail their own assertions. No write path, job, migration or PII surface is touched.

## Recommendation
merge_with_conditions — reason: gates green (lint, tsc, check, build RC=0, Playwright 120/0/5 on the production build, axe 0 critical/serious, `start.sh hosts` 14/14) and the routing blast radius is verified by an explicit 13-path × 2-host status matrix rather than assumed; but the diff crosses three boundaries, which MOD-06 routes to human architectural review rather than self-approving.

## Conditions if merge_with_conditions
- Human architectural review of `apps/web/src/middleware.ts` (the matcher negative-lookahead) before commit — it is the only hunk whose failure is site-wide rather than cosmetic.
- prd half of M15-T6 stays open until **O9** (production TLS) — do not record T6 as fully closed on the strength of the dev half alone.
- `SMTP_FROM` in `.env.example`/`.env.dev`/`.env.prd` still reads "Herald Fox"; protected surfaces, change only with owner approval in the same message.
- Residual (unchanged, owner decision pending): tile colour `#0b1220` (UI plan §5 decision 2) and the "System News" channel strings (D6/U1).

---

## Done

| Item | Artifact |
|------|----------|
| Source availability (M17) | permission ledger, `denied`/`challenge` outcomes, licensed-feed auth, availability gate, `/bot` allowlist block |
| Source acquisition (M18) | `sources discover` + overlap, licence/outreach register, `/go` click counting, portfolio health |
| Acquisition pipeline (M19) | candidate queue, per-source fetch history, robots-change warning, OPML round-trip, language gaps |
| Acquisition quality (M20) | licence enforcement, pg_trgm overlap, publisher traffic page, queue refresh, value/retirement, JSON Feed |
| Fetch safety (M16) | `politeness.py`, fetcher rewiring, bot page, profile repairs; `verify-sources` 50/50, `hosts` 14/14, 18 ledger tests |
| Content fixes (D1–D5, D7–D10) | prompt + validator rules, offer standfirst, one summary block, 30-day 404 copy; e2e + unit coverage |
| M15 plan-drift fixes | full plan v1.6 (`M15-T8` row + G1 `M15-T1..T8`); brand-assets plan header/tracked-art/derivation corrected and smoke-tested; MOD-06 → merge_ok |
| Apex responsive fix | Board keeps its table at 3 columns (languages dropped) and stops clipping the last column at 1024-1440 px; masthead wraps under 720 px; regression test in `e2e/lobby.spec.ts` |
| Email transport | `start.sh`/settings gateway lane, `info@links.heraldfox.com`, delivered with DKIM/DMARC pass |
| Restore hardening | `init-env` DB/Redis passwords + URL sync, preflight email lane, menu restore `--all`, bundle drill |
| Production stack | `vmi3435240` (169.58.4.85): stack up, data restored, HTTP-only nginx; TLS template fix |
| Footer credit | LogicBison mark + wordmark on channel, lobby and admin footers; 567 keys |
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
| Channel subdomains (ADR 015) | one host per desk, `start.sh hosts` 14/14, per-host canonical/sitemap/robots/RSS |
| Host nginx edge | `ops/nginx/site.conf.template`, `start.sh domains [--write|--http-only]`, `certs [--check|--run]`, `docs/domains.md` |
| Dev→prd bundle | `start.sh backup` (pg_dump + config + env + media + nginx + manifest) / `restore [--all]`; `docs/guides/migrate-dev-to-prod.md` |
| Preflight | `start.sh preflight`: secrets, https base URL, cert, ports, DNS |
| Apex lobby (ADR 016) | `/`, `/services`, `/privacy`, `/terms`, `GET /v1/desks`, migration 016, `e2e/lobby.spec.ts` |
| Lobby copy | 140 `lobby.*` keys EN/ES, parity-gated; deck `.work.biz/strategy/20261107-lobby-copy.md` |
| Lobby review | four defects from owner screenshots fixed; contact form added (D-020); "no ads" claims replaced (D-021) |
| Channel inventory gate | environment-free block, live/profile fallback, CI check |
| Log noise | outcome-based request logging, probes silent, uvicorn `--no-access-log`, dev rotation |
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
| Promotion copy (D-021) | The absolute "no ads" promise is gone from four surfaces (`lobby.faq.a7`, `proof.independentValue`, `brief.value2`, `asset.note`); replaced with the house-first, one-slot, labelled ceiling |
| Lobby contact form (D-020) | Same form and endpoint as every channel contact page, no industry attached; section 07, linked from masthead, spine and footer; e2e covers the submit |
| Log noise control | Request logging is by outcome: 5xx error, 4xx warning, slow info, success debug; probes (`/v1/health`, `/metrics`) silent unless they fail; uvicorn `--no-access-log`; dev containers get 10m x 3 rotation. Idle stack: 0 lines per 30 s, down from ~137 lines/min |
| Apex lobby review round 2 | Colour audit over every text node on six apex pages: 0 failures below 4.5:1 (dev + prod image). Fixed the "0 desks" copy when the API fails; disabled channels verified absent from `/v1/desks`, the lobby and the sitemap, with a contract test |
| Apex lobby review round | Fixed: anchor-colour specificity (CTA/skip invisible), page-relative section links on `/services` and legal pages, literal `{desks}`, form-field contrast; regression tests in `e2e/lobby.spec.ts` |
| Apex lobby (ADR 016) | `GET /v1/desks`, migration 016 (`surface`, `desk_enter`), apex `/` + `/services` + `/privacy` + `/terms`, `components/lobby/*` with the measured palette, 140 `lobby.*` keys in EN/ES, service inquiry via `/v1/contact`, `e2e/lobby.spec.ts` + 6 apex URLs in the axe sweep |
| Channel inventory | `docs/channel-inventory.md`: subdomain addresses, environment-free so it checks anywhere; generated from `/v1/industries` with a deployment-profile fallback; gated by `./bin/start.sh migrate` (warn), `./bin/start.sh test` (fail) and CI (fail, no server needed) |
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
| Channel subdomains (prod) | ADR 015 · `apps/web/src/lib/hosts.ts` + `url.ts` + `middleware.ts` · one host per channel, clean links, per-host canonical/sitemap/robots/RSS, apex compat URLs |
| Subdomains in dev | `SN_CHANNEL_DOMAIN=localhost` in `.env.dev`; `./bin/start.sh dev hosts` asserts 11 routing invariants over HTTP |
| nginx edge (prod) | `ops/nginx/site.conf.template` + generated `ops/nginx/sites/`; compose publishes loopback ports only; `domains --write`, `certs` |
| Dev->prd migration bundle | `./bin/start.sh backup` (pg_dump + config + env + media + nginx + manifest + checksums) and `restore` (`--all`); verified into a fresh postgres:16 and into the prd stack |
| Production gates | `./bin/start.sh preflight` (secrets, https base URL, cert, ports, DNS), `hosts`; prd log rotation caps |
| Playwright deps | `apps/web/Dockerfile.dev` runs `playwright install-deps chromium`, so a container recreate no longer breaks e2e |

---

## Recommended next

**M15–M20 complete** (2026-11-10). No agent plan work is open; the next move is the deploy,
then the owner lane.

| Priority | Item | Notes |
|----------|------|-------|
| **0** | Deploy to prd and finish TLS | `git pull`, `preflight`, `up`, `domains --write`, `nginx -t`, reload, `certs --check`, `hosts` (O9) |
| **1** | Run `FETCH_PACING=shadow` for one week | then flip to `enforce`; dev already enforces |
| **2** | Decide the queued NIST candidate | `sources candidates list`; `decide --status accepted` prints the profile row |
| **3** | Read the digital-technology window | closes **2026-11-27**; topic placements + channel inquiries per D-014 |
| **4** | Read the 14-day asset test | closes **2026-11-20**; `asset_interest` vs CTA impressions |
| **5** | D-trial: read the next natural refresh | 20 new summaries against D1–D5; no forced reset |
| **6** | Confirm CISA/SEC stay (O17) | answered 2026-11-10: keep both |
| **7** | Approve `SMTP_FROM` spelling (O15) | protected surface, needs same-message approval |
| **8** | Answer U32/U33, settle the brand string (D-018, 2026-12-15) | pricing shape; channel headers still say "System News" |

## Blocked on owner

| # | Item | Notes |
|---|------|-------|
| O5 | Answer U1-U12 | brand/domain, publisher portfolio, pilot, analytics, traffic |
| O15 | Approve the `SMTP_FROM` spelling change | `.env.example` (protected surface, same-message approval) |
| ~~O16~~ | ~~Approve `BOT_*`/`FETCH_*` in `.env.example`~~ done 2026-11-10 | keys added |
| O9 | Finish production TLS | `docs/domains.md`; `nginx -t`, reload and `certs --check` still need to pass |
| O10 | Approve the CI inventory gate | `.github/workflows/ci.yml` runs it on the next PR |
| O11 | Delete the unused `Caddyfile` | ADR 015 replaced the edge |
| U8 / D-002 | Email transport is live; the weekly-brief campaign | holds the lobby's brief card and every "weekly brief" promise |
| D-005 / U19 | Named reviewers | holds the reviewer signature in the services copy |
| U32 / U33 | Scope-call owner, pricing shape | gates the services band and the pilot SKU |
| O13 | Deploy the footer credit | `git pull` + `./bin/start.sh --env prd up` on the host |

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
- [x] playwright system libs: `apps/web/Dockerfile.dev` now runs `playwright install-deps chromium` (2026-11-07)

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
