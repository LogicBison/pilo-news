# ADR 014 - Source quality policy and channel portfolio

**Status:** Decided · 2026-11-05 · **Decision authority:** operator instruction "find a minimal reasonable number of sources, is there a way to establish some reasonable level of quality in the sources? if yes, apply it".
**Needs:** legal review of publisher terms stays with the owner (U11); this ADR decides the technical policy.

**Decides:** how feeds enter a channel, how many are required, and how quality is measured and enforced.

## Context

- Every channel must carry several news sources; two feeds per channel is too fragile (one stale feed halves the channel).
- Feed quality varies wildly: stale documents, mislabelled languages, empty payloads, email addresses used as publisher names, future-dated items.
- The operator asked for a defensible quality bar that can be applied consistently, not per-channel judgment calls.

## Decision

- **Coverage floor:** at least four enabled sources per channel, and at least one per supported language.
- **Quality gates** (implemented in `news_api.sources.application.quality`, pure and unit-tested): reachable/parseable, ≥3 items with title+link, newest item <45 days (warn at 14), declared language matches a stopword vote, ≤200 items, trust ≥0.75, duplicate ratio <40%. Hard failures block; soft issues lower the score.
- **Score and grade:** 0–1 score from penalties; `A ≥0.90`, `B ≥0.80`, `C ≥0.70`, `D <0.70`; pass requires no hard failure and score ≥0.70.
- **Verification command:** `python -m news_api.cli verify-sources --industry all` fetches every enabled source and prints per-source grades plus per-channel coverage; exit code 1 on any failure so CI can gate.
- **Portfolio:** five launch channels plus a sixth custom channel (`cybersecurity`) that exists only as a deployment-profile file; every channel carries 4–5 verified feeds (EN+ES where available).
- **Remediation is non-destructive:** a failing feed is disabled, never deleted, preserving provenance for already-published articles.
- **Publisher hygiene:** a publisher value that is an email is replaced by the parenthesised outlet name, then by the feed title/source name.

## Consequences

- **Positive:** channels cannot silently starve; quality is reproducible and testable; new portfolios are evaluated by the same standard; a broken publisher is visible in one command.
- **Negative:** the stopword language vote can misclassify very short feeds; the 45-day freshness rule rejects some genuinely low-cadence publishers (acceptable at launch).
- **Neutral:** licensing/terms compatibility remains an owner legal decision (U11); the policy is technical only.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| Manual editorial approval only | No repeatable signal; breaks when the portfolio changes |
| Third-party feed-quality API | New external dependency and cost for a check we can do locally |
| Hard-fail on any soft issue | Would reject usable niche publishers at launch |
| Delete failing sources | Loses provenance and operator history |
