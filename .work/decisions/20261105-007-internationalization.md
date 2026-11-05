# ADR 007 - Internationalization: locale routes, language-partitioned content, EN/ES

**Status:** Decided · 2026-11-05 (v2, supersedes the earlier draft of this ADR) · **Decision authority:** owner instruction "apply the best recommendation" (2026-11-05); ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** URL policy, content-language model, locale negotiation, fallback, and SEO for English and Spanish (and any locale added later).

## Context

- The brief requires EN + ES at launch, browser-derived default, one-click switch, and additive locales.
- The LogicBison reference (`docs/news-multilingual-replication.md`) is the as-built behavior to replicate: English is unprefixed, Spanish lives under `/es`, content is **partitioned by source language**, there is **no translation** of headlines or bodies, and each language gets an independent pipeline pass.
- The reference's known gaps (§14) must not be copied: hardcoded ES, English `/es` metadata, non-localized topic labels, ASCII-only tokenization, and a two-state switcher.
- The system adds an industry dimension on top of the reference's single site, so routing must resolve `locale × industry` without ambiguity.

## Decision

### 1. Locale set and URL policy

- Locales: `en` (default), `es`; registry-driven so a third locale is a data/catalog addition.
- **English is unprefixed**: `/{industry}/...` (e.g. `/legal`, `/legal/article/{id}`).
- **Other locales are prefixed**: `/es/{industry}/...` (e.g. `/es/legal`).
- `/` negotiates and `302`s to `/{industry}` or `/es/{industry}` (default industry per channel config).
- `/en/...` is **not** a public URL: `308` to the unprefixed path.
- Locale codes are **reserved**: an industry slug MUST NOT equal a supported locale code.
- Middleware resolves in order: explicit locale prefix → locale cookie (`sn_locale`, 1 year, `SameSite=Lax`) → `Accept-Language` → `en`. Redirects preserve the query string and never drop the locale prefix.
- Internally the app uses an `[locale]` segment (`/en/...`); the public URL stays clean, exactly like the reference.

### 2. Content-language model (partition, not translation)

- Every article carries `language` assigned **once at ingestion** from its source (`sources.language`, seeds declare theirs). There is no heuristic detection in v1.
- The pipeline partitions candidates by language **before** scoring; scoring, dedupe, layout, summaries, and desk briefs run per language pool. There is no mixed-language feed and **no cross-language dedupe** (the same story may legitimately appear in both bundles).
- AI summaries are generated **in the article's language only** - one summary per article, not one per locale. This is the reference behavior and the lowest-cost option.
- Translation of a story into another language is **out of scope for v1**; opt-in translated items are a Phase B lane (UNKNOWNS U16).
- Source `language` is validated against the supported locale set at ingest; an unsupported code rejects the source row and raises an alert (reference gap §14.13 fixed).

### 3. Fallback semantics (API and UI)

| State | API behavior | UI behavior |
|-------|--------------|-------------|
| Requested bundle **missing** (no items ever) | Serve the `en` bundle; `language: "en"`, `meta.fallback: true` | Render EN content with a visible "not yet available in Spanish" notice |
| Requested bundle **exists but empty** | Serve it as-is; `language: "es"`, empty `items` | Honest empty state in Spanish - never English content under Spanish chrome |
| Unknown locale | `400 invalid-locale` for API clients; site middleware only emits supported locales | `404` |
| Missing locale | `en` | - |

The response `language` field is authoritative; the UI MUST label a fallback rather than silently mix languages.

### 4. Presentation and SEO

- `[locale]` root layout validates the segment (`404` if unknown), sets `<html lang>`, and exports static params for every locale.
- UI strings come from typed `messages/{locale}.json`; a missing key fails CI. Article content is never machine-mixed in one paragraph.
- Switch: two-state pill (menu when >2 locales); sets `sn_locale`, then hard-navigates to the same path with the prefix added/removed (reference behavior).
- Dates use a per-locale map (`es-ES`, `en-US`) via `Intl`; times stay UTC.
- SEO: locale-aware `generateMetadata` (title, description, canonical, OpenGraph `locale`); `hreflang` for every locale + `x-default` = English; canonical per locale (`/legal` vs `/es/legal`); sitemap entries per channel with alternates (reference §10.6 fix applied).
- Topic labels are localized (`topics.label` JSONB per locale) - the reference gap §14.3 is fixed.

### 5. Adding a locale

Catalog + prompt table + source language + locale registry entry; no schema migration (language is a text column). The reference's hardcoded `es` branches are replaced by a prefix map and a negotiation loop over the registry (§14.14).

## Consequences

- **Positive:** matches the reference behavior and its proven client contract; one AI summary per article keeps LLM cost roughly half of a per-locale design; deterministic language assignment; clean English URLs; additive locales.
- **Negative:** a Spanish bundle is only as rich as the Spanish source portfolio (RISK R17); English and Spanish URLs differ in shape; two bundles double the cache/SEO surface.
- **Neutral:** translations can be added later as opt-in items without changing routing.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| Both locales prefixed (`/en/...`, `/es/...`) | Diverges from the reference and its client links; longer canonical URLs for the dominant language; no material benefit |
| Per-locale summaries of every article ("translate everything") | Doubles AI cost and crosses the reference's explicit non-goal; Spanish coverage is a sourcing problem, not a translation problem |
| Heuristic language detection | Non-deterministic; the operator already declares a feed's language |
| Hardcoded ES branches | Known reference debt (§14.14); blocks the third locale |

## References

- `/mnt/work/Projects/LogicBison/docs/news-multilingual-replication.md` §3, §4, §10.6, §14.3-§14.14
- `.work/features/industry-sites/20261105-SPEC.md` R1-R4
- `.work/features/news-api/20261105-SPEC.md` R13, R16
- `.work/plans/foundation/20261105-04-foundation-architecture.md` §5 NFR-8
- UNKNOWNS U16 (translations, deferred)

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
