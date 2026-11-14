# AI cost: the caps, the ledger, and the switches

**What it is:** how System News bounds its DeepSeek spend and how to spend the budget well.
**Status:** current (2026-11-13, M22) · **Needs:** nothing.

---

## 1. Six caps, two buckets

Every provider call this stack makes — item summaries, desk briefs, featured picks, offer drafts —
must fit **the day and the month** on **all three** dimensions. The first cap to bind stops the spend:

| Dimension | Env default | Why it exists |
|---|---|---|
| tokens/day | `AI_DAILY_TOKEN_LIMIT=300000` | tokens are what the provider bills and what its console shows |
| tokens/month | `AI_MONTHLY_TOKEN_LIMIT=6000000` | the same, over the month |
| requests/day | `AI_DAILY_REQUEST_LIMIT=400` | bounds a storm of calls that book nothing — refused calls still count |
| requests/month | `AI_MONTHLY_REQUEST_LIMIT=12000` | the same, over the month |
| USD/day | `AI_DAILY_BUDGET_USD=0.25` | the number an operator reads |
| USD/month | `AI_MONTHLY_BUDGET_USD=3` | the same, over the month |

The dollar caps are a *model* of the invoice: they come from the price table in
`apps/api/config/scoring.json`. If a price there is wrong, the token and request caps still hold.
That is why all three are enforced and why the ledger stores all three.

A daily cap above its monthly one is refused on write — it would make the daily knob decorative.

## 2. How a call is paid for

1. **Reserve** the worst case before the request: a deliberately pessimistic token count
   (3 chars/token) at peak cache-miss input rates, plus the full `max_tokens` at the peak output
   rate, +5%. Both buckets are locked in one transaction, so two concurrent runs cannot share money.
2. **Call** the provider.
3. **Settle** the reported `usage`, releasing the difference. Cache hits are priced at the cache-hit
   rate when the response reports the split.
4. A timeout, a parse failure or a 200 with no usable content **books the reservation** — the
   provider may have billed it, so the ledger assumes it did.
5. A refusal (4xx) books the **request** but no tokens and no dollars: it reached the provider, so it
   counts against the request caps, and it was not billed.
6. If the ledger cannot be read or written, the call is **denied**. A blank ledger is not a free pass.

Rows live in Postgres (`ai_usage`, migration `023`), one per UTC day and one per UTC month, and they
are never deleted — so the ledger survives a Redis flush, a `destroy`, a lost volume and a dev→prd
restore, and last Tuesday is still readable. Redis holds no spend state at all.

```bash
docker compose --env-file .env.prd -f docker-compose.prd.yml exec postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "SELECT bucket_kind, bucket, requests, tokens_prompt + tokens_completion AS tokens,
          cost_usd, requests_held, tokens_held, cost_held_usd, halted_reason
     FROM ai_usage ORDER BY bucket DESC LIMIT 8;"
```

Metrics: `ai_limit_remaining{dimension,period}`, `ai_denied_total{reason}`, `ai_budget_spent_usd`,
`ai_budget_remaining_usd`, `ai_estimated_cost_usd_total`, `ai_tokens_total{model,direction}`.

## 3. The kill switch

Some failures are not about money, and retrying them cannot help:

| Trigger | Effect | Clears when |
|---|---|---|
| provider `401` / `403` | halt, reason `auth_401` / `auth_403` | an operator resumes |
| provider `402` | halt, reason `provider_402` | an operator resumes |
| `AI_BREAKER_FAILURES` (5) consecutive provider failures | halt, reason `circuit_breaker` | `AI_BREAKER_SECONDS` (1800) elapse, or an operator resumes |

While halted, every call is refused **before** the request is sent. Fetching, scoring and publishing
continue; stories fall back to the source excerpt. `POST /v1/admin/ai/resume` (the **Resume AI calls**
button in the panel) clears it and is audited as `ai.halt.resume` with the reason that was cleared.

A run also stops walking its candidate pool as soon as a cap or a halt binds, instead of asking about
every remaining item. And the per-run allowance counts **attempts**, not successes — a provider that
refuses everything used to turn one run into a walk of the whole pool at two requests per item.

## 4. Admin overrides (no redeploy)

The console's **AI spend** tab (and `GET`/`PATCH /v1/admin/ai`) can change

| Setting | Default source |
|---|---|
| `ai_enabled` | `AI_ENABLED` |
| `ai_daily_token_limit`, `ai_monthly_token_limit` | `AI_DAILY_TOKEN_LIMIT`, `AI_MONTHLY_TOKEN_LIMIT` |
| `ai_daily_request_limit`, `ai_monthly_request_limit` | `AI_DAILY_REQUEST_LIMIT`, `AI_MONTHLY_REQUEST_LIMIT` |
| `ai_daily_budget_usd`, `ai_monthly_budget_usd` | `AI_DAILY_BUDGET_USD`, `AI_MONTHLY_BUDGET_USD` |
| `ai_max_items_per_run` | `AI_MAX_ITEMS_PER_RUN` |
| `ai_desks_per_tick`, `ai_rotation_minutes` | `AI_DESKS_PER_TICK`, `AI_ROTATION_MINUTES` |
| `ai_offpeak_only`, `ai_peak_windows`, `ai_peak_days`, `ai_peak_holidays` | the matching env keys |

A saved value beats `.env` for this stack and reaches the API and the worker within five seconds — no
restart. `PATCH` with `{"reset": true}` drops every override. Writes are validated (the calendar is
parsed, caps must be positive, daily ≤ monthly) and audited as `ai.settings.update`.

Not overridable on purpose: `AI_API_KEY` (a secret — it never enters the database), `AI_BASE_URL` and
`AI_MODEL` (deployment decisions that should be visible in a deploy), and the breaker settings (a
safety value is not a panel knob).

`GET` returns the whole ledger — per bucket: used, held, cap and remaining for requests, tokens and
dollars — plus `halted_reason`, so the panel shows the numbers it is enforcing.

## 5. Spending it well

- **Peak is Mon–Fri 01:00–04:00 and 06:00–10:00 UTC**; everything else is half price. With
  `AI_OFFPEAK_ONLY=true` no call happens inside a peak block. The calendar is configuration
  (`AI_PEAK_WINDOWS`, `AI_PEAK_DAYS`, `AI_PEAK_HOLIDAYS`), not code, so a provider change is an env
  edit. `AI_OFFPEAK_ONLY` is `true` in prd and `false` in dev.
- **Desk rotation.** Each rotation starts at most `AI_DESKS_PER_TICK` (2) of the due desks, drawn at
  random and weighted by staleness, and rotations are at least `AI_ROTATION_MINUTES` (60) apart. With
  twelve channels this is the difference between every desk getting one summary and a few desks
  getting a full run, rotating so no channel starves: a desk that keeps losing the draw keeps getting
  stale, and therefore keeps getting heavier, until it wins. Pacing lives in Redis; losing it costs one
  extra rotation, not a cent.
- **Per-run allowance.** A run may attempt `remaining × 0.8 ÷ (runs left × enabled desks) ÷ cost per
  item`, sized by tokens and by dollars for both the day and the month, capped by
  `AI_MAX_ITEMS_PER_RUN`; the smallest of the four wins. The rest publish with the source excerpt —
  the site stays full.
- **Cache-friendly prompts.** The system prompt is stable and comes first, so repeat calls can hit the
  provider's prefix cache (cheaper input). Do not put timestamps or per-item text before it.
- **Output caps.** A summary asks for 240 tokens, a desk brief 400, featured picks 200, an offer draft
  3000. Raising them raises the reservation, not just the bill.

## 6. Per-channel switches (admin → Channels)

| Switch | Stops | Leaves running |
|--------|-------|----------------|
| **Automatic fetching** (`auto_fetch_enabled`) | scheduled refresh runs | manual refresh, serving |
| **AI summaries** (`ai_summaries_enabled`) | every model call for that desk | fetching, publishing, excerpt fallback |
| **Channel enabled** (`enabled`) | the whole desk | nothing (404) |

`AI summaries` off is the cheap parking spot: the desk keeps publishing, the meter stops. Turning the
channel off is for retirement, not for saving money.

## 7. What the caps do not do

An application cap cannot protect the wallet from everything. Three limits sit outside this codebase
and belong to the operator:

1. **One key per environment.** dev and prd sharing `AI_API_KEY` means one invoice, two independent
   ledgers, and dev traffic spending production money. Issue separate keys.
2. **A prepaid balance.** The only ceiling no bug can exceed is the money in the account. Keep the
   balance at what you are willing to lose.
3. **Nothing else on that key.** Any other project or script using the same key bills the same
   account, and no ledger here can see it.

Budget shape: at ~560 tokens per summary, `AI_MONTHLY_TOKEN_LIMIT=6000000` buys roughly 10,000
summaries a month across all desks — about a third of what the full portfolio would want. The caps
therefore shape the product: a few summarised stories per desk per run, the rest headline plus source
excerpt. If that is not enough, the honest options are a bigger cap or fewer desks — not a weaker cap.

## 8. Incident record

2026-11-11→12, $21.40 on the shared key: 6,974 requests and 601,649,337 tokens — 86k tokens per
request, seven times the largest prompt this codebase can build. Verification, arithmetic and the
defects found (allowance counting successes, 401 retried forever, Redis-only monthly ledger, one key
for two stacks) are in `.work/reports/20261113-ai-spend-verification.md`. M22 is the response to it.
