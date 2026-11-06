# switching channels

answer first: the landing channel is one env var. set it, recreate `web`, done. no rebuild.

## switch the landing channel

```bash
# dev
./bin/start.sh --env dev industry stem-cell

# prd
./bin/start.sh --env prd industry legal
```

what it does: checks the slug against `/v1/industries`, rewrites `SN_DEFAULT_INDUSTRY` in `.env.<env>`, recreates only the `web` container.

manual equivalent:

```bash
# edit .env.dev
SN_DEFAULT_INDUSTRY=stem-cell

docker compose --env-file .env.dev -f docker-compose.dev.yml up -d --force-recreate web
```

verify:

```bash
curl -s -o /dev/null -w "%{http_code} %{redirect_url}\n" http://localhost:43991/
# 307 http://localhost:43991/stem-cell
```

## open any channel without switching

every channel is reachable by path; the landing redirect only affects `/`.

```
http://localhost:43991/<slug>
http://localhost:43991/es/<slug>
```

list slugs:

```bash
curl -s http://localhost:46105/v1/industries | python3 -c "import sys,json; print([c['slug'] for c in json.load(sys.stdin)['data']])"
```

current set: `legal`, `financial`, `behavioral-health`, `education`, `logistics`, `cybersecurity`, `stem-cell`, `manufacturing`, `energy`, `retail`.
canonical list with EN/ES URLs: `docs/channel-inventory.md` (regenerate with `./bin/channels.sh --write`).

## add an industry or custom subject

1. copy a template and rename it:

```bash
cp apps/api/config/deployments/legal.json apps/api/config/deployments/<slug>.json
```

2. edit the file. change `slug`, `code`, `name`, `theme`, `locales`, `disclaimers`, `cta`, `topics`, `sources`, `partner`. set `default_industry` to the new slug. keep `slug` to `^[a-z0-9-]{2,40}$`.

3. dry-run:

```bash
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli apply-profile --file config/deployments/<slug>.json --dry-run
```

4. apply:

```bash
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli apply-profile --file config/deployments/<slug>.json
```

5. first fetch (2-4 min, includes summaries):

```bash
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli refresh --industry <slug> --force
```

6. verify page, API, and feeds:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:43991/<slug>
curl -s "http://localhost:46105/v1/news/bundle?industry=<slug>&locale=es" | head -c 200
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli verify-sources --industry <slug>
```

rules the importer enforces: theme contrast, supported locales (`en`, `es`), public https feeds, no duplicate feeds, at least one source per language. it never deletes sources, articles, pins, or leads.

## switch back

```bash
./bin/start.sh --env dev industry legal
```

## troubleshooting

| symptom | cause | fix |
|---------|-------|-----|
| `/` still opens the old channel | `web` not recreated | `up -d --force-recreate web` |
| `unknown industry` from the helper | slug typo or channel not imported | `curl /v1/industries`, then apply the profile |
| `/<slug>` returns 404 | channel missing or disabled | apply the profile; check `enabled` |
| page renders but empty | no refresh yet | `refresh --industry <slug> --force` |
| Spanish column empty | no ES source or items older than the window | add an ES feed, check retention |
| importer exits 2 | profile invalid (theme, feed, locale) | read stderr; it names the field |

## related

- `docs/deployment-profile.md` — full profile contract and guards
- `docs/customization.md` — what is data vs what needs code
- `docs/source-quality.md` — feed gates and trust bands
