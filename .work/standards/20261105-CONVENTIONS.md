# Code Conventions - System News

**What it is:** binding engineering conventions for all application code in this repo.
**Status:** Approved for implementation (2026-11-05) · **Needs:** nothing.

Pairs with: `DOCS_TECH_STACK.md`, foundation doc 04, ADRs `.work/decisions/`, `20261105-DIRECTORY_MAP.md`.

---

## 1. Language and tooling baselines

| Surface | Tooling | Notes |
|---------|---------|-------|
| API (`apps/api`) | Python 3.12 · `ruff check` + `ruff format --check` · `mypy src` · `pytest` | All mandatory on every PR |
| Web (`apps/web`) | TypeScript 5.8 strict · ESLint (next config) · `tsc --noEmit` · Playwright | `strict: true`, no implicit `any` |
| SQL | Idempotent numbered scripts under `apps/api/migrations/` | No inline DDL in application code |
| Shell | `bash` with `set -euo pipefail` · `shellcheck` | Scripts under `bin/` and `apps/api/scripts/` |

`REPLACE:` tokens are forbidden in committed files. Generated files carry a one-line header saying so.

## 2. Type discipline

- API: public functions and all module boundaries are annotated; `mypy` runs over `src/`; Pydantic models for every request/response; no `Any` in domain signatures without a comment.
- Web: `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`; API responses typed by hand-written DTOs mirrored from `docs/api/openapi.v1.json` (no codegen in v1).
- DTOs at boundaries; ORM models never cross the HTTP layer; domain models never import FastAPI/Pydantic.

## 3. Naming

- Python: `snake_case` functions/modules, `PascalCase` classes, `UPPER_SNAKE` constants.
- TypeScript: `camelCase` values, `PascalCase` components/types, file names `kebab-case.ts(x)` except components (`PascalCase.tsx`).
- DB: `snake_case`, plural tables; FK `<entity>_id`; indexes `ix_<table>_<cols>`; constraints `ck_` / `uq_` / `fk_`.
- HTTP routes: plural nouns, kebab-case, no verbs (`/v1/news`, `/v1/industries/{slug}`).
- Locales: BCP 47 (`en`, `es`, later `pt-BR`).
- Dated docs: `YYYYMMDD-` prefix (except `NEXT.md`, `HANDOFF.md`).

## 4. Money, quantities, regulated fields

- No money fields in v1. If added: decimal/NUMERIC end-to-end, never float, `USD` explicit.
- Percentages/trust stored as `NUMERIC(3,2)` or `NUMERIC(5,2)` with a check constraint.
- Any future regulated identifier is documented in the SPEC and data-classification before implementation.

## 5. Time

- Persist UTC (`TIMESTAMPTZ`); ISO-8601 with offset at the API boundary.
- Render in the channel's timezone (default `America/El_Salvador`) via `Intl`.
- One clock helper (`news_api.platform.clock`) for testability; no direct `datetime.now()` in domain code.

## 6. Errors

- Domain errors are a small typed hierarchy (`NotFound`, `ValidationError`, `Conflict`, `RateLimited`, `UpstreamError`).
- HTTP maps to RFC 7807; never leak stack traces or upstream bodies.
- All errors carry `request_id`; logs include it.

## 7. Logging and secrets

- Structured JSON logs via `structlog`; one line per request and per pipeline stage.
- Never log emails, phone numbers, raw message bodies, tokens, or API keys; log IDs/status only.
- Secrets only from environment; `.env*` is git-ignored except `.env.example` (created on owner approval).

## 8. Module boundaries

- Layout is `context/{domain,application,infrastructure,http,ports}` (see DIRECTORY_MAP).
- A context imports `news_api.platform` and other contexts' `ports` only - never their `infrastructure`/`http`/`domain` internals.
- Cross-context communication via ports, DTOs, or events; no shared ORM models across contexts.
- `platform` imports no context.

## 9. Testing

- Unit tests colocated by domain module; integration tests use a real Postgres (testcontainers or compose).
- Every public endpoint has a contract test asserting the envelope, error shape, and auth behavior.
- Bug fixes add a failing-then-passing regression test.
- Test names describe behaviour (`test_news_list_excludes_hidden_articles`), not implementation.

## 10. Frontend conventions

- Server components by default; `"use client"` only for interactivity (locale switch, form, search box).
- No `any`; no `dangerouslySetInnerHTML` without a sanitizer and a comment.
- Tailwind utility classes; theme values via CSS custom properties, never hardcoded hex in components.
- All user-visible strings come from `messages/{locale}.json`; no literals in JSX.
- Images use `next/image` with explicit dimensions and `alt`.

## 11. Definition of done (code change)

1. Lint, format, type, unit + contract tests pass locally in the compose service.
2. Migration idempotency verified (run twice) if schema changed.
3. Observability added for new paths (metric/log/trace per observability spec).
4. SPEC/ADR updated or an amendment added when behaviour changes.
5. `touch-scope-verify` and `blast-radius-check` pass.

---

## Next action

None - binding as written; amend with a new dated standard when the stack, threat model, or API contract changes.
