# ADR 010 - Ingestion and AI summary pipeline

**Status:** Decided · 2026-11-05 (v2, supersedes the earlier draft of this ADR) · **Decision authority:** owner instructions "apply the best recommendation", "twice a day", "manual forced polling", "deepseek v4.1 flash" (2026-11-05); ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** fetch schedule, language handling, scoring/dedupe, retention, AI provider and prompt contract, and manual refresh.

## Context

- The reference implementation (`aggregator.py`, `summary.py`) already implements RSS parsing, per-language scoring, dedupe/corroboration, retention, and incremental AI summaries. Its behavior is documented in `docs/news-multilingual-replication.md`.
- The reference refreshes on a request-driven TTL (default 360 min), which couples freshness to traffic and can produce a cold-start cost spike.
- The owner requires: **twice-daily updates by default**, **configurable cadence**, **easy manual forced polling**, and **lowest practical LLM cost**.
- The provider is DeepSeek V4.1 Flash; the current official API model id is **`deepseek-flash`** (legacy `deepseek-v4-flash` routes to the same model and must not be used in new code).

## Decision

### 1. Schedule and manual refresh

- **Scheduled refresh:** one run per channel every `REFRESH_INTERVAL_MINUTES` (default **720** = twice a day). The worker schedules per channel with a stagger (0-10 min) to spread feed and AI load; schedule state lives in `refresh_runs`/Redis, not in memory.
- **Manual forced refresh:** `POST /v1/admin/refresh` `{industry, force:true}` → `202` + `run_id`; `GET /v1/admin/refresh/{run_id}` reports status. CLI: `python -m news_api.cli refresh --industry all --force`, wrapped as `./bin/start.sh refresh`. Both bypass the schedule, not the single-flight lock.
- **Single-flight:** a Redis lock per channel; a duplicate request while a run is active returns `409` with the active `run_id` (no second run).
- **No request-driven TTL refresh.** Public reads never trigger ingestion; a cold cache serves `503` with `Retry-After` until the first run completes.
- **Refresh is all-or-nothing per channel across languages:** one run rebuilds every language pool for that channel; `locale` only selects the response.

### 2. Language handling

- `sources.language` is mandatory and validated against the supported locale set; items inherit it. Seeds declare `language`. No heuristic detection (ADR 007).
- Partition candidates by language **before** scoring; score, dedupe, layout, and AI run per pool; no cross-language dedupe.
- Unsupported-language items are rejected at ingest with a source-config error (not silently parked).

### 3. Fetch, normalize, score, dedupe

- **Fetch:** conditional GET (`ETag`/`If-Modified-Since`), 12 s total / 6 s connect timeouts, https-only, SSRF guard (private-IP block, redirect cap 3, 5 MB cap), per-host concurrency 1, declared charset with UTF-8 fallback.
- **Normalize:** parse RSS 2.0/Atom; strip HTML; unescape twice; repair common mojibake; excerpt ≤ 280 chars; title ≤ 300 chars; canonical URL strips `www.`, fragment, and tracking params (`utm_*`, `fbclid`, `gclid`, `ref`).
- **Identity:** `id = "<source_id>:<hash(canonical_url, casefolded title)>"`; upsert by canonical URL; one channel per article.
- **Age + exclusion:** `retention.max_age_days` (default 7); undated items kept; exclusion is a case-folded substring test over title + excerpt + blurb; `exclude_keywords` global plus optional `exclude_keywords_<locale>`.
- **Scoring:** reference formula and constants (`keyword_weight`, `topic_weight_multiplier`, `source_trust_weight 0.85`, `recency_half_life_hours 72`, `recency_floor 0.15`, `pinned_boost 5.0`, `min_score 0.35`, `title_length_bonus 0.08`); per-language `keywords_<locale>` with English fallback; pinned items bypass topic/min-score gates.
- **Dedupe:** Jaccard title similarity ≥ 0.72 **within a language pool**; canonical-URL duplicates merge source names; corroboration count + `+0.15 × (n-1)`; single-source penalty 0.12 below trust 0.8; Unicode-aware tokenization (reference §14.9 fixed).
- **Seeds:** pinned seeds are **exempt from the age filter** (reference bug §14.1 fixed); seeds still pass scoring/dedupe/summary.
- **Retention:** display window 7 days; rows purged at 30 days.

### 4. AI generation

- **Provider:** DeepSeek, base `https://api.deepseek.com`, OpenAI-compatible `POST /chat/completions`.
- **Model:** `deepseek-flash` (DeepSeek-V4.1-Flash). Env `AI_MODEL` overrides; legacy `deepseek-v4-flash` is rejected in new configs.
- **Thinking:** disabled for summaries and picks (`thinking: {"type": "disabled"}`); temperature 0.4 prose / 0.3 picks; timeout 45 s desk, ≥120 s items, ≥60 s picks.
- **Outputs (per language):** 5-line desk brief (≤ 1200 chars), one 2-4 sentence paragraph per article (≤ 900 chars), 1 lead + N favorite picks by id.
- **Prompts:** versioned EN/ES tables (`apps/api/config/prompts/{en,es}.json`), `PROMPT_VERSION=1`; a config `system_prompt` override is not offered (reference §14.7 avoided).
- **Language stamping:** `summary_language` = article language; reuse only on exact language match; incremental refresh reuses valid summaries regardless of `prompt_version`; only a full reset regenerates them.
- **Validation:** reject URL-like output, HTML, < 80 chars, or summaries that copy the title verbatim; enforce sentence count; strip URLs/`Article URL:`/`Comments URL:`/HN artifacts; repair mojibake.
- **Fail-open:** any provider error/timeout produces headlines without summaries; never blocks publication; statuses recorded but not exposed publicly.
- **Cost controls:** only new/changed items are summarized; batch ≤ 6; per-run item cap (`AI_MAX_ITEMS_PER_RUN`, default 60 per channel); monthly budget cap (`AI_MONTHLY_BUDGET_USD`) enforced before each call; `ai_tokens_total` and `ai_estimated_cost_usd_total` metrics.

### 5. Manual and operational flows

- Force refresh from the console, the admin API, and the CLI; the run is audited.
- `full_reset=true` (admin-only, typed confirmation) wipes bundles and regenerates all summaries; audited.
- A failed feed logs a warning and contributes nothing; the run still succeeds (`partial` status).

## Consequences

- **Positive:** predictable cost (2 runs/day + manual), no traffic-coupled cold starts, deterministic language assignment, reference-compatible output, one summary per article (lowest AI spend).
- **Negative:** freshness can lag up to 12 h for scheduled items (manual force covers urgent cases); Spanish coverage depends on Spanish sources (RISK R17); a provider outage removes all new summaries until recovery (headlines still publish).
- **Neutral:** cadence is an env var, tunable without code; more frequent schedules increase cost roughly linearly.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| Reference request-driven TTL | Couples cost/freshness to traffic; cold-start spike |
| 5-10 min polling (earlier draft) | 72-288 runs/day; AI spend and feed load unacceptable for v1 |
| Per-locale summaries | Doubles AI cost; contradicts the no-translation model |
| `deepseek-v4-flash` / `deepseek-v4.1-flash` | Legacy or non-existent ids; current official model id is `deepseek-flash` |
| On-demand public refresh | Abuse/cost vector; admin-only is sufficient |

## References

- `/mnt/work/Projects/LogicBison/docs/news-multilingual-replication.md` §6-§8, §14.1, §14.7, §14.9
- `/mnt/work/Projects/LogicBison/api/config/news_algorithm.json`
- DeepSeek model list: `deepseek-flash` = DeepSeek-V4.1-Flash (https://api-docs.deepseek.com/api/list-models)
- SPEC `.work/features/ingestion-pipeline/20261105-SPEC.md`
- RISK_REGISTRY R1-R3, R17, R18

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
