# Template deployment plan - next session

**Status:** done · **Needs:** nothing - CLI path chosen over the admin import endpoint.
**Next action:** clone a customer vertical from `apps/api/config/deployments/<slug>.json`; re-run `verify-sources`.

## Current capability

- Channel creation is data-only: `POST /v1/admin/industries` (theme, locales,
  disclaimers, CTA, topics) and the admin `Channels` tab.
- Sources are data: `POST /v1/admin/sources` (feed URL, language, trust, poll
  interval, allow_http) with SSRF validation and test-fetch.
- Scoring is `apps/api/config/scoring.json`; prompts are
  `apps/api/config/prompts/{en,es}.json`; curated pinned items are
  `apps/api/config/seeds.json`.
- Web reads only `/v1`; no per-industry build step.
- Per-deployment env: brand-adjacent settings (`APP_BASE_URL`, `APP_DOMAIN`,
  `SN_DEFAULT_INDUSTRY`, `SN_DEFAULT_LOCALE`, refresh interval, AI budget),
  plus random host ports and isolated compose networks.

## Gap

Creating a *new deployment* is still manual: env copy, channel API calls, source
API calls, optional seeds/topics, and verification. There is no single declarative
profile and no import command. Replicating a vertical per customer would be
error-prone.

## Proposed profile

Add `apps/api/config/deployment.example.json`:

```json
{
  "brand": "System News",
  "site_url": "https://example.com",
  "default_locale": "en",
  "default_industry": "legal",
  "refresh_interval_minutes": 720,
  "industries": [
    {
      "slug": "legal",
      "name": "Legal Services & Corporate Governance",
      "code": "LEGAL_TECH",
      "theme": {"layout": "editorial"},
      "locales": {"en": {"name": "..." , "tagline": "..."}, "es": {"name": "..."}},
      "disclaimers": {"en": "...", "es": "..."},
      "cta": {"kind": "consultation", "headline": {"en": "...", "es": "..."}},
      "topics": [{"slug": "regulation", "label": {"en": "Regulation"}, "keywords": {"en": ["compliance"]}}],
      "sources": [{"name": "ABA Journal", "feed_url": "https://...", "language": "en", "trust": 0.92}],
      "partner": {"name": "...", "contact_email": "..."}
    }
  ]
}
```

## Proposed import

1. `python -m news_api.cli apply-profile --file config/deployment.json`
   (inside api container; admin auth not required because it is an operator CLI).
2. Idempotent per slug: upsert channel/locale/theme/disclaimers/CTA; upsert topics;
   insert missing sources; upsert partner; never delete operator data.
3. Validate theme (same `validate_theme`), language, SSRF, duplicate feeds.
4. Emit a diff summary: created/updated/skipped.
5. Optional `--dry-run` and `--only-industry`.

Alternative: `POST /v1/admin/deployments/import` with the same payload for
remote provisioning; keep the CLI as the offline path.

## Outcome (2026-11-05)

1. Schema + example: `apps/api/config/deployment.example.json`, validated with Pydantic.
2. `apply-profile` service (`news_api.provisioning`) + CLI (`--dry-run`, `--only-industry`); 18 tests including a no-database run against injected ports.
3. Sources are imported inside the same profile; each feed is validated with `validate_feed_url`.
4. Docs: `docs/deployment-profile.md`, `docs/source-quality.md`, `docs/customization.md`.
5. Verified end to end: `cybersecurity` channel created from a profile only (13 entities), refreshed, serving `/v1/news` and `/cybersecurity`.
6. Still pending: k6, prd deploy/rollback, GitHub CI (owner/ops).

## Guardrails

- No per-industry code forks; every difference stays in data/config.
- No feed scraping beyond approved RSS/Atom; language is declared, never detected.
- Theme changes must pass contrast; prompts stay per-language.
- Profile import never deletes sources/articles/pins/leads.
