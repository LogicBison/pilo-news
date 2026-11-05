# ADR 008 - Public API contract and versioning

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** the contract every client (LogicBison first) integrates against.

## Context

- The brief makes the API mandatory and requires documentation usable by developers **and agentic coding assistants**.
- Clients read lists, detail, splash/featured, topics, sources, and search; they should not scrape HTML.
- The data changes constantly (5-10 min), so caching semantics must be part of the contract.

## Decision

- **Base:** `https://{host}/v1` with `Content-Type: application/json; charset=utf-8`.
- **Envelope:** every success response is `{ "data": ..., "meta": { "request_id", "locale", "generated_at", "next_cursor" } }`; errors are RFC 7807 Problem Details with `type`, `title`, `status`, `detail`, `instance`, `request_id`.
- **Resources:** `/industries`, `/industries/{slug}`, `/news` (filters: `industry`, `locale`, `topic`, `q`, `limit` ≤ 50, `cursor`), `/news/{id}`, `/news/splash`, `/topics`, `/sources`.
- **Pagination:** opaque cursor (base64 of `(score, published_at, id)`), never offset.
- **Caching:** `ETag` + `Cache-Control: public, max-age=60, stale-while-revalidate=300` on public reads; `304` on `If-None-Match`.
- **Auth:** public reads need no key; `X-API-Key` raises rate limits; admin endpoints require `Authorization: Bearer <JWT>`.
- **Rate limits:** 120 req/min per IP (keyless), 600 req/min per key; `429` + `Retry-After` + `RateLimit-*` headers.
- **Versioning:** additive-only within `v1` (new fields/endpoints allowed); breaking change = `/v2` with a 6-month overlap and `Sunset` headers. Deprecations announced in `docs/api/CHANGELOG.md`.
- **OpenAPI:** generated at `/v1/openapi.json`, rendered at `/v1/docs`; a committed snapshot `docs/api/openapi.v1.json` is refreshed by CI and reviewed in PRs.
- **Documentation:** `docs/api/README.md` (quickstart, auth, pagination, errors, examples in `curl` + TypeScript + Python) and `docs/api/agent-quickstart.md` (machine-oriented: endpoints, schema, invariants, common failure modes).

## Consequences

- **Positive:** stable, cacheable, testable contract; clients can build against a committed OpenAPI snapshot; agents get explicit rules.
- **Negative:** envelope adds one nesting level; cursor pagination is less familiar than offset; contract tests must gate changes.
- **Neutral:** GraphQL was considered and rejected for cache simplicity and client familiarity.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| GraphQL | Caching + rate-limit story is harder; clients are simple readers |
| Unversioned JSON | Breaks clients on any change; no deprecation path |
| Offset pagination | Unstable under frequent inserts; duplicates/skips |
| Per-client bespoke endpoints | Multiplies surface; contract drift |

## References

- Doc 02 (integration catalog)
- `.work/standards/20261105-api-style-guide.md`
- SPEC `.work/features/news-api/20261105-SPEC.md`

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
