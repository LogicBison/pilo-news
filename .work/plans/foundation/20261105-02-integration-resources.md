# System News - Integration resources (developer catalog)

**Doc:** foundation **02** · **Created:** 2026-11-05
**What it is:** the verified external-system catalog (feeds, AI provider, email, client consumers) with mirrors and open questions.
**Status:** Draft (2026-11-05) · **Needs:** owner confirmation of feed portfolio (U5) and AI budget cap (U4).

**Audience:** developers and agents integrating with external systems.

**Goal:** single place for official sources, mirrored artifacts, and verified vs assumed claims.

---

## 1. How to use this document

| Priority | Source | Use for |
|----------|--------|---------|
| P0 | Publisher feed / vendor official docs | Contract truth |
| P1 | Publisher terms, robots.txt, copyright pages | Legal interpretation (with advisor) |
| P2 | Community posts | Hints only - never override P0 |

**Offline mirror:** `.work/docs/integration/` + `.work/docs/integration/MANIFEST.txt` (one table row per artifact: `canonical_url`, `relative_path`, `sha256`, `retrieved`).

Rule: a claim about an external system is **Confirmed** only with a mirrored file or a cited live URL fetched in-session; otherwise **Assumed**.

---

## 2. Systems in scope

| # | System | Role | Auth | Mirror | Status |
|---|--------|------|------|--------|--------|
| I1 | Industry publishers (RSS 2.0 / Atom feeds) | Primary article source | None (public feeds) | Per-source snapshots in `tmp/` during dev only; no article text mirrored | Confirmed pattern, sources TBD (U5) |
| I2 | DeepSeek API (`deepseek-flash`, OpenAI-compatible) | Article summaries + desk brief | Bearer API key (env/secret store) | Prompt templates versioned in repo; model list verified 2026-11-05 | Decided (ADR 010); budget pending (U4) |
| I3 | Transactional email (SMTP or API) | Contact-form notification | SMTP creds or API key | n/a | Assumed (U8) |
| I4 | Client news consumers (LogicBison, third parties) | API consumers | API key optional, rate-limited | OpenAPI snapshot in `docs/api/openapi.v1.json` (generated) | Confirmed by brief |
| I5 | Search engines / sitemaps | Discovery | None | Sitemap contract documented in industry-sites SPEC | Confirmed pattern |
| I6 | Industry configuration dataset | Channel definitions v1 | Local file | `.work/docs/integration/industries-v1.1.0/data.json` + SHA-256 | Confirmed |
| I7 | Reference site (design input) | Look/feel reference for single-theme landing pages | None | Screenshot + URL note | Confirmed |

---

## 3. Authentication

| System | Mechanism | Secrets storage |
|--------|-----------|-----------------|
| I1 publishers | None; respect `robots.txt` and feed ToS | n/a |
| I2 AI provider | `AI_API_KEY` bearer token | `.env` (never committed); optional secret manager |
| I3 email | SMTP user/pass or provider API key | `.env` |
| I4 consumers | `X-API-Key` (hashed at rest) | Issued in console; shown once |
| I5 search engines | None; verification token may be required | `.env` |
| Admin surface | Argon2id password hash + short-lived JWT | `.env` for bootstrap admin |

**Rule:** keys never appear in logs, docs, fixtures, or client bundles (`.cursorrules` § Data Privacy & Security).

---

## 4. Rate limits and SLAs

| System | Limits / SLA | Our behavior |
|--------|--------------|--------------|
| I1 publishers | Varies; assume ≤ 1 req/min per host | Poll twice daily (default 720 min) + manual force, conditional GET, exponential backoff, per-host concurrency 1 |
| I2 AI provider | Token/min + $ budget | Batch ≤ 6 items/call, ≤ 1 concurrent refresh, hard monthly cap, fail-open |
| I3 email | Provider quota | Queue + retry 3x, then record failure |
| I4 consumers | Our limits | 120 req/min per IP (keyless), 600 req/min per key; 429 + `Retry-After` |
| I5 sitemaps | Crawl asynchronously | Sitemap index per channel + `lastmod` |

---

## 5. Publisher terms, copyright, and takedown

- We store **headline, canonical URL, publisher name, published time, topics, and an original 2-4 sentence summary**. We do **not** store full article text or images.
- Every card and article page links to the publisher with `rel="noopener"` and visible attribution.
- Before enabling a source, the operator records: feed URL, terms URL, whether aggregation + summary is permitted, and the date checked (editorial console field `terms_checked_at`).
- A takedown request is honored within 24 h: hide item (`status = hidden`) and block the source if repeated; audit event recorded.
- `robots.txt` and feed-level policies are respected on fetch.

**Open legal risk:** R1 in `.work/plans/RISK_REGISTRY.md`; counsel review is U11.

---

## 6. Verification log

| Date | Checker | Action |
|------|---------|--------|
| 2026-11-05 | plan-foundation | Catalog seeded; industry dataset mirrored with SHA-256; no live publisher contracts yet |

---

## 7. Open integration unknowns

| ID | Unknown | Blocks |
|----|---------|--------|
| U4 | AI monthly budget cap (`AI_MONTHLY_BUDGET_USD`) | Cost alert, run sizing |
| U5 | Publisher portfolio per channel + terms | Source seeding, legal sign-off |
| U8 | Email delivery vendor | Contact notification |
| I2 | Provider JSON-mode/streaming behavior | Deterministic parsing; assume chat-completions JSON output |

Promoted to `.work/plans/UNKNOWNS.md`.

## Next action

`@plan-foundation continue` (foundation doc 03 - product adjacency) - no owner input required for the next step.
