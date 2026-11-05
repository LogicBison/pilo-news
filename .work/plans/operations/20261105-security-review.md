# Security review - v1

**Status:** implemented controls; cross-model review still recommended before production credentials.
**Scope:** threat model T1-T12, OWASP ASVS L2 intent.

| Control | Evidence |
|---------|----------|
| TLS + HSTS + headers | `Caddyfile`, API middleware, web middleware |
| CSP | web middleware (`unsafe-eval` dev only), API docs CSP |
| Admin auth | Argon2id/plain dev fallback, HS256 JWT 15 min, httpOnly cookie, Redis denylist |
| CSRF | double-submit `sn_csrf` + `X-CSRF-Token` on every mutation |
| API keys | `sn_live_` + 32 random bytes, SHA-256+pepper, prefix only, constant-time compare |
| Rate limits | Redis fixed window: keyless/key/contact/lead/login |
| SSRF | scheme allowlist, private/loopback/link-local/metadata block, DNS re-check, redirect cap |
| Input safety | Pydantic, HTML strip at ingest, React escaping, no body/media storage |
| PII | lead IP/UA peppered hashes, no PII in logs/analytics, DSAR export/erase, retention purge |
| Secrets | env only, `.env*` ignored except `.env.example`; secret scan in CI |
| Dependencies | pip-audit + pnpm audit recommended each PR; pins in pyproject/package |
| Error leakage | RFC 7807, no stack traces/SQL/upstream bodies |

**Residual risks:** single-VPS SPOF, feed licensing (U5), AI provider dependency,
SQL injection surface reviewed but not fuzzed, no MFA in v1.

**Manual checks before prd:** rotate `SECRET_KEY` and `ADMIN_PASSWORD`, set
`ADMIN_PASSWORD_HASH`, set `AI_API_KEY`, confirm `REDIS_PASSWORD`, disable
metrics publicly, run `pip-audit`/`pnpm audit`, verify off-site backups.
