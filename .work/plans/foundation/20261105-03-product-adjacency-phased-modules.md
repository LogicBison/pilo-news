# System News - Product adjacency (phased modules)

**Doc:** foundation **03** · **Created:** 2026-11-05
**What it is:** optional product lanes beside the core v1 slice - phasing, integration seams, explicit out-of-scope.
**Status:** Draft (2026-11-05) · **Needs:** owner confirmation of Phase B priorities (U6, U12).

**Related:** doc 01 scope · doc 02 integrations.

---

## 1. Principle

- **Core v1** delivers: a themed news site per industry plus a stable public API, fed by an automated aggregation/summarization pipeline.
- Adjacent modules share **master data** (`industries`, `sources`, `articles`) through published ports - no cross-import of another context's infrastructure layer.
- Adjacency is additive: enabling a lane must not require changing the public API contract or the channel theming model.

---

## 2. Integration seams

| Seam | Core responsibility | Adjacent module | Contract |
|------|---------------------|-----------------|----------|
| `articles.ports.ArticleQueryPort` | Serve scored, locale-aware article lists | Newsletter digests, widgets | Read-only DTOs; no ORM leaks |
| `articles.ports.ArticleEvents` | Emit `article.published`, `article.hidden` | Webhooks, notifications, feeds | At-least-once, idempotent consumer |
| `channels.ports.ThemePort` | Resolve theme tokens + disclaimers per channel | New verticals, white-label skins | Versioned theme JSON schema |
| `sources.ports.SourceHealthPort` | Per-source freshness/status | Ops dashboard, alerting | Read-only metrics DTO |
| `publishing.ports.ExportPort` | Export channel bundles (JSON/XML) | Static-site generators, partners | Versioned bundle schema |

---

## 3. Phased modules

### Phase A (pairs with core v1)

| Module | Why now | Seam |
|--------|---------|------|
| Editorial console | Needed to operate sources, pins, hides, keys | `editorial` context |
| Contact + channel legal notices | Required for credible landing pages | `publishing` + `channels` |
| Sitemaps + JSON-LD | Organic discovery from day one | `publishing` + web |
| API docs portal (`/docs/api`) | Brief mandates consumable docs | `publishing` |

### Phase B (post-GA)

| Module | Trigger | Notes |
|--------|---------|-------|
| Newsletter / email digests | Audience retention goal | Reuses `ArticleEvents` + I3 email |
| Webhooks for client sites | Client requests push instead of polling | Signed HMAC, retries, DLQ (Redis Streams) |
| Sponsored / labeled placements | Revenue decision (U12) | Must carry machine-readable `sponsored` flag + disclosure UI |
| Additional locales (pt, fr) | Audience demand | Catalog + summary prompts only; no schema change |
| Dedicated search engine | > 100k articles or sub-50 ms search | Replace Postgres FTS behind `SearchPort` |
| Public self-serve API keys | Third-party adoption | Console signup + abuse controls |
| Static export for partners | Syndication deals | `ExportPort` bundle format |

### Phase C (strategic, not planned)

- Per-industry directories / professional listings (lead gen).
- Mobile apps (thin WebView or native) consuming `/v1`.
- White-label multi-instance deployments (would require revisiting ADR 006).

---

## 4. v1 out-of-scope (default)

- Full ERP / CRM / accounting integrations.
- Full article-text republication, image rehosting, or paywall bypass.
- Comments, user accounts, subscriptions, payments.
- Automated social posting.
- Programmatic SEO pages generated without editorial review.

---

## 5. Decision log

| Item | Status | ADR |
|------|--------|-----|
| Channel theming is data-driven, not per-vertical code forks | Decided | ADR 009 |
| Public API is versioned REST with a stable envelope | Decided | ADR 008 |
| Webhooks deferred to Phase B | Deferred | UNKNOWNS U13-U15 |
| Sponsored placements deferred pending owner decision | Open | UNKNOWNS U12 |

## Next action

`@plan-foundation continue` (foundation doc 04 - foundation and architecture) - no owner input required for the next step.
