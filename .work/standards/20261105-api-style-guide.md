# API Style Guide - System News v1

**What it is:** the binding contract style for `/v1` - enough detail to implement the HTTP layer without guessing.
**Status:** Approved for implementation (2026-11-05) · **Needs:** nothing.

---

## 1. Base and versioning

- Base URL: `https://{host}/v1`.
- Version in the path; additive changes only within `v1`; breaking changes → `/v2` with 6-month overlap + `Sunset`.
- `Content-Type: application/json; charset=utf-8` on both requests and responses.
- `X-Request-Id` accepted; otherwise generated and echoed in `meta.request_id` and `X-Request-Id`.

## 2. Success envelope

```json
{
  "data": [ ... ],
  "meta": {
    "request_id": "01J...",
    "locale": "en",
    "generated_at": "2026-11-05T14:03:00Z",
    "next_cursor": "eyJzIjox..."
  }
}
```

- `data` is an object for single resources and an array for collections.
- `meta.next_cursor` is `null` on the last page.
- No top-level fields besides `data` and `meta` (no `error: null`).

## 3. Errors (RFC 7807)

```json
{
  "type": "https://system-news.example/problems/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "No industry with slug 'unknown'.",
  "instance": "/v1/industries/unknown",
  "request_id": "01J..."
}
```

| Status | When |
|--------|------|
| 400 | Malformed query/body, unknown enum value |
| 401 | Missing/invalid admin credentials |
| 403 | Valid identity, insufficient scope |
| 404 | Unknown resource |
| 409 | Conflict (duplicate source URL, pin collision) |
| 422 | Semantic validation failure (Pydantic) |
| 429 | Rate limit exceeded (`Retry-After`) |
| 502 | Upstream (feed/AI) failure that blocks the operation |
| 503 | Dependency unavailable (DB/Redis) |

Never return stack traces, SQL, or upstream bodies.

## 4. Resources and naming

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/v1/health` | none | Liveness/readiness |
| GET | `/v1/industries` | none | List channels |
| GET | `/v1/industries/{slug}` | none | Channel detail + theme summary |
| GET | `/v1/news` | optional key | List articles for one language (`industry`, `locale`, `topic`, `q`, `limit`, `cursor`) |
| GET | `/v1/news/bundle` | optional key | Reference-compatible single-language bundle (splash, columns, topics, desk brief) |
| GET | `/v1/news/{id}` | optional key | Article detail |
| GET | `/v1/news/splash` | optional key | Lead + favorites for the hero |
| GET | `/v1/topics` | none | Topics for a channel |
| GET | `/v1/sources` | none | Public source attribution |
| GET | `/v1/openapi.json` | none | Machine contract |
| GET | `/v1/docs` | none | Swagger UI |
| POST | `/v1/contact` | none (rate-limited) | Contact form |
| POST | `/v1/leads` | none (rate-limited) | Lead capture (consultation/brief) |
| POST | `/v1/cta-events` | none (rate-limited) | Funnel event (no PII) |
| POST | `/v1/admin/auth/login` | none | Admin login |
| POST | `/v1/admin/refresh` | Bearer | Trigger ingestion (`force` bypasses schedule) |
| GET | `/v1/admin/refresh/{run_id}` | Bearer | Run status/stats |
| CRUD | `/v1/admin/sources` | Bearer | Source management |
| POST | `/v1/admin/industries` | Bearer | Create a data-only industry channel |
| PATCH | `/v1/admin/industries/{slug}` | Bearer | Enable/disable, theme, disclaimers |
| CRUD | `/v1/admin/pins` | Bearer | Pins |
| POST | `/v1/admin/articles/{id}/hide` | Bearer | Hide article |
| CRUD | `/v1/admin/api-keys` | Bearer | Key management |
| GET | `/v1/admin/audit` | Bearer | Audit log |
| GET/PATCH | `/v1/admin/leads` | Bearer | Lead inbox + status |
| POST | `/v1/admin/leads/{id}/assign` | Bearer | Partner assignment |
| GET/DELETE | `/v1/admin/leads/{id}/export` · `/v1/admin/leads/{id}` | Bearer | DSAR export/erase |
| CRUD | `/v1/admin/partners` | Bearer | Partner registry |

- Paths are plural nouns, kebab-case; no verbs except `hide`/`refresh` actions (documented exceptions).
- Resource ids are UUIDs; slugs are `[a-z0-9-]{2,40}`.

## 5. Filtering, pagination, sorting

- Unknown query params → `400` (fail loud, no silent ignore).
- `limit` default 20, max 50; non-integer or out of range → `400`.
- `cursor` is opaque base64; invalid → `400` with `type=invalid-cursor`.
- Default sort: `score DESC, published_at DESC, id DESC` (stable tiebreak).
- `industry` is required for `/news`; if omitted → `400` (no cross-channel default) except when exactly one channel is enabled.

## 6. Caching

| Response | Headers |
|----------|---------|
| Public list/detail | `ETag`, `Cache-Control: public, max-age=60, stale-while-revalidate=300` |
| Health | `Cache-Control: no-store` |
| Admin | `Cache-Control: no-store` |
| 304 | same `ETag`, empty body |

ETag is a weak hash of the serialized body + language + cursor. Cache keys include `industry`, `locale`/`language`, and normalized query.

## 7. Auth

- Public reads: no credential.
- `X-API-Key: sn_live_<32 hex>` optional; invalid key → `401` (not silently anonymous).
- Admin: `Authorization: Bearer <JWT>`; `401` on expiry/invalid; `403` on scope.
- Admin mutations also require `X-CSRF-Token` matching the `sn_csrf` cookie.

## 8. Rate limits

| Scope | Limit | Headers |
|-------|-------|---------|
| Keyless per IP | 120 req/min | `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` |
| Per API key | 600 req/min (configurable) | same |
| Contact | 3/hour/IP | `429` + `Retry-After` |
| Admin login | 5/min/IP | `429` |

## 9. Idempotency and writes

- Admin writes accept `Idempotency-Key` (optional in v1, required for `POST /admin/refresh` retries); stored 24 h in Redis.
- `POST /v1/contact` is not idempotent; duplicate submissions within 10 min are dropped silently (200) to avoid leaking spam logic.

## 10. Dates, locales, numbers

- All timestamps are ISO-8601 UTC with `Z`.
- `locale` is a BCP 47 tag; unsupported → `400 invalid-locale`.
- `locale` selects the language bundle: items are returned only in that language; a missing bundle falls back to `en` with `meta.fallback: true` (ADR 007 §3).
- Numbers are JSON numbers; no stringified decimals.

## 11. Documentation requirements (every change)

1. Endpoint table row in this file.
2. OpenAPI annotation (FastAPI route + Pydantic models).
3. Example request/response in `docs/api/README.md`.
4. Contract test asserting the shape.
5. `docs/api/CHANGELOG.md` entry when behavior changes.

---

## Next action

None - binding as written; amend with a new dated standard when the stack, threat model, or API contract changes.
