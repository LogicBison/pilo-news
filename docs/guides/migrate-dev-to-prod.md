# Migrate dev to production

Goal: take everything that makes the dev stack what it is — database, channels,
sources, articles, leads, API keys, offers, deployment config, media, secrets —
and land it on the production host with the production URLs.

Nothing here needs Docker volume access. A `pg_dump` is portable across hosts
and image versions; a Postgres data directory is not.

## 1. On the dev machine: one command

```bash
./bin/start.sh dev preflight     # catch a broken env before you package it
./bin/start.sh dev backup
```

The bundle records the checkout's git SHA but **does not contain code or images**.
Commit and push before you package, and clone that SHA on the target; `up` builds
the images there.

`backups/news-dev-bundle-<timestamp>.tar.gz` (mode 600) contains:

| Member | What it is | Why it is needed |
|--------|------------|------------------|
| `db.sql.gz` | `pg_dump --clean --if-exists --no-owner --no-privileges` | channels, sources, articles, summaries, topics, pins, leads, contacts, API keys, offer issues, audit trail, migration ledger |
| `config/` | `apps/api/config/**` (deployment profiles, prompts, scoring, offers, seeds) | channel definitions that were tuned on dev |
| `env/.env.dev` | the environment file, secrets included | `AI_API_KEY`, SMTP credentials, `ADMIN_PASSWORD`, admin password hash |
| `media/` | `apps/web/public/**` | channel photography, credits, skins |
| `ops/nginx/` | generated site blocks | the exact hosts dev was serving |
| `manifest.json` | git SHA, migration, row counts, channel slugs | proof of what is inside; paste it into the release note |
| `SHA256SUMS` | checksums for every member | restore refuses a corrupt or truncated archive |

The bundle contains credentials. Treat it like a password: copy it over SSH/SFTP,
never through chat, email or a public bucket, and delete it from the target when
the restore is verified.

## 2. On the production host: stack first, data second

```bash
git clone <repo> /srv/system-news && cd /srv/system-news
./bin/start.sh --env prd init-env          # random SECRET_KEY, admin, Postgres and Redis passwords
$EDITOR .env.prd                           # real domain, ports, AI key
./bin/start.sh --env prd preflight         # must report no blocking issues
```

Set at least:

```ini
APP_ENV=prd
APP_DOMAIN=heraldfox.com
APP_BASE_URL=https://heraldfox.com
SN_CHANNEL_DOMAIN=                         # empty → derived from APP_DOMAIN
SSL_CERT_NAME=heraldfox.com
SN_DEFAULT_INDUSTRY=legal
```

`init-env` already generated `SECRET_KEY`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`
and both matching URLs. If you rotate either password, change its URL in the same
edit: the API reads `DATABASE_URL`/`REDIS_URL`, while Postgres and Redis read the
password variables.

Then bring up the stack and land the data:

```bash
./bin/start.sh --env prd up                # builds images, starts everything
scp and/or copy the bundle to ./backups/
./bin/start.sh --env prd restore           # pick the bundle; type restore-prd
```

`restore` verifies `SHA256SUMS`, replays the SQL, stages `config/`, `media/`,
`ops/` and `env/` under `backups/restored/<bundle>/`, then runs migrations so a
bundle from an older checkout is brought up to the current schema. Use
`restore --all` to also copy config, media and nginx sites into the checkout; the
interactive menu asks the same question (`apply config, media and nginx sites?`).

Redis is deliberately not in the bundle: it holds a cache and a queue, both
rebuilt by the worker on the next cycle.

## 3. Keep the production secrets or adopt the dev ones

The bundle carries dev's `SECRET_KEY` and `ADMIN_PASSWORD`. Two valid choices:

- **Adopt dev secrets** (fewest surprises): copy `AI_API_KEY`, SMTP credentials and
  `ADMIN_PASSWORD_HASH` from `backups/restored/<bundle>/env/.env.dev` into `.env.prd`.
  Admin sign-in and AI summaries keep working unchanged.
- **Keep production secrets** (default): production `init-env` already generated a
  fresh `SECRET_KEY` and admin password. AI and SMTP credentials still have to be
  copied from the bundle, or summaries and lead notifications stay off.

Either way, sessions do not survive a `SECRET_KEY` change: sign in again.

## 4. Edge, DNS and certificate

```bash
./bin/start.sh --env prd domains --write   # one nginx server block per channel
./bin/start.sh --env prd certs             # prints the certbot command
```

Add the DNS records, issue the certificate, include the generated sites and
reload nginx — the exact sequence is in `docs/domains.md`.

## 5. Verify before telling anyone the URL

```bash
./bin/start.sh --env prd status
./bin/start.sh --env prd hosts        # subdomain routing contract, over HTTP
./bin/start.sh --env prd migrate      # idempotent; expect "nothing to apply"
curl -fsS https://heraldfox.com/v1/health
curl -fsS https://stem-cell.heraldfox.com/feed.xml | head
```

Then, in the browser: the channel home, `/es`, `/about`, the admin console sign-in,
and one lead submission on a channel host (it exercises the `/api/proxy` → `/v1`
path that the edge must not swallow).

`hosts` failing with `404` on a channel host almost always means the bundle was
restored into a database that does not have that channel, or nginx is pointing at
the wrong loopback port.

## Rollback

- Data: keep the previous bundle, `restore` it.
- Code: redeploy the previous image tag (ADR 012).
- Edge: previous `ops/nginx/sites/` snapshot is inside the same bundle.

## What is not in the bundle

| Not included | Why | What to do instead |
|--------------|-----|--------------------|
| Docker volumes | not portable across image versions | `db.sql.gz` is the supported path |
| Application code and images | the bundle is data/config, not a release | clone the repo at the manifest `git.sha`; `up` builds the images |
| TLS certificates | host-specific, issued per host | `./bin/start.sh --env prd certs` |
| Redis data | cache + queue, rebuilt automatically | nothing |
| `.env.prd` | generated on the target | `init-env`, then copy the credential keys you need |
| Off-site copies | out of scope for a local bundle | upload the bundle to the backup bucket (ADR 005, O3) |
