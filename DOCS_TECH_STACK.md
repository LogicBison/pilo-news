# Technology stack - System News

**What it is:** the pinned stack for v1; rationale lives in `.work/decisions/` (ADR cross-reference in §6).
**Status:** Approved for implementation (2026-11-05) - owner ratification of O1-O3 tracked in `.work/context/HANDOFF.md`.
**Linked from:** `.cursorrules` as the tech-stack doc.

---

## 1. Summary

| Layer | Choice | Version (pin) | Notes |
|-------|--------|---------------|-------|
| Language (primary) | Python | 3.12.x | API + worker |
| HTTP API | FastAPI | 0.115.6 | + Uvicorn 0.34.0, Pydantic 2.10.5 |
| DB access | SQLAlchemy async + asyncpg | 2.0.x · 0.30.x | No Alembic; numbered SQL migrations |
| Database | PostgreSQL | 16-alpine | Source of truth |
| Cache / queue / locks | Redis | 7-alpine | Cache, rate limits, Redis Streams, single-flight locks |
| Search | PostgreSQL full-text | 16 built-in | `tsvector` + GIN behind `SearchPort` |
| Frontend | Next.js + React + Tailwind | 15.1.8 · 19.1.0 · 4.1.6 | App Router, RSC, ISR |
| Language (web) | TypeScript | 5.8.x | `strict` |
| i18n | Typed JSON catalogs + locale routes | in-repo | `en`, `es`; additive |
| Auth | API keys (read) + JWT/Argon2id (admin) | in-repo | ADR 011 |
| Hosting | Single VPS + Docker Compose + Caddy | compose v2 · caddy 2 | ADR 005 |
| CI/CD | GitHub Actions | - | ADR 012 |
| Email | SMTP / transactional API | provider TBD | Contact notifications (U8) |
| Refresh cadence | `REFRESH_INTERVAL_MINUTES` | default 720 | Twice daily; manual force via admin API/CLI (ADR 010) |
| AI summaries | DeepSeek `deepseek-flash` (V4.1 Flash) | OpenAI-compatible | base `https://api.deepseek.com`; `AI_MODEL` overrides (ADR 010) |

**Deferred (not installed):** object storage/CDN, dedicated search engine, managed cloud, Kubernetes, GraphQL.

---

## 2. Repository layout

| Path | Purpose |
|------|---------|
| `apps/api/` | FastAPI service + worker (`news_api`) |
| `apps/api/migrations/` | Idempotent numbered SQL |
| `apps/api/src/news_api/platform/` | Shared platform package |
| `apps/web/` | Next.js public UI + admin console |
| `bin/start.sh` | Visual stack menu (`up`, `down`, `logs`, `test`, `migrate`, `refresh`, `backup`, `restore`, `destroy`) |
| `docs/api/` | Public API docs + committed OpenAPI snapshot |
| `docker-compose.dev.yml` / `docker-compose.prd.yml` | Dev / production stacks |
| `.env.example` → `.env.dev` / `.env.prd` | One root template; per-env files generated, ignored |
| `apps/*/Dockerfile.dev` / `Dockerfile.prd` | Image per environment suffix |
| `.work/` | Plans, SPECs, ADRs, standards, HANDOFF |
| `tmp/` | Scratch/reference inputs (git-ignored) |

See `.work/standards/20261105-DIRECTORY_MAP.md` for the binding map.

---

## 3. Local development

| Item | Value |
|------|-------|
| Dev stack script | `./bin/start.sh` (menu) · `./bin/start.sh --env prd <cmd>` |
| Compose file | `docker-compose.<env>.yml` (env = dev \| prd) |
| Test command | `pytest -q` (in `api`, from `/app`) |
| Lint | `ruff check . && ruff format --check .` (in `api`) |
| Type check | `mypy src` (in `api`); `tsc --noEmit` (in `web`) |
| Frontend lint | `pnpm lint` (in `web`) |
| Frontend tests | `pnpm test` (Playwright, in `web`) |
| Scope check | `bash /mnt/work/Projects/pilo.ai.logicbison/scripts/touch-scope-verify.sh` |
| Blast radius | `bash /mnt/work/Projects/pilo.ai.logicbison/scripts/blast-radius-check.sh` |
| Default dev ports | web 3000 · api 8080 · postgres 5433 · redis 6380 · prometheus 9090 · grafana 3001 |

**Rule:** never run app tests/lint/installs on the host while Compose is used - use `./bin/start.sh --env <env> <command>` or `docker compose --env-file .env.<env> -f docker-compose.<env>.yml exec <service> ...` (see `.cursorrules` § Docker / Dev Environment).

---

## 4. CI/CD

| Item | Status |
|------|--------|
| Platform | GitHub Actions |
| Workflows | `ci.yml` (lint/type/unit/contract/integration), `build.yml` (images on `main`), `deploy.yml` (manual, SSH to VPS) |
| Deploy targets | staging (optional, `STACK_SUFFIX=stg`) / production (`STACK_SUFFIX=prd`) |
| Image tags | `sha-<short>` + `latest`; rollback = previous SHA |
| Migrations | run by the API container on start; health-gated |
| Secrets | GitHub Environments with required reviewers for production |

---

## 5. Open decisions (tracked in `.work/plans/UNKNOWNS.md`)

| ID | Topic | Owner | Where |
|----|-------|-------|-------|
| U3 | VPS provider + budget | owner | ADR 005 ratification (HANDOFF O2) |
| U4 | AI monthly budget (`AI_MONTHLY_BUDGET_USD`) | owner | cost cap; provider/model decided (`deepseek-flash`) |
| U5 | Publisher feed portfolio + terms | owner | source seeding, R1 |
| U8 | Email delivery vendor | owner | contact flow |
| U10 | Traffic expectation | owner | sizing/scaling trigger |
| U13-U15 | Search engine / object storage / mobile | eng | Phase B |

No `TODO` in this file is untracked: every unknown maps to an `UNKNOWNS` ID.

---

## 6. ADR cross-reference

| Decision | ADR |
|----------|-----|
| Backend stack | `001-backend-stack.md` |
| Database | `002-database-postgresql.md` |
| Cache/queue/search | `003-data-services.md` |
| Frontend | `004-frontend-nextjs.md` |
| Hosting | `005-hosting-deployment.md` |
| Tenancy/channels | `006-tenancy-channel-model.md` |
| i18n | `007-internationalization.md` |
| API contract | `008-public-api-contract.md` |
| Theming | `009-industry-theming.md` |
| Ingestion/AI | `010-ingestion-ai-pipeline.md` |
| Auth | `011-auth-access-control.md` |
| CI/CD | `012-cicd-release-flow.md` |

This file holds **pins** only; rationale belongs in the ADRs.

---

## Next action

None - pins are current; update only when an ADR changes.
