# ADR 011 - Authentication and access control

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** how public clients and administrators authenticate.

## Context

- Public read endpoints must be trivially consumable (no key required) or the "any site can integrate" goal fails.
- Abuse control needs identity for higher quotas.
- Admin surface (sources, pins, hide, keys) is small but high-impact.
- No user accounts or end-user login in v1.

## Decision

- **Public reads:** unauthenticated, IP rate-limited (120 req/min). Optional `X-API-Key` identifies a client and raises the limit to 600 req/min.
- **API keys:** 32-byte random, shown once at creation, stored as `sha256(pepper || key)`; constant-time compare; `scopes` (`read`, `admin:keys`), `rate_limit`, `enabled`, `last_used_at`; revocation is immediate (cache-busted).
- **Admin:** single operator account bootstrapped from `ADMIN_EMAIL` + `ADMIN_PASSWORD_HASH` (Argon2id). Login issues a 15-minute JWT (`HS256`, `sub`, `exp`, `jti`) in an httpOnly, Secure, SameSite=Strict cookie; logout revokes `jti` in Redis.
- **CSRF:** admin mutations require a double-submit token (cookie + `X-CSRF-Token`).
- **Sessions:** stateless JWT + Redis denylist; no refresh tokens in v1 (re-login on expiry).
- **MFA:** deferred to Phase B (single editor at launch).
- **Audit:** every admin mutation writes `audit_events` (actor, action, entity, payload hash).

## Consequences

- **Positive:** zero friction for public clients; quotas manageable; small, auditable admin surface.
- **Negative:** keyless IP limits can be evaded via proxies (cost tradeoff, acceptable); single admin account weakens accountability until roles arrive.
- **Neutral:** OAuth/OIDC for editors can be added later without changing client auth.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| API key required for all reads | Kills casual integration and demoability |
| OAuth2 client credentials | Overkill for read-only public data |
| Session-only admin cookie for API | Doesn't fit the admin API; JWT is simpler for the console |
| Basic auth | No expiry, poor UX, weak audit |

## References

- SPEC `.work/features/news-api/20261105-SPEC.md` R10-R12
- `.work/standards/20261105-threat-model.md` T7-T9
- `DOCS_TECH_STACK.md` §1

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
