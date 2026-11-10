# Cloning a deployment from a profile

One declarative file provisions a whole deployment: brand metadata, industry
channels, locale copy, themes, topics, sources, and partners. The importer is
idempotent, never deletes operator data, and runs without a web build.

Two starting points:

| File | Use |
|------|-----|
| `apps/api/config/deployments/<slug>.json` | One complete template per channel — the five launch channels plus five custom channels (`cybersecurity`, `stem-cell`, `manufacturing`, `energy`, `retail`) that are not in the reference industry JSON and exist only as profiles. Each carries skin, locale copy, disclaimers, CTA, topics, verified sources, and partner. Copy one to clone a vertical. |
| `apps/api/config/deployment.example.json` | Two-channel example that reproduces the seeded deployment exactly; running it against a fresh stack reports only `skipped` actions. |

Apply one template with `--file config/deployments/<slug>.json`, or every
template in sequence with the loop in §5.

## 1. Edit the profile

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
      "code": "LEGAL_TECH",
      "name": "Legal Services & Corporate Governance",
      "theme": {"layout": "editorial"},
      "locales": {"en": {"name": "...", "tagline": "..."}},
      "disclaimers": {"en": "News, not legal advice."},
      "cta": {"kind": "consultation", "headline": {"en": "..."}},
      "topics": [{"slug": "regulation", "label": {"en": "Regulation"}, "weight": 1.4}],
      "sources": [{"name": "ABA Journal", "feed_url": "https://www.abajournal.com/rss"}],
      "partner": {"name": "Partner", "contact_email": "partner@example.com"}
    }
  ]
}
```

Per industry, defaults are: `timezone` `America/El_Salvador`, `retention_days`
30, `sort_order` 100, `enabled` true, `locales` EN+ES named after the channel,
and a generic "news, not professional advice" disclaimer.

`theme` may be a bare layout (`{"layout": "editorial"}`) or any subset of the
tokens; missing tokens are filled from the layout preset. Every theme is
validated for required tokens and WCAG AA contrast before anything is written.

Source defaults: `language` `en`, `trust` 0.7, `poll_interval_min` 720,
`allow_http` false, `auth_type` `none`.

Licensed or publisher-gated feeds add `auth_type` (`header` or `basic`) and
`auth_secret_ref`, the **name** of an environment variable holding the secret —
never the secret itself. `auth_header_name` names the header for `header` auth
(default `Authorization`). Setting `auth_header_name: User-Agent` sends a
publisher-requested identity for that one feed; there is no global UA override. Feed URLs must be public HTTPS (HTTP requires
`allow_http: true`); test each feed with `POST /v1/admin/sources/{id}/test`
before relying on it.

Partner `weight` is a routing weight, `regions` is a free-form list of region
codes used by lead routing.

## 2. Import

```bash
# report only
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli apply-profile --file config/deployment.json --dry-run

# apply
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli apply-profile --file config/deployment.json

# one channel only
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli apply-profile --file config/deployment.json --only-industry legal
```

The command prints a JSON report: per industry `state` (`created`, `updated`,
`unchanged`), every action (`industry`, `locale`, `topic`, `source`, `partner`)
with `created` / `updated` / `skipped`, plus totals and `warnings`. Coverage
warnings flag channels below four enabled sources, a missing language, or trust
below the floor (see `docs/source-quality.md`).

Use `./bin/start.sh shell api` for a shell in the API container; the repo is
mounted at `/app`, so profile paths are relative to `apps/api`.

## 3. Guarantees

- **Idempotent.** Running the same profile twice: the second run reports zero
  `created` and zero `updated`. Tests assert this.
- **Non-destructive.** Sources, topics, partners, pins, articles, and leads that
  the profile does not mention are left alone. Removing an industry from the
  profile never deletes the channel.
- **Validated up front.** Reserved slugs, unsupported locales, duplicate feeds,
  private/HTTP feeds, invalid themes, and low-contrast themes fail before any
  write; the exit code is `2` and nothing changes.
- **Never touches secrets.** Partner emails and feed URLs only; no keys, no
  passwords.

## 4. Switching the demo industry

Quick reference: `docs/guides/switching-channels.md`.

`SN_DEFAULT_INDUSTRY` decides where `/` sends visitors. It is read at request
time, so switching needs an env change plus a web container restart — never a
rebuild:

```bash
./bin/start.sh --env dev industry behavioral-health
```

The command checks the slug against `/v1/industries`, rewrites
`SN_DEFAULT_INDUSTRY` in `.env.dev`, and recreates only the `web` container.
To switch by hand, edit `.env.dev` and run
`docker compose --env-file .env.dev -f docker-compose.dev.yml up -d --force-recreate web`.

## 5. What stays in `.env.<env>`

The profile is not a replacement for environment settings. Keep these in
`.env.dev` / `.env.prd`:

| Setting | Why |
|---------|-----|
| `APP_DOMAIN`, `APP_BASE_URL` | Public URL and canonical host |
| `SN_DEFAULT_INDUSTRY`, `SN_DEFAULT_LOCALE` | Web entry redirect |
| `REFRESH_INTERVAL_MINUTES` | Worker cadence (profile value is advisory) |
| `AI_*` | Provider key, model, monthly budget, per-run item cap |
| `SECRET_KEY`, `ADMIN_*` | Session signing and console credentials |
| `POSTGRES_*`, `REDIS_*`, ports | Stack identity and isolation |

`brand` and `site_url` in the profile are metadata for operators and tooling;
they do not rewrite the running environment. The importer warns when
`refresh_interval_minutes` differs from the running setting.

## 6. Clone checklist

1. Copy `apps/api/config/deployments/<slug>.json` to `deployment.json` (keep
   real partner contacts out of git if they are customer data).
2. Duplicate one `industries` object; change `slug`, `code`, `name`, theme,
   locale copy, disclaimers, CTA, topics, and sources.
3. Add only feeds you have verified with the test-fetch endpoint, one per
   language. Trust below 0.75 needs an editorial reason.
   Run every template at once:
   ```bash
   for f in config/deployments/*.json; do
     docker compose --env-file .env.dev -f docker-compose.dev.yml exec -T api \
       python -m news_api.cli apply-profile --file "$f"
   done
   ```
4. Run `--dry-run`; read the report; then apply.
5. Trigger a refresh and verify:
   ```bash
   POST /v1/admin/refresh {"industry":"<slug>","force":true}
   GET  /v1/news/bundle?industry=<slug>&locale=en
   GET  /v1/industries/<slug>?locale=es
   ```

   Regenerate the canonical channel inventory after applying a profile:

   ```bash
   ./bin/channels.sh --write
   ```
6. Open `https://<domain>/<slug>` and `/es/<slug>`; check theme contrast with
   `pnpm check` in `apps/web` (run inside the `web` container).

## 7. Going beyond the reference industries

The profile importer is how an implementation stops matching the five reference
verticals: `apps/api/config/deployments/cybersecurity.json` and
`apps/api/config/deployments/stem-cell.json` were applied to the running stack
without a code change. See `docs/customization.md` for the full
contract — what is data, what needs code, and how to fork.

## 8. Relationship to the admin console

The console (`/admin` → Channels) remains the interactive path for one-off
edits. The profile importer is the reproducible path: it converges a deployment
to a file, and the file can be reviewed and versioned. Both write the same
tables; the importer never deletes.

## Next action

Add a real vertical by duplicating an industry block and verifying its feeds.
