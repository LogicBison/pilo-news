# ADR 007 - Internationalization: locale-prefixed routes + typed catalogs

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** how EN/ES (and future locales) work across UI and content.

## Context

- Brief: English and Spanish required; default language = browser/environment setting; one-click manual switch; must extend to other languages.
- Content has two layers: **UI strings** (nav, labels, disclaimers) and **article summaries** (AI-generated per locale).
- SEO requires crawlable, distinct URLs per locale (`hreflang`), not a client-only toggle.

## Decision

- **Routes:** `/{locale}/{industry}/...` with `locale ∈ {en, es}`; bare `/` negotiates via `Accept-Language`, then cookie `sn_locale`, then `en`, and redirects (302) to the chosen locale.
- **UI strings:** typed JSON catalogs in `apps/web/src/messages/{en,es}.json`; a small `t()` helper with compile-time key checks; missing key = build error in CI (no silent English fallback except where explicitly marked).
- **Switcher:** server action sets `sn_locale` cookie (1 year, `SameSite=Lax`) and redirects to the same path in the other locale.
- **Content:** API accepts `locale`; returns `title`/`summary` in that locale when available, otherwise the source language **with an explicit `language` field** and UI label ("available in English") - never machine-mixed prose.
- **Adding a locale:** add catalog + prompts + `locales` array entry + channel copy; no schema migration (article language is a text column).
- **Dates/numbers:** `Intl.DateTimeFormat`/`Intl.NumberFormat`; times stored UTC, rendered in `America/El_Salvador` by default, overridable per channel theme.

## Consequences

- **Positive:** crawlable localized URLs; testable key completeness; content fallback is explicit; new locales are additive.
- **Negative:** duplicate page trees per locale (cache/SEO surface doubles); two summary passes per item (AI cost); cookie + redirect adds one hop on first visit.
- **Neutral:** no third-party i18n framework dependency; if catalogs grow beyond a few hundred keys, migrate to `next-intl` behind the same `t()` interface.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| Client-only language toggle | Not crawlable; breaks `hreflang`; flashes wrong language |
| Header/query-only locale | Poor SEO and shareability |
| `next-intl` from day one | Adds a dependency and routing conventions before the need is proven |
| Machine-translate article text | Copyright + accuracy risk; we summarize, not republish |

## References

- Doc 01 § success criteria S2
- Doc 04 §5 NFR-8
- SPEC `.work/features/industry-sites/20261105-SPEC.md` R3

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
