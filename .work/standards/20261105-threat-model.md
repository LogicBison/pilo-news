# Threat Model - System News v1

**What it is:** assets, trust boundaries, threats, and mitigations for the v1 platform.
**Status:** Approved for implementation (2026-11-05) · **Needs:** owner review of T1-T3 before enabling legal/financial channels.

**Method:** STRIDE-style enumeration over the data-flow below; each threat maps to a control and a SPEC rule. Re-review at every architecture change and before each new industry channel.

---

## 1. Assets

| Asset | Why it matters | Class |
|-------|----------------|-------|
| Published article corpus + channel attribution | Product integrity and copyright posture | Public (integrity-critical) |
| Channel isolation (`industry_id` filtering) | Cross-channel leakage is a trust and legal event | Internal |
| Admin credentials / JWT signing key | Full editorial control | Restricted |
| API keys (hashed) | Client identity and quotas | Restricted |
| Contact messages (name, email, phone, message) | PII | Confidential |
| AI provider key + monthly budget | Cost and abuse | Restricted |
| Source feed list and fetch state | Operational integrity | Internal |
| Volume snapshots (`.tar.gz`) | Full recovery | Restricted |

## 2. High-risk areas (SPEC review required)

1. Any query returning articles (isolation).
2. Feed fetcher (SSRF, parser abuse, retention).
3. AI summarizer (prompt injection, output trust).
4. Auth / API-key / admin mutation paths.
5. Contact-form and lead PII.

## 3. Data flow

```
Publisher feeds ──https──▶ Fetcher ──▶ Postgres (articles)
                                   └─▶ Redis Stream ──▶ Worker ──▶ AI provider (titles+excerpt)
Browser ──https──▶ Caddy ──▶ Next.js web ──https──▶ /v1 API ──▶ Postgres
Browser ──https──▶ Caddy ──▶ /v1 API (direct clients) ──▶ Postgres/Redis
Admin browser ──https──▶ /v1/admin (JWT) ──▶ Postgres/Redis
```

Trust boundaries: **B1** internet→Caddy, **B2** web/API→data stores, **B3** API→publisher feeds, **B4** API/worker→AI provider, **B5** operator→admin.

## 4. Threats and controls

| ID | Threat (STRIDE) | Vector | Control | SPEC rule |
|----|-----------------|--------|---------|-----------|
| T1 | **Spoofing** admin | Stolen password / session | Argon2id, 15-min JWT, httpOnly+Secure+SameSite=Strict, `jti` denylist, CSRF double-submit | news-api R11 |
| T2 | **Tampering** published content | Unauthorized admin call / compromised key | Scoped keys, audit log, admin-only mutations, no public write endpoints | news-api R10-R12 |
| T3 | **Repudiation** | No record of who hid/pinned | `audit_events` append-only with actor + payload hash | editorial R6 |
| T4 | **XSS** via feed title/summary | Malicious RSS content rendered raw | Sanitize at ingest (strip HTML), escape at render, React auto-escape, CSP `script-src 'self'`, no `dangerouslySetInnerHTML` | industry-sites R8 |
| T5 | **SSRF** via feed URL | Admin (or compromised admin) enters internal URL; redirect to metadata IP | https-only, block private/loopback/link-local/metadata ranges, DNS re-check, max 3 redirects, 10 s timeout | ingestion R2 |
| T6 | **Prompt injection** | Feed text instructs the model to emit malicious/irrelevant output | Content is data, never instructions; fixed system prompt; no tools; output length/format validation; summaries are text only | ingestion R13 |
| T7 | **Elevation** via API key | Key leaks; scope escalation | Keys hashed with pepper, scopes checked server-side, immediate revocation, no admin scope by default | news-api R11 |
| T8 | **DoS / scraping** | High-volume reads, expensive `q` queries | Redis rate limits per IP/key, `q` length cap, cursor + `limit` caps, cache headers, 429 + Retry-After | news-api R9 |
| T9 | **CSRF** on admin | Cross-site form post | SameSite=Strict cookie + `X-CSRF-Token` header check | news-api R12 |
| T10 | **Information disclosure** | Error bodies, logs, source maps | RFC 7807 without internals, no PII in logs, source maps off in prod | observability §4 |
| T11 | **Supply chain** | Vulnerable dependency | Pinned versions, `pip-audit` + `npm audit` in CI, Dependabot-style updates reviewed | ADR 012 |
| T12 | **Data loss** | Host failure / accidental delete | Nightly off-site encrypted volume `.tar.gz` snapshots, 30-day retention, restore drill, no agent drop/truncate | doc 04 §6 |
| T13 | **Lead PII abuse / spam** | Fake or injected submissions; partner misuse; PII in logs | Explicit consent + version, honeypot, 5/hour/IP, duplicate suppression, hashed IP/UA, no PII in logs/analytics, partner scoping | ADR 013, news-api R18-R20 |
| T14 | **Consent / DSAR failure** | Lead kept after withdrawal; export/erase missing | Consent version + timestamp, 24-month retention, export/delete admin API, audit | ADR 013 R15 |

## 5. Specific controls

### 5.1 Feed fetcher (T5)

- Scheme allowlist `https` (HTTP only with explicit owner approval per source).
- Resolve DNS, reject `10/8`, `172.16/12`, `192.168/16`, `127/8`, `169.254/16`, `::1`, `fc00::/7`, `fe80::/10`.
- No user-supplied headers; fixed User-Agent with contact URL.
- Response size cap 5 MB; parse with a hardened parser; timeouts everywhere.
- On failure: mark source `degraded`, back off, never retry in a tight loop.

### 5.2 AI summarizer (T6)

- Inputs: `title` (≤ 300 chars) + `excerpt` (≤ 600 chars) only.
- Output: plain text, 2-4 sentences, ≤ 900 chars; reject URLs, HTML, and overlong output.
- No tool/function calling; no retrieval; no user-controlled system prompt.
- Model output is never executed, never used for ranking.

### 5.3 Contact form (PII)

- Server-side validation (length, email format), honeypot + rate limit (3/hour/IP).
- Store minimal fields; 90-day retention then hard delete; export/erase by email request.
- Never log the message body.

### 5.4 Secrets

- `.env*` ignored; `.env.example` contains names only.
- CI requires `GITHUB_TOKEN` only; production secrets live in the VPS env file with `600` permissions.
- Rotation: admin password (immediate), API keys (create-new → revoke-old), AI key (provider console).

## 6. Residual risks

| Risk | Status | Owner |
|------|--------|-------|
| Copyright/aggregation exposure (R1) | Open - legal review U11 | owner |
| Single-VPS SPOF (R4) | Accepted for v1 | ops |
| AI provider trust (data sent to third party) | Accepted - titles/excerpts only, no PII | owner |
| Keyless IP rate limits are bypassable | Accepted - cost tradeoff | eng |

## 7. Review log

| Date | Reviewer | Change |
|------|----------|--------|
| 2026-11-05 | plan-foundation | Initial threat model |

---

## Next action

None - binding as written; amend with a new dated standard when the stack, threat model, or API contract changes.
