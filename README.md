# System News

**One platform, many industry news sites, one public API.**

System News aggregates industry news from approved publisher feeds, scores and de-duplicates it, writes a short original summary for each story in its own language, and serves it two ways:

1. a **themed landing-page/news site per industry** - `/{industry}` in English, `/es/{industry}` in Spanish - and
2. a **versioned REST API** (`/v1`) that any client can consume - LogicBison first. Updates run **twice a day** by default; each channel can override that cadence in the editorial console, and any refresh can be force-triggered on demand.

Every channel carries one professional CTA that routes consented inquiries to a partner professional (ADR 013). Lead generation is a primary goal, not a footer afterthought.

**Status:** v1 implemented (2026-11-05): API, ingestion + AI summaries, public sites, editorial console, leads, tests, CI, and volume backups. Template-ready: add an industry as data.

---

## Start here

| If you are… | Read |
|-------------|------|
| New to the repo | this file → `.work/context/HANDOFF.md` → `.work/plans/NEXT.md` |
| An agent starting a session | `.cursorrules` → `.work/context/HANDOFF.md` → `.work/plans/NEXT.md` |
| Looking for the product scope | `.work/plans/foundation/20261105-01-system-news-initial-scope.md` |
| Looking for the architecture | `.work/plans/foundation/20261105-04-foundation-architecture.md` |
| Making a decision | `.work/decisions/README.md` (ADRs 001-012) |
| Writing code | `.work/standards/20261105-CONVENTIONS.md`, `20261105-DIRECTORY_MAP.md` |
| Integrating a client | `docs/api/README.md`, `docs/api/openapi.v1.json` |
| Adding an industry | `docs/adding-an-industry.md` |
| Live channels | twelve: legal, financial, behavioral-health, education, logistics, cybersecurity, stem-cell, manufacturing, energy, retail, digital-technology, health-medicine |
| Channel inventory (EN/ES URLs) | `docs/channel-inventory.md` |
| Cloning a deployment | `docs/deployment-profile.md` |
| Source quality policy | `docs/source-quality.md` |
| Switching channels (quick reference) | `docs/guides/switching-channels.md` |
| Customizing an implementation | `docs/customization.md` |
| Backups / restore | `.work/plans/operations/20261105-backup-restore.md` |
| Operating the stack | `.work/plans/operations/20261105-docker-compose-proposal.md` |

---

## Repository layout

```
apps/api/        Python 3.12 + FastAPI service and worker
apps/web/        Next.js 15 public UI + admin console
bin/             start.sh - dev stack control
docs/            Public API docs
.work/           Plans, SPECs, ADRs, standards, registries, HANDOFF
tmp/             Scratch and reference inputs (git-ignored)
DOCS_TECH_STACK.md
.cursorrules
```

---

## Quickstart (after M1 scaffold exists)

```bash
./bin/start.sh init-env --env dev   # creates .env.dev with random host ports (mode 600)
./bin/start.sh --env dev up        # postgres, redis, api, worker, web
./bin/start.sh --env dev refresh   # force a news fetch now (scheduled: every 12 h)
./bin/start.sh --env dev status    # prints the actual web/API URLs and health
./bin/offers.sh build --industry legal --dry-run   # draft a dated offer without writing
./bin/offers.sh list                               # generated offer drafts
curl -s "http://localhost:$(grep '^API_PORT=' .env.dev | cut -d= -f2)/v1/health"
curl -s "http://localhost:$(grep '^API_PORT=' .env.dev | cut -d= -f2)/v1/news?industry=legal&locale=en&limit=5"
```

Host ports are random per stack and bound to `127.0.0.1`; Postgres and Redis
have no host ports and live on an internal compose network. The stack uses two
per-project networks (`*-net`, `*-data`) so it cannot cross-talk with another
checkout on the same host.

`./bin/start.sh` with no arguments opens the visual menu. Every artifact is suffixed by the same `dev|prd` value: `docker-compose.<env>.yml`, `apps/*/Dockerfile.<env>`, `.env.<env>`. Only `.env.example` is tracked; `.env.*` lives at the repo root only.

Tests run inside the containers:

```bash
./bin/start.sh --env dev test     # ruff, mypy, pytest, ESLint, tsc, catalogs, themes, host routing
```

---

## Channel subdomains

Every channel is its own site. Dev runs the same shape on `*.localhost`, so there
is no proxy to install to see it:

```
http://localhost:43991/                  the lobby: every desk, services, legal
http://stem-cell.localhost:43991/        channel home (the port is WEB_PORT)
http://stem-cell.localhost:43991/es
http://localhost:43991/stem-cell         path URLs still work on the apex
```

```bash
./bin/start.sh dev hosts            # asserts the routing contract over HTTP
./bin/start.sh dev domains          # host table; --write renders nginx sites
```

Production terminates TLS on the host's nginx: `apps/web` and `apps/api` publish
only loopback ports, and one generated server block per channel proxies to them.
`./bin/start.sh --env prd domains --write` renders `ops/nginx/sites/`, `certs`
prints the certbot command, and `preflight` refuses to call a stack ready while a
placeholder secret or an http base URL is in `.env.prd`. Details:
`docs/domains.md`.

End-to-end and accessibility tests run against a production build; see
`apps/web/playwright.config.ts` and `e2e/`.

Until the scaffold lands, the commands above are **planned**, not verified.

---

## Lead and contact attribution

Every lead and contact message stores the channel, offer kind, locale, source page, UTM campaign keys, a peppered hash of the network address and user agent, a hashed session id, and consent metadata. Raw IP addresses are never stored. A coarse country code is stored only when `GEO_COUNTRY_HEADER` names a trusted edge header (for example `CF-IPCountry`); leave it empty if no edge overwrites the header.

## Offer issues

The free reference offers are generated from public records, not hand-written. Two adapters ship today:

- `legal`: US Federal Register rules from a legal-relevant agency set, monthly.
- `cybersecurity`: CISA KEV additions, weekly on Wednesday.

The worker checks due offers every five minutes and queues a draft. Publishing is a separate, reviewer-gated action: a draft becomes a public page at `/{locale}/{industry}/references/{date}` only after a named reviewer signs it. The public table can be filtered by jurisdiction. The issue scope is explicit: `US` for Federal Register, `global` for CISA KEV. The command is `./bin/offers.sh build --industry <slug> [--dry-run]`; publish with `./bin/offers.sh publish <id> --reviewer "Name"`. The admin API is `GET /v1/admin/offers`, `POST /v1/admin/offers/build`, and `POST /v1/admin/offers/{id}/publish`.

## Industries

| Public slug | Dataset key | Name | Layout variant | Compliance context |
|-------------|-------------|------|----------------|--------------------|
| `legal` | `legal_compliance` | Legal Services & Corporate Governance | editorial | ABA ethics, SOC2, GDPR |
| `financial` | `financial_banking` | Financial Services & Banking | professional | AML/KYC, FINRA, SEC, PCI-DSS |
| `behavioral-health` | `psychiatry_psychology` | Psychiatry & Clinical Psychology | editorial | HIPAA, 42 CFR Part 2, GDPR |
| `education` | `education_academics` | Education & Higher Academics | academic | FERPA, COPPA, GDPR |
| `logistics` | `logistics_supply_chain` | Logistics & Supply Chain | professional | DOT, IATA, C-TPAT |

Source of truth: `.work/docs/integration/industries-v1.1.0/data.json` (mirrored from `tmp/references/industries/data.json` v1.1.0). Compliance labels describe the **audience**, not data processed by System News.

---

## API in one paragraph

`GET /v1/news?industry={slug}&locale={en|es}` returns a `{data, meta}` envelope with cursor pagination and ETags; `GET /v1/news/bundle` returns a reference-compatible single-language bundle (splash, columns, topics, sources, desk brief) for LogicBison-style clients. Every response belongs to exactly one industry and one language. Every channel also publishes an RSS 2.0 feed at `/{industry}/feed.xml` (and `/es/{industry}/feed.xml`), discovered from the page head. Public reads need no key; `X-API-Key` raises rate limits. Errors are RFC 7807. Breaking changes require `/v2`. Full contract: `.work/standards/20261105-api-style-guide.md`.

---

## Documentation map

| Area | Path |
|------|------|
| Foundation docs 01-04 | `.work/plans/foundation/` |
| Master plan | `.work/plans/full/20261105-full-plan.md` |
| ADRs | `.work/decisions/` |
| Feature SPECs | `.work/features/` |
| Binding standards | `.work/standards/` |
| Registries | `.work/plans/{ASSUMPTIONS,RISK_REGISTRY,UNKNOWNS}.md` |
| Operations proposals | `.work/plans/operations/` |
| Integration mirror | `.work/docs/integration/` |
| Channel domains and the nginx edge | `docs/domains.md` |
| Dev-to-production migration | `docs/guides/migrate-dev-to-prod.md` |

---

## Readiness

| State | Value |
|-------|-------|
| Foundation-complete | yes (P0-P6 gates) |
| Plan-master-ready | yes (2026-11-05) |
| Master plan | Approved v1.1 (2026-11-05) |
| Implementation-ready | yes - implemented 2026-11-05 |

Owner actions pending: `.work/context/HANDOFF.md` § Open owner actions (O5, O7-O8).

---

## Next action

Set the owner decisions in `.work/plans/UNKNOWNS.md` (brand, feed portfolio,
pilot, analytics), then run the launch checklist in
`.work/plans/operations/20261105-launch.md`.
