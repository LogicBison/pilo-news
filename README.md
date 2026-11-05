# System News

**One platform, many industry news sites, one public API.**

System News aggregates industry news from approved publisher feeds, scores and de-duplicates it, writes a short original summary for each story in its own language, and serves it two ways:

1. a **themed landing-page/news site per industry** - `/{industry}` in English, `/es/{industry}` in Spanish - and
2. a **versioned REST API** (`/v1`) that any client can consume - LogicBison first. Updates run **twice a day** by default (configurable) and can be force-triggered on demand.

Every channel carries one professional CTA that routes consented inquiries to a partner professional (ADR 013). Lead generation is a primary goal, not a footer afterthought.

**Status:** foundation complete, plan-master-ready (2026-11-05). No application code yet - implementation starts after `@plan-master greenfield` produces an Approved master plan.

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
| Integrating a client | `docs/api/README.md` (created during M1), `/v1/openapi.json` |
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
./bin/start.sh init-env --env dev   # creates .env.dev from .env.example (mode 600)
./bin/start.sh --env dev up        # postgres, redis, api, worker, web
./bin/start.sh --env dev refresh   # force a news fetch now (scheduled: every 12 h)
open http://localhost:3000        # locale-aware site
curl -s http://localhost:8080/v1/health
curl -s "http://localhost:8080/v1/news?industry=legal&locale=en&limit=5"
```

`./bin/start.sh` with no arguments opens the visual menu. Every artifact is suffixed by the same `dev|prd` value: `docker-compose.<env>.yml`, `apps/*/Dockerfile.<env>`, `.env.<env>`. Only `.env.example` is tracked; `.env.*` lives at the repo root only.

Tests run inside the containers:

```bash
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api bash -c "cd /app && pytest -q"
docker compose --env-file .env.dev -f docker-compose.dev.yml exec web bash -c "cd /app && pnpm lint && pnpm typecheck"
```

Until the scaffold lands, the commands above are **planned**, not verified.

---

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

`GET /v1/news?industry={slug}&locale={en|es}` returns a `{data, meta}` envelope with cursor pagination and ETags; `GET /v1/news/bundle` returns a reference-compatible single-language bundle (splash, columns, topics, sources, desk brief) for LogicBison-style clients. Every response belongs to exactly one industry and one language. Public reads need no key; `X-API-Key` raises rate limits. Errors are RFC 7807. Breaking changes require `/v2`. Full contract: `.work/standards/20261105-api-style-guide.md`.

---

## Documentation map

| Area | Path |
|------|------|
| Foundation docs 01-04 | `.work/plans/foundation/` |
| Master plan (to be authored) | `.work/plans/full/` |
| ADRs | `.work/decisions/` |
| Feature SPECs | `.work/features/` |
| Binding standards | `.work/standards/` |
| Registries | `.work/plans/{ASSUMPTIONS,RISK_REGISTRY,UNKNOWNS}.md` |
| Operations proposals | `.work/plans/operations/` |
| Integration mirror | `.work/docs/integration/` |

---

## Readiness

| State | Value |
|-------|-------|
| Foundation-complete | yes (P0-P6 gates) |
| Plan-master-ready | yes (2026-11-05) |
| Master plan | not yet authored |
| Implementation-ready | no - requires Approved master plan (`@plan-master status`) |

Owner actions pending: `.work/context/HANDOFF.md` § Open owner actions (O1-O5).

---

## Next action

`@plan-master greenfield` - author the master implementation plan.
