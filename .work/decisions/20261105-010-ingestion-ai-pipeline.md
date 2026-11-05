# ADR 010 - Ingestion and AI summary pipeline

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** how articles become published, scored, deduplicated, summarized content.

## Context

- Reference implementation (`aggregator.py`, `summary.py`) already implements RSS parsing, scoring (topic keyword match, recency half-life 72 h, trust weight, pinned boost), dedupe (title similarity 0.72, corroboration), retention (7 days), and incremental AI summaries with a JSON cache.
- The brief requires reliability and consistency for clients; publication must not depend on the AI provider.
- Copyright constraints forbid storing full text.

## Decision

- **Fetch:** per-source poll every 5-10 min, conditional GET (`ETag`/`If-Modified-Since`), 10 s timeout, per-host concurrency 1, exponential backoff, SSRF guard (https only, private-IP block, redirect cap 3).
- **Normalize:** parse RSS 2.0/Atom; strip HTML; truncate excerpt to 600 chars; canonicalize URL (lowercase host, strip tracking params, follow declared `<link>`); detect language (declared first, heuristic fallback).
- **Store:** upsert by `canonical_url`; never store full content; `status = draft` until it passes scoring.
- **Score (ported from reference):** topic weight × keyword matches + trust × 0.85 + length bonus, multiplied by recency (half-life 72 h, floor 0.15), + pinned boost 5.0; min score 0.35; `require_topic_match` default true.
- **Dedupe:** cluster by title similarity ≥ 0.72 (token-set ratio); keep highest score; attach `corroboration` count and `corroborating_sources`; +0.15 per extra source; single-source items below trust 0.8 get a 0.12 penalty and `verification = single-source`.
- **Retention:** 7-day window for display; rows retained 30 days for audit then purged by a nightly job.
- **AI summaries:** OpenAI-compatible chat API; per-item 2-4 sentence paragraph (≤ 900 chars), desk brief 5 lines (≤ 1200 chars); EN/ES prompts; only new/changed items (`prompt_version`); batch ≤ 6; **fail-open** (no summary → headline-only card; never block publish); no URLs in summaries; output validated (length, sentence count, no raw HTML).
- **Incremental:** prior summaries preserved by canonical URL + language; a full reset is an explicit admin action.
- **Worker:** Redis Streams consumer, single-flight refresh lock, `refresh_runs` row per run with stats; retries with backoff then dead-letter stream.

## Consequences

- **Positive:** proven algorithm reused; AI cost bounded and cancellable; publication resilient; copyright-safe by construction.
- **Negative:** scoring is heuristic (manual pins compensate); summary quality varies by model; 7-day retention limits deep archives.
- **Neutral:** embeddings/personalization can be added later as a separate read model.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| LLM-scored relevance | Cost + non-determinism for a ranking that works well heuristically |
| Full-text storage + display | Copyright exposure (R1) |
| Synchronous summarize on request | Latency + cost spikes; breaks on provider outage |
| Dedicated NLP pipeline | Overkill for 10k items/day/channel |

## References

- `/mnt/work/Projects/LogicBison/api/src/news/aggregator.py`
- `/mnt/work/Projects/LogicBison/api/src/news/summary.py`
- SPEC `.work/features/ingestion-pipeline/20261105-SPEC.md`
- RISK_REGISTRY R1, R2, R3, R13

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
