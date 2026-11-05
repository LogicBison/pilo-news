# Architectural Decision Records (ADRs)

Project-specific ADRs. Process: `.ai/skills/plan-foundation/skill.md` P2 · pointer: `.ai/decisions/README.md`.

## Conventions

- **Filename:** `YYYYMMDD-NNN-short-slug.md` (3-digit zero-padded NNN)
- **Status:** `Proposed | Decided | Deferred | Superseded by <ADR id>`
- **Sections:** Context · Decision · Consequences · Alternatives · References
- **Never edit** a `Decided` ADR - supersede with a new file
- Foundation register in `*-04-foundation-architecture.md` §12 must agree; **ADRs win** on conflict

## Index

| ADR | Topic | Status |
|-----|-------|--------|
| 001 | Backend stack (Python 3.12 + FastAPI) | Decided |
| 002 | Primary database (PostgreSQL 16) | Decided |
| 003 | Supporting data services (Redis 7 + Postgres FTS) | Decided |
| 004 | Frontend (Next.js 15 + React 19 + Tailwind 4) | Decided |
| 005 | Hosting and deployment (single VPS + Compose + Caddy) | Decided |
| 006 | Tenancy and channel model (one deployment, many channels) | Decided |
| 007 | Internationalization (locale routes + typed catalogs) | Decided |
| 008 | Public API contract and versioning | Decided |
| 009 | Industry theming model | Decided |
| 010 | Ingestion and AI summary pipeline | Decided |
| 011 | Authentication and access control | Decided |
| 012 | CI/CD and release flow | Decided |

**Ratification:** ADRs 001-012 were prepared under the owner instruction "prepare everything" (2026-11-05). Owner ratification of the stack/hosting/budget assumptions is tracked in `.work/context/HANDOFF.md` § Open owner actions O1-O3; ratification is a review action, not a re-decision.

**Template:** `.ai/templates/work/decisions/YYYYMMDD-NNN-slug.md.template`
