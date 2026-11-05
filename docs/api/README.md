# System News API v1

**Status:** implemented · **Contract:** `openapi.v1.json` (generated) · **Base URL:** `https://{host}/v1`

Public reads need no key. `X-API-Key: sn_live_...` raises the rate limit. Admin routes use an httpOnly JWT cookie plus `X-CSRF-Token`.

## Quickstart

```bash
curl -s "$API/v1/health"
curl -s "$API/v1/industries"
curl -s "$API/v1/news?industry=legal&locale=en&limit=5"
curl -s "$API/v1/news/bundle?industry=legal&locale=es"
curl -s "$API/v1/news/{id}?industry=legal&locale=en"
curl -s "$API/v1/topics?industry=legal&locale=en"
```

Every success uses the envelope:

```json
{ "data": [], "meta": { "request_id": "...", "locale": "en", "language": "en", "fallback": false, "generated_at": "2026-11-05T14:03:00Z", "next_cursor": null } }
```

Errors are RFC 7807 with `type`, `title`, `status`, `detail`, `instance`, and `request_id`.

## Language and fallback

`locale` selects a single-language bundle. Items are never mixed. A missing
language bundle falls back to English with `meta.fallback = true`; an existing
but empty bundle stays empty with `fallback = false`. Unsupported locales return
`400 invalid-locale`.

## Pagination

Use `limit` (1-50) and the opaque `meta.next_cursor`. Sorting is deterministic:
score, published time, id. Unknown query parameters return `400`.

## Caching

Public reads return a weak `ETag` and `Cache-Control: public, max-age=60,
stale-while-revalidate=300`; send `If-None-Match` to get an empty `304`.

## Rate limits

| Scope | Limit |
|-------|-------|
| Keyless per IP | 120 req/min |
| Per API key | key-configured (default 600/min) |
| Contact | 3/hour/IP |
| Leads | 5/hour/IP |
| Admin login | 5/min/IP |

`429` responses carry `Retry-After` and `RateLimit-*` headers.

## Leads and contact

`POST /v1/leads` requires explicit `consent: true`, stores the consent version
and timestamp, hashes IP/UA, routes to the channel partner, and returns no PII.
`POST /v1/contact` is the desk inbox. Honeypot and duplicate suppression are
handled server-side.

## Admin

`POST /v1/admin/auth/login` sets `sn_admin` (httpOnly) and `sn_csrf` cookies.
Mutating calls require `X-CSRF-Token` equal to the `sn_csrf` cookie.
`POST /v1/admin/refresh` accepts `{industry, force, full_reset, confirmation}`;
`full_reset` requires `confirmation: "RESET"`.

## Adding a channel

`POST /v1/admin/industries` is data-only: slug, name, code, theme, locales,
disclaimers, CTA, and optional topics. The public site, sitemap, and API discover
the new channel automatically. See `docs/adding-an-industry.md`.

## Notes

- No article bodies or media are stored; every item links to its publisher.
- The committed `openapi.v1.json` is regenerated with
  `python scripts/export_openapi.py` from `apps/api`; CI fails on a diff.
