# AI cost: the ceiling, the ledger, and the switches

**What it is:** how System News bounds its DeepSeek spend and how to spend the ceiling well.
**Status:** current (2026-11-11, M21) · **Needs:** nothing.

---

## 1. The ceiling

`AI_MONTHLY_BUDGET_USD` is the hard ceiling for **every** provider call this stack makes: item
summaries, desk briefs, featured picks and offer drafts. The default is **1**.

The cap is enforced on the *ledger*, not on trust:

1. **Reserve** the worst case before the request: peak cache-miss input for a deliberately
   pessimistic token count, plus the full `max_tokens` at the peak output rate, +5%.
2. **Call** the provider.
3. **Settle** the real cost from the returned `usage`, releasing the difference. Cache hits are
   priced at the cache-hit rate when the response reports the split.
4. A timeout, a parse failure or any unknown outcome **keeps the hold** — the provider may have
   billed it, so the ledger must assume it did.
5. If Redis cannot be read or written, the call is **denied**. A blank ledger is not a free pass.
6. A provider `402` marks the period exhausted and stops further attempts until the bucket resets.

The trade-off is honest: the last call can overrun its reservation by the estimation error, and a
hard-stop is one call wide. It cannot be the width of a month any more.

Keys live in Redis, expire a few days after the month ends, and are visible to an operator:

```bash
docker compose --env-file .env.prd -f docker-compose.prd.yml exec redis \
  redis-cli -a "$REDIS_PASSWORD" --scan --pattern 'ai:*'
```

`ai:spend:<YYYYMM>` is booked cost, `ai:held:<YYYYMM>` is in-flight reservations.

Metrics: `ai_budget_spent_usd`, `ai_budget_remaining_usd`, `ai_estimated_cost_usd_total`,
`ai_tokens_total`.

## 2. Admin overrides (no redeploy)

The console's **AI spend** tab (and `GET`/`PATCH /v1/admin/ai`) can change

| Setting | Default source |
|---|---|
| `ai_enabled` | `AI_ENABLED` |
| `ai_monthly_budget_usd` | `AI_MONTHLY_BUDGET_USD` |
| `ai_max_items_per_run` | `AI_MAX_ITEMS_PER_RUN` |
| `ai_offpeak_only` | `AI_OFFPEAK_ONLY` |
| `ai_peak_windows`, `ai_peak_days`, `ai_peak_holidays` | the matching env keys |

A saved value beats `.env` for this stack and applies to the API and the worker within five seconds — no
restart. `PATCH` with `{"reset": true}` drops every override and returns to `.env`. Writes are validated
(the calendar is parsed, the ceiling must be above zero) and audited as `ai.settings.update`.

Not overridable on purpose: `AI_API_KEY` (a secret — it never enters the database), `AI_BASE_URL` and
`AI_MODEL` (a deployment decision that should be visible in a deploy). The API key and model are still
checked on every call, so a blank key means no spend regardless of the panel.

`GET` also returns `spent_usd`, `held_usd`, `remaining_usd` and the current `bucket`, read from the same
ledger the cap uses, so the panel shows the number it is enforcing.

## 3. Spending it well

- **Peak is Mon–Fri 01:00–04:00 and 06:00–10:00 UTC**; everything else is half price. With
  `AI_OFFPEAK_ONLY=true` no call happens inside a peak block. The calendar is configuration
  (`AI_PEAK_WINDOWS`, `AI_PEAK_DAYS`, `AI_PEAK_HOLIDAYS`), not code, so a provider change is an
  env edit.
- **Per-run allowance.** Each run may summarise `remaining × 0.8 ÷ (runs left in the month ×
  enabled desks)`, capped by `AI_MAX_ITEMS_PER_RUN`. At $1 the first day affords roughly a dozen
  items per run, not sixty. The rest publish with the source excerpt — the site stays full.
- **Cache-friendly prompts.** The system prompt is stable and comes first, so repeat calls can hit
  the provider's prefix cache (50× cheaper input). Do not put timestamps or per-item text before it.
- **Output caps.** A summary asks for 240 tokens, a desk brief 400, an offer draft 3000. Raising
  them raises the worst case, not just the bill.

## 4. Per-channel switches (admin → Channels)

Two independent switches, both audited:

| Switch | Stops | Leaves running |
|--------|-------|----------------|
| **Automatic fetching** (`auto_fetch_enabled`) | scheduled refresh runs | manual refresh, serving |
| **AI summaries** (`ai_summaries_enabled`) | every model call for that desk | fetching, publishing, excerpt fallback |
| **Channel enabled** (`enabled`) | the whole desk | nothing (404) |

`AI summaries` off is the cheap parking spot: the desk keeps publishing, the meter stops. Turning
the channel off is for retirement, not for saving money.

## 5. What $1 does not buy

The current portfolio wants roughly 40k summaries a month. $1 at off-peak list price buys about
8,000. The cap therefore shapes the product: a few summarised stories per desk per run, the rest
headline plus source excerpt. If that is not enough, the honest options are a bigger ceiling or
fewer desks — not a weaker cap.
