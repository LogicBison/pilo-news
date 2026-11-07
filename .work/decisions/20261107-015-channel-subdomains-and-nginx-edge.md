# ADR 015 - Channel subdomains and the host nginx edge

**Status:** Decided · 2026-11-07 · **Supersedes:** ADR 005 §Decision (the `caddy` service is replaced by the host's nginx) · **Decision authority:** owner instruction 2026-11-07 ("each channel must be a sub-domain… production must use the host's nginx").
**Needs:** nothing to unblock; TLS material is an operator action (see Consequences).

**Decides:** how a channel is addressed, and what terminates TLS in production.

## Context

- Channels are the product's unit: eleven today, each with its own editorial identity, offers and feeds.
- v1 addressed them by path: `/<slug>`, `/es/<slug>`. That works for one origin but reads as one publication with sections, and every channel shares one origin for cookies, analytics and search-console entries.
- The owner's production requirement is `https://stem-cell.heraldfox.com`.
- ADR 005 chose Caddy inside the compose stack. The production host already runs nginx as its edge, and the owner requires that nginx stay the TLS terminator so certificates, renewals and the other sites on that host share one mechanism.

## Decision

- **A channel's public URL is `https://<slug>.<APP_DOMAIN>`**, with the default locale at `/` and Spanish at `/es`. The apex serves `/` by redirecting to the default channel; `<slug>` paths on the apex keep working and carry a canonical pointing at the channel host.
- **`APP_DOMAIN` + `APP_ENV=prd` is the switch.** `SN_CHANNEL_DOMAIN` overrides it, which is how dev gets `http://stem-cell.localhost:43991` with no proxy at all.
- **One Next.js tree serves both shapes.** Middleware maps host → channel and rewrites `/<path>` to `/en/<slug>/<path>`; the app has no idea whether it was reached by path or subdomain, and internal links are built from the request host.
- **TLS and routing live on the host's nginx**, configured by `ops/nginx/site.conf.template` and one generated server block per channel. Compose publishes only loopback ports; nothing is exposed directly.
- **One certificate covers the apex and every channel host** (multi-SAN via HTTP-01, or a wildcard via DNS-01). `SSL_CERT_NAME` names it; `SSL_CERT_DIR` locates it.
- **No wildcard-by-default and no on-demand issuance.** A host that is not in the generated set never gets a certificate, so the platform cannot be used to mint certificates for names it does not own.

## Consequences

- **Positive:** one canonical URL per channel; per-channel search-console and analytics attribution; subdomain isolation for cookies; the host's existing nginx, certbot and firewall stay the single edge.
- **Negative:** a new channel needs `./bin/start.sh --env prd domains --write` plus a certificate that covers the new name, then an nginx reload. Certbot HTTP-01 needs `/var/www/certbot` served on port 80 for every host.
- **Neutral:** the app still boots and serves path URLs, so an edge without subdomain config degrades to the v1 behaviour instead of failing.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| Path URLs in production (`/stem-cell`) | Weak per-channel identity; one origin for cookies and analytics; owner requirement is explicit |
| Caddy in compose (ADR 005) | The host's nginx already owns 80/443 and renewals; two edges on one host fight over ports |
| Wildcard `*.heraldfox.com` only | Requires DNS-provider credentials in the deployment and widens the certificate to names we may never serve |
| One container per channel | Eleven images to build, patch and monitor for one codebase |
| Subdomain → path redirect at the edge | Two URL shapes in the index; canonical churn; `Link` prefetch would follow the redirect on every click |

## References

- `apps/web/src/middleware.ts`, `apps/web/src/lib/hosts.ts`, `apps/web/src/lib/url.ts`
- `ops/nginx/site.conf.template`, `./bin/start.sh domains`
- `docs/domains.md`, `docs/guides/migrate-dev-to-prod.md`
- ADR 005 (hosting), ADR 012 (release flow)
