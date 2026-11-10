# Channel domains

Every channel is its own site. In production that is a subdomain:

```
https://heraldfox.com            -> the lobby: every desk, the services page
https://stem-cell.heraldfox.com  -> the stem-cell channel (English)
https://stem-cell.heraldfox.com/es
https://stem-cell.heraldfox.com/about
https://stem-cell.heraldfox.com/feed.xml
https://heraldfox.com/admin      -> editorial console (apex only)
```

Path URLs keep working — `https://heraldfox.com/stem-cell/about` renders the page
with a canonical pointing at the channel host — so old links never break. On the
channel host itself a redundant `/<slug>` prefix is redirected away (`308`).

## How it resolves

| Layer | Behaviour |
|-------|-----------|
| nginx (prd) | One server block per host, generated from `ops/nginx/sites/`. Terminates TLS, proxies `/v1/*` to the API and everything else to the web app, sets `X-SN-Channel`. |
| Middleware | Maps host → channel (`Host` against `SN_CHANNEL_DOMAIN`, or the proxy header), rewrites `/<path>` to `/<locale>/<slug>/<path>`, keeps `/admin` on the apex. |
| App | `lib/url.ts` builds every internal link, canonical and feed URL from the request host, so a page never emits a `/<slug>` prefix on a subdomain. |

The channel domain comes from `channelDomain()` in `apps/web/src/lib/hosts.ts`:

1. `SN_CHANNEL_DOMAIN` when set (dev sets it to `localhost`).
2. `APP_DOMAIN` when `APP_ENV=prd`.
3. empty → path mode.

## Local development

`dev` runs with `SN_CHANNEL_DOMAIN=localhost`, so subdomains work with no proxy:
`*.localhost` resolves to `127.0.0.1` in every browser.

```
http://localhost:43991/              -> the lobby (all eleven desks)
http://stem-cell.localhost:43991/    -> channel home
http://stem-cell.localhost:43991/es
http://legal.localhost:43991/about
```

Path URLs still work on the apex host, which is what the Playwright suite uses.

Verify both shapes with:

```bash
./bin/start.sh dev hosts
./bin/start.sh dev domains --write   # also renders the nginx files
```

## Production

One certificate covers the apex, `www`, and every channel host. Two phases,
because nginx refuses to start with a `443` block whose certificate does not
exist yet, and certbot needs port 80 answering for every host first.

### Phase 1 — port 80 answers

```bash
./bin/start.sh --env prd preflight
./bin/start.sh --env prd domains --write --http-only   # no 443 blocks yet
sudo mkdir -p /var/www/certbot
# one include file, not a directory symlink: nginx's `include sites-enabled/*`
# tries to read every entry, and a directory entry fails `nginx -t`
sudo sh -c 'printf "include /srv/system-news/ops/nginx/sites/*.conf;\n" > /etc/nginx/sites-enabled/system-news.conf'
sudo nginx -t && sudo systemctl reload nginx
```

DNS must already point every host at this machine (apex, `www`, and one record
per channel). Check it before issuing:

```bash
for h in heraldfox.com www.heraldfox.com stem-cell.heraldfox.com; do
  printf '%-34s %s\n' "$h" "$(getent ahosts "$h" | awk 'NR==1{print $1}')"
done
```

### Phase 2 — issue the certificate

```bash
./bin/start.sh --env prd certs            # prints the exact command and the host list
sudo ./bin/start.sh --env prd certs --run # or let the script drive certbot
```

`certs --run` refuses to start without root or certbot, prints the names it will
request, runs a **staging dry run first** (a typo there costs no rate limit), then
issues for real. It writes to `/etc/letsencrypt/live/<SSL_CERT_NAME>/` and needs
`/var/www/certbot` to exist.

### Phase 3 — turn TLS on

```bash
./bin/start.sh --env prd domains --write   # full config, 443 blocks included
sudo nginx -t && sudo systemctl reload nginx
./bin/start.sh --env prd certs --check     # every host covered? expiry?
```

`certs --check` reads the installed certificate and reports, per host, whether it
is covered — by an exact name or by a wildcard — plus days to expiry. It is the
fastest way to tell "certificate is fine" from "one channel was added and nobody
reissued".

### Multi-domain or wildcard

| | Multi-SAN (default) | Wildcard |
|---|---|---|
| Names | apex + `www` + each channel, one cert | `heraldfox.com` + `*.heraldfox.com` |
| Challenge | HTTP-01, needs port 80 reachable | DNS-01, needs a DNS plugin + API token |
| New channel | reissue with `--expand` (one command, `certs` prints it) | nothing to do |
| Cert passes for | only the names listed | any subdomain, including ones we do not run |
| File location | `/etc/letsencrypt/live/<SSL_CERT_NAME>/` | same |

Start with multi-SAN: no DNS credentials, no certificate that would validate a
phishing host under our domain. Move to wildcard only if channel hosts change
often or port 80 is not reachable from the internet.

```bash
# wildcard, for reference (requires the provider's certbot plugin)
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/heraldfox.ini \
  -d heraldfox.com -d '*.heraldfox.com' --cert-name heraldfox.com
```

`SSL_CERT_NAME` and `SSL_CERT_DIR` do not change between the two strategies.

### Renewal

certbot's systemd timer renews both shapes. The generated sites serve
`/.well-known/acme-challenge/` on port 80 for every host, so renewals keep
working after the redirect goes live.

```bash
sudo certbot renew --deploy-hook 'systemctl reload nginx'
sudo systemctl list-timers | grep certbot
```

### Generated files

`ops/nginx/sites/` is generated and git-ignored; edit
`ops/nginx/site.conf.template` instead. The template assumes:

- `SSL_CERT_DIR` (default `/etc/letsencrypt/live/<SSL_CERT_NAME>/`) holds
  `fullchain.pem` and `privkey.pem`,
- certbot's `/etc/letsencrypt/options-ssl-nginx.conf` and `ssl-dhparams.pem` exist
  (`certbot` package on Debian/Ubuntu installs both),
- `/var/www/certbot` is the webroot, written by certbot as root and read by nginx.

### Adding a channel

```bash
./bin/start.sh --env prd domains --write --http-only   # if the cert has no name for it yet
# add the DNS record, then:
sudo certbot certonly --webroot -w /var/www/certbot --expand \
  -d heraldfox.com -d www.heraldfox.com -d <existing>... -d new-slug.heraldfox.com \
  --cert-name heraldfox.com
./bin/start.sh --env prd domains --write
sudo nginx -t && sudo systemctl reload nginx
./bin/start.sh --env prd certs --check
```

A host without a generated server block gets no certificate and no traffic: the
platform cannot issue certificates for names it does not serve. If a certificate
cannot cover the new name yet, the channel keeps its path URL
(`https://heraldfox.com/<slug>`) and everything else follows automatically.

## Reachability check

`./bin/start.sh --env <env> hosts` asserts the contract over real HTTP with the
`Host` header the edge sends:

- apex `/` renders the lobby and lists all eleven desks
- channel `/`, `/es`, `/about` render
- `/<slug>/about` redirects to `/about`
- `/admin` redirects to the apex
- `/feed.xml` and `/sitemap.xml` are host-scoped
- no page emits a `/<slug>` prefixed link
- the canonical points at the channel host

`./bin/start.sh test` runs it whenever channel subdomains are enabled.
