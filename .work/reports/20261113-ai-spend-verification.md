# AI spend verification — why $25 left the account while a $1 ceiling was configured

**Status:** verified locally (dev stack, code, git history). **Not** verified: the provider invoice and the prd runtime.
**Needs:** three answers from the operator (below) or approval for read-only prd checks.
**Date:** 2026-11-13 · **Mode:** read-only. no code changed, nothing staged, nothing committed.

---

## Answer first

the $1 ceiling is real and it is holding in dev. the ledger reads `ai:spend:202611 = 0.956216878`
against `budget_usd = 1.0`, `platform_settings` is empty (no admin override), and both AI call sites
reserve before they send. the ceiling did **not** cover the period before it existed: until `b7d3506`
reached prd on 2026-11-11, the cap in code was **$20 per stack per month**
(`ai_monthly_budget_usd: float = 20.0`, `.env.example` `AI_MONTHLY_BUDGET_USD=20`) enforced by a soft
once-per-call check that booked only successful calls. a single-day $25 bill is consistent with that
old ceiling and inconsistent with the new one.

the operator's instinct — too many requests — is correct as a mechanism, and it is still live: three
defects let request volume run far ahead of the configured allowance. none of them can push *booked*
spend past the ledger, but one of them hides spend from the ledger entirely.

## Evidence

| # | check | result | source |
|---|-------|--------|--------|
| 1 | dev effective settings | `budget_usd 1.0`, `max_items_per_run 60`, `item_cost_estimate 0.00016`, `offpeak_only False`, model `deepseek-flash`, key present | `exec api python -c get_settings()` |
| 2 | dev ledger | `ai:spend:202611 = 0.956216878` · `ai:held:202611 = 0` · no `ai:exhausted:202611` · TTL 1907858 s | `redis-cli MGET` |
| 3 | ledger durability | `appendonly yes`, `maxmemory-policy noeviction`, `evicted_keys:0`, volume `system-news-dev_redisdata` created 2026-11-05 → not evicted, not lost on today's restart | `redis-cli CONFIG GET` / `INFO stats` / `docker volume inspect` |
| 4 | admin overrides | `platform_settings` 0 rows → `.env` is what runs | psql |
| 5 | call sites | only `articles/application/ingest.py:244` and `offers/application/draft.py:110` build an `AIClient`; both reach the provider only through `_chat` → `reserve` → `settle` | grep over `apps/api/src`, `apps/api/scripts` |
| 6 | cap is in the request path | `reserve` runs before `client.post`; `BudgetUnavailable` → deny (fail closed); 402 → `mark_exhausted` | `ai_client.py:290-330`, `ai_budget.py:31-45` |
| 7 | **provider is rejecting dev now** | worker booted 20:22 UTC; in 5 minutes it sent **498 requests, all `provider status 401`** — 478 `summary.failed`, 20 `desk_brief.failed`, 0 summaries stored | dev worker log |
| 8 | **allowance ignored when calls fail** | today's 5 runs recorded `summary_budget` = 5 in total (1 per desk) yet ~239 summaries were attempted | `refresh_runs.stats` vs worker log |
| 9 | old ceiling | `git show b7d3506~1:.../settings.py` → `ai_monthly_budget_usd: float = 20.0`; `b7d3506` changed `.env.example` `-AI_MONTHLY_BUDGET_USD=20` → `+=1` (2026-11-11) | git |
| 10 | old limiter and guard | `b7d3506~1:.../ingest.py:245` → `summary_budget = settings.ai_max_items_per_run` (60 per desk per run); guard was `spent >= budget` once per call, booking cost only after a 200 | git |
| 11 | dev volume | summaries per day: 11-05 **439**, 11-06 159, 11-07 48, 11-10 **278**, 11-11 5, 11-12 5, 11-13 0. runs per day: 11-05 **46** (36 manual), 11-06 21, 11-07 11, 11-10 **25** (2 manual), 11-12 5, 11-13 5 | psql `articles`, `refresh_runs` |
| 12 | scheduler is not a hot loop | enqueue only when the last scheduled run is older than the interval (+ per-channel stagger), skipped when a run is active; 1 s poll | `queue.py:150-181` |

## Defects found (reported, not fixed)

**D1 — the per-run allowance counts successes, not attempts.**
`ingest.py:296-306` increments `summarized` only when a summary is stored, and the loop guard is
`summarized < summary_budget`. when calls fail the counter never moves, so the run walks the entire
candidate pool: today a budget of **5** produced **~239 attempts / 498 HTTP requests** (two tries per
item). post-M21 the ledger still stops the money — a denied reserve raises before `client.post` — but
pre-M21 nothing stopped it except the $20 soft cap.

**D2 — a 401 is treated as transient and books nothing.**
`ai_client.py:305-307`: any status ≥ 400 releases the reservation and raises `AIError`; only **402**
sets `ai:exhausted:<bucket>`. with a rejected key the ledger never advances, so the cap never engages
and the worker keeps sending — dev is in exactly that state now. if DeepSeek answers 401 rather than
402 for a stopped or unpaid account, the kill switch never fires.

**D3 — every worker start re-runs every due desk.**
`queue.py:150-181` enqueues on boot any desk whose last scheduled run is older than the interval, so
restarts multiply AI volume: dev logged 25 runs on 11-10 and 46 on 11-05. pre-M21 each run was allowed
60 items per desk, and prd has more desks than dev.

**D4 — the ledger is a model of the invoice, not the invoice.**
`usage_cost` prices reported tokens from `config/scoring.json` (`deepseek-flash`: $0.30 in / $1.20 out
per M at peak, half off-peak, cache hits $0.006/$0.003, note says checked 2026-11-11). if the account's
real price, model or billed token set differs, the ceiling bounds the *estimate*. dev's booked month is
$0.956; a 26× pricing error would read as ~$25 on the invoice. **hypothesis, not a finding** — only the
provider's token totals for that day can settle it.

**D5 — dev is not off-peak gated, and there is no env kill switch.**
`.env.dev:63 AI_OFFPEAK_ONLY=false` (prd `true`), so dev buys at peak rates. `AI_ENABLED` is unset in
`.env.dev`, `.env.prd` and `.env.example`, defaulting to true.

**D6 (hygiene, not spend):** `.env.prd:42` embeds the Redis password inside `REDIS_URL`; it surfaced in
this session's command output. the file is gitignored and local, but the value should be rotated or
moved to `REDIS_PASSWORD` only.

## What I could not verify

- **which day** the $25 landed on, and whether it post-dates the prd deploy of `b7d3506` (2026-11-11).
- **prd runtime**: its ledger value, run history, worker logs, running commit, `platform_settings`.
  needs host access.
- whether dev and prd share one DeepSeek key, and whether any other project, script or manual test
  billed the same account. my attempt to fingerprint the keys in `.env.*` was blocked by the sandbox
  credential policy; I did not route around it.

## Open questions

1. which date does the DeepSeek console show the $25 on, and does the same view give token totals
   (input / output / cache) for that day?
2. do `.env.dev` and `.env.prd` hold the same `AI_API_KEY`, and could another project or manual test on
   this machine have billed the same account?
3. is the 401 expected — was the key rotated or revoked after the bill?

## Next action

answer 1–3 (or approve read-only prd checks: ledger `MGET ai:spend:202611`, `refresh_runs`/`articles`
per day, worker log grep for `provider status`, running commit, `platform_settings`), then scope the
fix: count attempts against the allowance (D1), treat 401/403 as terminal for the run and — when the
account is stopped — for the period (D2), and reconcile the ledger against the provider invoice before
trusting the ceiling (D4).

---

# Addendum — operator answers (2026-11-13) and the invoice decomposition

**Answered:** the $25 window is **11-11 → 11-12**; the DeepSeek console for it reads **cost $21.40**,
**6,974 requests**, **601,649,337 tokens**. dev and prd share **one API key**. the 401 is deliberate —
the operator deleted the keys to stop the leak.

## The invoice does not fit this codebase

| derived | value | how |
|---|---|---|
| tokens per request | **86,270** | 601,649,337 ÷ 6,974 |
| blended price | **$0.0356 / M tokens** | 21.40 ÷ 601.649 M |
| largest call this repo can emit | **≈12k tokens** | offer draft: `max_rows` clamped to ≤30 (`offers/application/config.py:29`), each record's summary clipped to 600 chars (`draft.py:_prompt`) → ≈9k prompt + `max_tokens=3000` |
| typical call | **≈840 tokens** | item prompt measured in the running container: 394 template tokens + title ≤300 chars + excerpt ≤280 chars, `max_tokens=240` |
| desk brief / featured picks | ≈1.3k tokens each | `max_tokens` 400 / 200, headlines ≤12×200 chars, candidates ≤20×160 chars |

86k tokens per request is **7× the largest prompt this system can construct** and ~100× the typical one.
there is no code path in `apps/api` that can produce it: the only provider call site is
`ai_client.py:337`, and every caller truncates its input.

**Volume ceiling for the window.** prd, worst case, pre-cap code: 11 desks × 2 scheduled runs/day ×
60 items (`AI_MAX_ITEMS_PER_RUN`) × 2 attempts × 840 tokens ≈ **2.2 M tokens/day**; with the queue's
3 retries on a failed run (`queue.py:schedule_retry`, `BACKOFF_SECONDS`) ≈ **6.6 M tokens for the two
days**. at the invoice's own blend that is **≈$0.24**; at peak list price **≈$2–3**.
dev contributed ~10 calls (5 summaries on 11-11, 5 on 11-12 — `refresh_runs`, `articles`) ≈ **$0.01**,
and dev's ledger for the whole month is **$0.956** of its $1 ceiling.

**Conclusion (correcting the working assumption):** most of those 601 M tokens were **not** System
News. the shared key means the console line aggregates everything that used it — including any other
project, agent or manual test on that account. System News' realistic share of the $21.40 is **$2–3**,
and its own ceiling held at $1 per stack. what System News *did* contribute is the request volume:
6,974 requests is the right order of magnitude for two days of dev+prd refresh runs with D1 (attempts
not counted) and D2 (401s retried forever) — i.e. this system can burn *requests* and, with a valid
key, a few dollars a day, but it cannot burn 600 M tokens.

**Still unverified:** prd's own counters for the window (`refresh_runs` per day, `articles.summary`
created 11-11/11-12, `ai:spend:202611`, worker log statuses, running commit) — needs host access. if
prd shows an order of magnitude more AI calls than the schedule allows, this conclusion weakens and
D1/D2 become the primary cause.

## Additional defects (from the answers)

**D7 — one key, two wallets.** dev and prd share `AI_API_KEY`, so each stack enforces its *own* $1
ledger against the operator's *one* balance, and dev traffic spends production money. the ledger has no
notion of the other stack.

**D8 — the ledger is Redis-only and monthly-only.** `ai:spend:<YYYYMM>` lives in the Redis volume; a
`destroy`, a volume loss, or a dev→prd bundle restore starts the month at zero spent. there is **no
daily cap** at all: on 2026-12-01 both stacks get a fresh ceiling, and nothing bounds a single day
inside a month.

**D9 — the dollar model is the only bound.** the cap is denominated in USD computed from
`config/scoring.json`; if a price is wrong the ceiling silently bounds the wrong number. tokens and
request counts are what the provider bills and what the console shows, and neither is capped today.

**D10 — no env-level kill switch is set.** `AI_ENABLED` is absent from `.env.dev`, `.env.prd` and
`.env.example`, so it defaults to `true`: re-issuing a key resumes spending immediately with no code
change.

## Immediate mitigation (before new keys are issued)

1. set `AI_ENABLED=false` in `.env.prd` and `.env.dev` (protected files — needs the operator's
   same-message approval), or save `ai_enabled=false` from `/admin` → AI spend, which wins over `.env`
   within 5 s and needs no restart.
2. issue **one key per environment**, and keep the account balance at the amount the operator is
   willing to lose — a prepaid balance is the only limit no application bug can exceed.
3. until D1/D2 are fixed, keep `ai_summaries_enabled` off on the prd desks: the run will still fetch
   and publish with excerpt fallback, and it will not attempt the whole candidate pool.
