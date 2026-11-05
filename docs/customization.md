# Customizing an implementation

System News is one codebase with channel-as-data. The five reference industries
in `.work/docs/integration/industries-v1.1.0/data.json` are a starting
portfolio, not a limit: the running system already serves two extra channels
(`cybersecurity`, `stem-cell`) that exist only as profile files.

## 1. Add an industry without touching code

Create `apps/api/config/deployments/<slug>.json` (copy an existing template) and
import it:

```bash
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli apply-profile --file config/deployments/<slug>.json --dry-run
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli apply-profile --file config/deployments/<slug>.json
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli refresh --industry <slug> --force
```

Example: `apps/api/config/deployments/stem-cell.json` is a complete
regenerative-medicine channel with six sources (four English, two Spanish).

The channel, its EN/ES pages, SEO metadata, sitemap entries, disclaimers, CTA,
lead form, and `/v1` endpoints appear immediately — no build, no route, no
component. Review the profile's `warnings`; `coverage` lists missing sources or
languages.

## 2. What is data (edit the profile or console)

| Surface | Where |
|---------|-------|
| Channel identity, code, sort order, enabled | profile `industries[].slug/code/name/sort_order/enabled` |
| Skin (colors, radius, fonts, layout) | profile `theme`; validated for tokens + WCAG AA contrast |
| Locale copy (name, tagline) | profile `locales` |
| Disclaimers | profile `disclaimers` |
| CTA copy and kind | profile `cta` (`consultation` or `brief`) |
| Topics and scoring keywords | profile `topics`, or `/admin` → Topics |
| Sources, language, trust, poll interval | profile `sources`, or `/admin` → Sources |
| Partner and lead routing | profile `partner`, or `/admin` → Partners |
| Refresh cadence per deployment | `REFRESH_INTERVAL_MINUTES` in `.env.<env>` |
| Default landing channel | `SN_DEFAULT_INDUSTRY` in `.env.<env>` |
| AI model, budget, item cap | `AI_*` in `.env.<env>` |
| Scoring weights and thresholds | `apps/api/config/scoring.json` |
| Summary prompts per language | `apps/api/config/prompts/{en,es}.json` |
| Curated pinned stories | `apps/api/config/seeds.json` |

## 3. What needs code (extension points)

| Change | Work |
|--------|------|
| A third content language | add the locale to `SUPPORTED_LOCALES`, add `config/prompts/<locale>.json`, add `apps/web/src/messages/<locale>.json`, extend the middleware locale negotiation, and seed `industry_locales` rows |
| A new theme layout variant | add the preset to `DEFAULT_THEMES` and a `[data-layout]` block in `globals.css` |
| A new CTA kind | extend the lead `kind` check in the leads schema and the form copy |
| A new scoring signal | `apps/api/src/news_api/articles/domain/scoring.py` + fixtures |
| A new public field | API `docs/api/openapi.v1.json` + web DTO in `lib/api.ts` |

Everything in this table is a deliberate, reviewable change; nothing in §2 is.

## 4. Fork an implementation

The repo is a complete deployment, not a library. To run a branded fork:

1. Copy the repo, then `./bin/start.sh init-env --env dev` (fresh secrets and
   ports; every stack is isolated on its own Docker networks).
2. Write your profile — or start from `config/deployments/<slug>.json`.
3. Apply the profile, refresh, verify with `verify-sources`.
4. Change `.env.<env>` brand-adjacent values (`APP_DOMAIN`, `APP_BASE_URL`,
   `SN_DEFAULT_INDUSTRY`, AI budget).
5. If you need a different copy/UX, edit `apps/web/src/messages/`, the components
   under `apps/web/src/components/`, or the tokens in `globals.css`.

## 5. Guardrails

- No per-industry code forks: every difference stays in data or config.
- Themes must pass contrast; profiles are rejected otherwise.
- Prompts stay per language; the system never machine-translates.
- A profile import never deletes sources, articles, pins, or leads.
- Sources must pass the quality policy (`docs/source-quality.md`).

## Next action

Add your first custom channel from a copied template and run the dry-run first.
