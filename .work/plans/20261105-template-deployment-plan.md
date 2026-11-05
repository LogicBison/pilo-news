# Template deployment plan - next session

**Status:** proposed · **Needs:** operator choice on profile format (file vs admin import).
**Next action:** implement `apps/api/config/deployment.example.json` + an idempotent import command, then use it to clone a second channel/deployment.

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

## Next-session tasks

1. Define the profile schema + example; validate with Pydantic.
2. Implement `apply-profile` service + CLI + tests (idempotency twice).
3. Add a source-import bulk path that reuses `validate_feed_url`/test-fetch.
4. Extend `docs/adding-an-industry.md` into a deployment guide (feed choices,
   trust tuning, prompt/scoring overrides, AI budget, CTA/partner).
5. Verify a second profile end to end: `up`, `apply-profile`, `refresh`,
   `/v1/news/bundle` EN/ES, web pages, sitemap.
6. Run pending verification: k6, prd deploy/rollback, GitHub CI.

## Guardrails

- No per-industry code forks; every difference stays in data/config.
- No feed scraping beyond approved RSS/Atom; language is declared, never detected.
- Theme changes must pass contrast; prompts stay per-language.
- Profile import never deletes sources/articles/pins/leads.
