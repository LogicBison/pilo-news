# RISK_REGISTRY - planning registry

**Updated:** 2026-11-05 · **Maintained by:** plan-foundation / plan-master

Status: **Open** | **Mitigated** | **Accepted** | **Closed**

| ID | Risk | Category | Likelihood | Impact | Mitigation | Status | Owner |
|----|------|----------|------------|--------|------------|--------|-------|
| R1 | Copyright / feed-licensing exposure from republishing third-party article content | legal / content | M | H | Headlines + original AI summaries + link-out only; store no full text; per-source ToS checklist; documented takedown path (doc 02 §5, SPEC ingestion R14) | Open | owner + legal advisor |
| R2 | AI summaries hallucinate or misattribute facts | product / AI | M | M | Constrain prompts to title + excerpt; no invented quotes; label "AI summary"; editor can hide; fail-open to headline-only (ADR 010) | Open | eng |
| R3 | AI provider outage or budget overrun stalls publication | operational | M | M | Fail-open pipeline; per-refresh batch cap; cost metric + alert; cached summaries never invalidated by outage (observability spec) | Mitigated | eng |
| R4 | Single VPS is a SPOF (host loss = full outage) | infrastructure | L | H | Nightly off-site `pg_dump`, documented RTO 4h/RPO 24h, restore drill at P5 (doc 04 §6) | Open | ops |
| R5 | Feed breakage / upstream schema drift silently empties a channel | integration | H | M | Per-source status + `last_success` metric; stale-channel alert after 2 missed polls; manual seed fallback | Open | eng |
| R6 | Abuse / scraping of the public API exhausts capacity | security | M | M | Redis rate limits (IP + key), 429 + `Retry-After`, cursor caps, cache headers (SPEC news-api R9) | Open | eng |
| R7 | Cross-industry data leakage (an article or source served on the wrong channel) | product / security | L | H | Every read filters by `industry_id`; contract tests assert isolation; no cross-channel joins in read paths (SPEC news-api R4) | Open | eng |
| R8 | Industry-specific compliance misrepresentation (e.g. implying legal/financial advice) | legal / product | M | M | Per-channel disclaimer blocks, "not advice" copy, editorial review before enabling a channel (SPEC industry-sites R11) | Open | owner |
| R9 | i18n drift: Spanish pages missing summaries or UI strings | product | M | M | Locale completeness check in CI; explicit fallback label when a summary is unavailable; no mixed-language UI (SPEC industry-sites R3) | Open | eng |
| R10 | SEO duplicate-content penalty across industry sites | growth | M | M | Canonical URLs per channel + `hreflang`; sitemap per channel (SPEC industry-sites R7) | Open | eng |
| R11 | XSS via untrusted feed titles/summaries | security | M | H | Escape on render, sanitize at ingest, CSP with no inline script (threat model T4) | Mitigated | eng |
| R12 | SSRF via attacker-controlled feed URLs | security | L | H | Feed URLs admin-only, scheme allowlist (https), private-IP block, redirect cap (threat model T5) | Mitigated | eng |
| R13 | Prompt injection through feed content influencing summaries or console actions | security / AI | M | M | Feed text is data only; prompts isolate content; no tool calls from summarizer; output validation (threat model T6) | Open | eng |
| R14 | Contact-form PII mishandled (retention, logging) | privacy | M | M | 90-day retention, no PII in logs, deletion endpoint, DPIA note (data-classification §4) | Open | eng |
| R15 | Stack choices (FastAPI/Next/Postgres/VPS) are agent recommendations not yet owner-ratified | process | M | M | Ratification actions O1–O3 in HANDOFF; ADRs marked Decided under delegated authority | Open | owner |
| R16 | Timeline/cost estimate is unvalidated; scope may exceed a 1-3 person team | process | M | M | plan-master milestones sized to one agent session each; re-estimate after M1 | Open | owner |

## Review log

| Date | Reviewer | Action |
|------|----------|--------|
| 2026-11-05 | plan-foundation | Seeded from doc 01, doc 04, threat model |

---

## Next action

None - reviewed at every gate; see `.work/plans/NEXT.md`.
