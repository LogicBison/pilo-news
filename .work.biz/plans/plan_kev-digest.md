# Cybersecurity KEV digest — MVP scope

**What it is:** the scoped MVP for the first gated reference asset (offer S3) on the cybersecurity channel: a weekly known-exploited-vulnerability brief filtered to the reader's own vendor stack.
**Status:** Approved (2026-11-06) — D-003…D-006 approved, reader confirmed as the IT generalist; 14-day card test pending. Sits on `.work.biz/strategy/20261105-offer-and-leadgen-brief.md` §2.1 S3 and `20261105-product-feasibility-verification.md` §4.
**Needs:** D-003…D-006 below; a 14-day dormant-demand test (§11) before any generator is written.

---

## Verdict

build it, but not as "a KEV list". the list is free, complete, and already republished by an n8n template, a daily newsletter, and at least one vendor alerting service. the only defensible product is the reader's own stack, filtered, in plain language, weekly.

three corrections to the brief that follow from the data:

- **weekly, not daily.** the catalog gains 6.6 entries a week over the last 27 weeks (4 in the last 7 days). a daily send would be empty most days.
- **wednesday, not monday.** additions cluster Tuesday (83) and Wednesday (70) over the last 12 months. a Wednesday issue catches the week's batch.
- **no deadline pitch.** 1,762 of 1,768 rows have a due date already in the past. the dates are US federal (FCEB) mandates, not the reader's obligations.

## 1. Context loaded

| Field | Value |
|-------|-------|
| **Build target** | extension of the live cybersecurity channel; one asset, one page, no new product surface |
| **User** | the IT generalist at a 20–200 person org who "also does security"; reads the channel to decide whether an advisory applies to their stack — `.work.ui/screens/channel-home-cybersecurity/20261105-SCREEN-SPEC.md:12` |
| **Buyer** | none directly. the asset earns the inquiry ("incident readiness review"), which is routed to a partner. partner model still U18 |
| **Stack** | FastAPI 0.115 + httpx + asyncpg/SQLAlchemy + Redis Streams worker (`apps/api/pyproject.toml:7`); Next 15.1.8 / React 19 (`apps/web/package.json:17`); DeepSeek `deepseek-flash` at a $20/mo cap (`apps/api/src/news_api/platform/settings.py:30`) |
| **Build capacity** | solo, 6–12 week envelope; this MVP is 4–6 days (estimated, §9) |
| **Price point** | free. no paid tier (D-002, no payment surface) |
| **Gaps** | traffic baseline (U10 open), partner pricing (U18), named reviewer (D6), email delivery (D-002 defers `pilo-mail`) |

## 2. What the reader gets

**Problem statement:** the reader cannot tell which of 1,768 known-exploited vulnerabilities touch software they actually run, so they either ignore the list or pay a scanner to filter it.

**Core user story:** as an IT generalist running a small vendor stack, i want a weekly list limited to the vendors i use, with the one action to take, so that i patch the right thing on Monday instead of reading a catalog.

**One-line pitch:** "what got exploited last week, in the software you actually run."

**It is not:** a threat-intel feed, a scanner, a CVE explanation service, or a compliance certificate.

**Lenses:** data→insight (1,768 catalog rows → 5–12 actions), platform extension (existing channel, asset waitlist, funnel events), workflow automation (the weekly patch decision).

## 3. Evidence base

Source facts measured against the live feed on 2026-11-06 (`https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`, HTTP 200, 1.83 MB):

| Fact | Value | Grade |
|------|-------|-------|
| catalog version / release | `2026.11.04` / `2026-11-04T20:00:05Z` | measured |
| entries | 1,768 | measured |
| additions in the last 7 / 30 / 90 days | 4 / 30 / 72 | measured |
| additions in the last 12 months | 207 (6.6/week over 27 weeks) | measured |
| additions by weekday, 12 months | Tue 83 · Wed 70 · Fri 53 · Thu 52 · Mon 52 | measured |
| rows with a future due date | 6 | measured |
| ransomware flag = Known | 361 total, 0 in the last 30 days | measured |
| `forensicTriage` = Yes | 97 | measured |
| top vendors | Microsoft 390 · Cisco 102 · Apple 96 · Adobe 83 · Google 76 · Oracle 46 · Apache 41 · Ivanti 38 | measured |
| a 20-vendor filter covers | 64% of the catalog, 65% of the last 90 days | measured |
| row fields available | `cveID`, `vendorProject`, `product`, `vulnerabilityName`, `dateAdded`, `shortDescription`, `requiredAction`, `dueDate`, `knownRansomwareCampaignUse`, `forensicTriage`, `notes`, `cwes` | measured |
| NVD 2.0 answers without an API key | one-CVE query returned 200 with description, status, timestamps | measured |
| NVD rate limits without a key | 5 requests / 30 s (the official page returned a bare shell on fetch) | inferred |
| CISA terms | no explicit reuse grant; "provided for general information only… reliance at your own risk" ([terms](https://www.cisa.gov/terms-use)) | measured |
| licence | US federal work, public domain (17 U.S.C. §105) — needs legal confirmation under U11 | inferred |

Build-side facts (`Confirmed`, repository evidence):

| Fact | Evidence |
|------|----------|
| sources are RSS/Atom only; no JSON-API ingestion exists | `apps/api/migrations/001_init.sql:32` (`feed_url`), `apps/api/src/news_api/articles/infrastructure/fetcher.py:129` (`parse_feed`) |
| no issue/brief table exists | `apps/api/migrations/` 001–010; nothing digest-shaped |
| `/{industry}/briefs` renders an honest empty state, not content | `apps/web/src/app/[locale]/[industry]/briefs/page.tsx:42` (`EmptyState`) |
| asset capture is a waitlist keyed by a slug | `apps/web/src/components/AssetOffer.tsx:14`; registry in `apps/web/src/lib/assets.ts:15` (one entry, `waitlist: true`) |
| the asset card is hardcoded to the legal channel | `apps/web/src/app/[locale]/[industry]/page.tsx:57` and `:101`, likewise the article page |
| email exists but is inert without SMTP config | `apps/api/src/news_api/platform/notify.py:30` (`notify.skipped … smtp_not_configured`) |
| lead kinds `asset` / `question` and the `asset_interest` event already ship | `apps/api/migrations/010_offer_rungs.sql:9`, `apps/api/src/news_api/publishing/http/funnel.py:20` |
| free competing digests already exist | [n8n KEV workflow](https://dev.to/runbookfoundry/get-a-weekly-cisa-kev-digest-with-n8n-free-workflow-3nk9), [CVEDaily newsletter](https://cvedaily.io/newsletter/), [Senserva Watch](https://senserva.com/senserva-watch.html) |

## 4. MVP feature set

exactly this, nothing else:

1. **one dated issue page per week** at `/{locale}/cybersecurity/digest/{issue-date}`, plus `…/digest` showing the latest. 5–12 rows, one line each.
2. **only new entries since the previous issue**, plus a secondary "missed in the last four weeks" block (≤ 15 rows) so a skipped week is not silent.
3. **stack filter.** 20 checkboxes for the top vendors, remembered in `localStorage`, no account. Rows keep their vendor; unselected vendors collapse.
4. **per-row: vendor · product · what to do · CVE link · date added.** the CISA `requiredAction` text is reused verbatim when it is one sentence; otherwise a one-line paraphrase carrying a link to the source row.
5. **attribution and provenance:** "source: CISA KEV, catalog 2026.11.04", issue date, and the named reviewer.
6. **the shipped asset waitlist** as the email CTA, unchanged copy ("we email it when the first issue is ready" until delivery exists).
7. **both locales.** EN and ES for every row and the chrome; ES is translated at generation time, the English source stays one click away.

## 5. Out of scope

- sending email (D-002 / D1 open). the page and the waitlist ship without a sender.
- daily cadence, per-CVE deep dives, CVSS scoring UI, exploit-status timelines.
- accounts, saved stacks across devices, RSS/Atom or webhook output, Slack integration.
- Asia sources, EPSS, or any second vulnerability catalog.
- gating the archive, partner routing automation, paid tier.
- the other eight channels' assets.

## 6. Definition of done

- first issue live at both locales, 5–12 rows, every row's citation URL returns 200 on the day of publish.
- `./bin/start.sh test` green (API tests, `ruff`, `mypy`, web `lint`/`typecheck`/`check`, channel inventory).
- axe clean on the issue page; page weight under the current channel-home budget.
- the issue page states its source version, its date, and its reviewer; a correction, if any, is a dated note on the page.
- the generator refuses to publish with no reviewer name (`--reviewer` required).

## 7. First 3 users

| # | Who | How they are reached | Status |
|---|-----|---------------------|--------|
| 1 | the operator's own IT contractor or MSP | direct | `Unknown` — not named yet |
| 2 | one compliance/risk lead at an SMB the operator can reach | direct | `Unknown` — not named yet |
| 3 | existing readers of the cybersecurity channel | the asset card on the channel home | traffic unknown (U10) |

naming users 1 and 2 is an owner action, not an agent one. the file that should hold them is `.work.biz/pipeline/pipeline_tracker.md`, currently empty.

## 8. Success metric at 30 days

**primary:** ≥ 10 waitlist joins on the cybersecurity asset, of which ≥ 3 come from distinct company domains. a consumer-mailbox-only list measures curiosity, not demand.

**guardrail:** ≥ 1 attributed "incident readiness review" inquiry within 45 days of issue 1. if joins happen and inquiries don't in 60 days, the asset is a newsletter, not a lead source — re-scope it.

## 9. Build shape

recommended seam, minimal diff:

| Piece | Where | Note |
|-------|-------|------|
| issue storage | migration `011_digest_issues.sql` | one table, one row per issue: `industry_id`, `issue_date`, `catalog_version`, `reviewer`, `items jsonb`, `created_at`; unique on `(industry_id, issue_date)`. no second table until the archive needs querying by CVE |
| KEV adapter | `apps/api/src/news_api/digests/infrastructure/kev.py` | httpx GET of the JSON feed; the existing fetcher's SSRF guard (`validate_fetch_url`) is reused, not re-implemented |
| diff + draft | `apps/api/src/news_api/digests/application/build.py` | filter `dateAdded > last issue`, group by vendor, one line per row, ES translation via the existing DeepSeek client with a fail-closed path (a failed translation blocks the issue; a half-Spanish issue is worse than a late one) |
| CLI | `python -m news_api.cli digest build --industry cybersecurity --date … --reviewer "…" --dry-run` then `publish` | follows the `apply-profile` / `verify-sources` CLI pattern (`apps/api/src/news_api/cli.py:141`) |
| API | `GET /v1/industries/{slug}/digest` and `…/digest/{issue_date}` | ETag + cache headers like the other public reads |
| page | `apps/web/src/app/[locale]/[industry]/digest/[date]/page.tsx` + client filter | plus sitemap entry and EN/ES message keys |
| asset card | `apps/web/src/lib/assets.ts:15` + the two hardcoded call sites | select by channel instead of the literal `legal-regulatory-calendar` |

**Effort (estimated, solo):** adapter + diff 1 d · migration + repo 0.5 d · API 1 d · page + filter 1.5 d · copy/i18n 0.5 d · tests 1 d → **4–6 days**.

**Cost per issue:** one 1.83 MB fetch, ≤ 12 NVD calls (5–12 new CVEs × 2), ~12 LLM calls for the plain-language lines and their Spanish, all inside the existing `AI_MONTHLY_BUDGET_USD=20`. well under $1/week (estimated).

**Review cost:** 30–60 min per issue at this size (estimated). this is the recurring cost that kills the asset if D6 stays unanswered.

## 10. Variants (build decision)

| | low effort | high effort |
|---|---|---|
| **high value** | **build first:** public weekly page, 20-vendor filter, no email (§4) | phase 2: email delivery + per-stack alerting + archive by vendor (needs D1 and a reviewer) |
| **low value** | quick win: publish the raw 30-day KEV table as an SEO page, no filter, no promise | don't build: accounts, saved stacks, an API for the digest |

## 11. Validation before build (14 days, no generator)

the cheapest honest test is the card that already exists. it needs ~2 hours of code, not a pipeline:

1. add one `ASSETS` entry (`cybersecurity-kev-digest`, `waitlist: true`) and select the asset by channel instead of the hardcoded legal slug (`apps/web/src/lib/assets.ts:15`, `apps/web/src/app/[locale]/[industry]/page.tsx:57`).
2. copy: "a weekly list of known-exploited vulnerabilities in the vendors you run. free. we email it when the first issue is ready." no date promise.
3. measure for 14 days: `asset_interest` events per channel session (the event already fires), from `/v1/admin/funnel`.
4. **decision rule:** build if ≥ 1% of cybersecurity channel sessions produce an `asset_interest` event, or ≥ 10 joins total. otherwise re-scope to the inquiry rung and stop promising an asset.

caveat, stated plainly: the funnel read-out gives counts, not channel sessions by placement, so the 1% will be computed from CTA impressions as the denominator. mark it `estimated` in the read-out.

### Window (pre-registered 2026-11-06)

| Field | Value |
|-------|-------|
| starts | 2026-11-06, the day the cybersecurity card ships (M9) |
| ends | 2026-11-20 (14 days) |
| numerator | `asset_interest` events whose `placement` is `cybersecurity-kev-digest` |
| denominator | cybersecurity channel CTA impressions, from `/v1/admin/funnel` |
| build if | ≥ 1% of CTA impressions **or** ≥ 10 joins |
| re-scope if | neither, for two consecutive 7-day reads |
| note | the rule is pre-registered; results are read, not tuned. a denominator of 0 is reported as `unknown`, never as 0% |

## 12. Kill criterion

stop, keep the inquiry rung, delete the promise, if any of these hold:

- fewer than 15 joins after two published issues (8 weeks) — demand is not there at this traffic level.
- fewer than 1% of cybersecurity channel sessions join across the same window.
- no attributable readiness-review inquiry in 60 days after issue 1.
- no named reviewer for two consecutive issues (D6). an unreviewed digest is a liability, not an asset.

## 13. What makes it hard

- **the list is a commodity.** CISA publishes it free; an n8n template, a daily newsletter, and vendor alerting already republish it. the defensible part is the filter and the plain-language action, and both are thin moats.
- **the reader who cares already has it.** security teams subscribe to better feeds. the product only works for the org with no scanner — a reader who does not know what a CVE is and will not check 20 boxes.
- **the deadline angle is dead.** 1,762/1,768 due dates are past, and the remaining ones bind US federal agencies, not the reader. any "your deadline" copy is false.
- **review is the recurring cost.** generation is nearly free; a human signing each issue is 30–60 min a week forever.
- **the promise outruns the system, again.** the asset card promises an email; delivery is deferred (`D-002`). shipping the card before the page repeats the §6 R1 mistake at a smaller scale — the page must exist before the card is enabled.

## 14. Open technical questions

| # | Question | Grade | Note |
|---|----------|-------|------|
| T1 | can the existing fetcher be reused for JSON, or does it need a second path? | `Confirmed` | it parses XML (`parse_feed`); a JSON path is new code, the SSRF guard is reusable |
| T2 | is an NVD API key needed? | `Inferred` | one-keyless call returned 200; official limits page did not render. 12 calls/week is far under any limit |
| T3 | is republishing KEV rows legal? | `Unknown` | US federal work, no explicit CISA grant; needs U11 legal review before issue 1 |
| T4 | is Spanish translation of `requiredAction` safe? | `Unknown` | a mistranslated action is a liability. mitigation: translate the commentary, not the action; link the English source |
| T5 | does the issue page stay under the channel-home weight budget? | `Inferred` | 12 rows + filter is small; measure at build |
| T6 | what is the traffic denominator for the 1% rule? | `Unknown` | U10 open; use CTA impressions and mark `estimated` |

## 15. Decisions (approved 2026-11-06)

- **D-003 — cadence (approved):** publish weekly on Wednesday and drop "daily" from the brief. affects `.work.biz/strategy/20261105-offer-and-leadgen-brief.md:31` and `.work/plans/NEXT.md:74`.
- **D-004 — gate shape (approved):** public issue page + waitlist first, email gated later. this is the sequencing that keeps the promise honest while D1 is open.
- **D-005 — reviewer (approved; name still open):** who signs each issue (D6). without a name, the asset cannot ship; the generator enforces the field.
- **D-006 — one channel (approved):** cybersecurity only until issue 3 ships. no second channel's asset before this one is proven.

## Open questions

1. ~~is the reader the IT generalist or the security analyst?~~ **answered 2026-11-06: the IT generalist.** the filter design and the plain-language action follow from this.
2. should the digest be indexable and public, or `noindex` until the list is proven? public is better for discovery, worse for the "gated" story.
3. does the partner for the cybersecurity channel want the subscriber list, or only inquiries? answers U18 and changes the value of the list.
4. who writes the correction note when a row is wrong — the reviewer or the operator?

## Next action

run the 14-day card test in §11 (decisions D-003…D-006 approved 2026-11-06; iteration M9 planned in `.work/plans/NEXT.md`). the generator starts only if the test clears its rule.
