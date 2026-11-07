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
| 005 | Hosting and deployment (single VPS + Compose + Caddy) | Decided; edge superseded by 015 |
| 006 | Tenancy and channel model (one deployment, many channels) | Decided |
| 007 | Internationalization (EN unprefixed, `/es`, language partition) | Decided |
| 008 | Public API contract and versioning | Decided |
| 009 | Industry theming model | Decided |
| 010 | Ingestion and AI summary pipeline | Decided |
| 011 | Authentication and access control | Decided |
| 012 | CI/CD and release flow | Decided |
| 013 | Lead capture and CTA architecture | Decided |
| 015 | Channel subdomains and the host nginx edge | Decided (owner instruction 2026-11-07) |

**Ratification:** ADRs 001-012 were **ratified by the owner on 2026-11-05** (HANDOFF O1-O3 approved).

**Template:** `.ai/templates/work/decisions/YYYYMMDD-NNN-slug.md.template`
