# ADR 012 - CI/CD and release flow

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1-O3.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** how code is validated and released.

## Context

Two deployables (API, web) plus infrastructure; a 1-3 person team; no CI exists yet. The reference project deploys via Docker Compose. We need repeatable checks and a rollback path without building a platform team.

## Decision

- **GitHub Actions** with three workflows: `ci.yml` (lint, type, unit, contract, integration on PR), `build.yml` (build/push images on main), `deploy.yml` (manual `workflow_dispatch` → SSH to VPS → `docker compose -f docker-compose.prd.yml pull && up -d`).
- **Branching:** trunk-based; short-lived branches; PR required for `main`; no direct pushes except hotfix with owner approval.
- **Image tags:** `sha-<short>` plus `latest`; deploy pins a SHA; rollback re-deploys the previous SHA.
- **Migrations:** run automatically by the API container on start (idempotent); deploy step waits for `/v1/health` and fails otherwise.
- **Secrets:** GitHub Environments (`staging`, `production`) with required reviewers for production.

## Consequences

- **Positive:** one pipeline definition, traceable releases, fast rollback, no bespoke deploy tooling.
- **Negative:** requires VPS SSH key management; GitHub Actions minutes are a (small) cost; no canary/blue-green in v1.
- **Neutral:** staging is optional at v1 (single VPS can host a `staging` compose project with a `STACK_SUFFIX`).

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| GitLab CI | Repo hosting is not decided; GitHub is the default for this workspace |
| Self-hosted Drone/Woodpecker | Extra infra to maintain for a small team |
| Manual deploys only | No repeatability, no audit trail |

## References

- `.work/plans/operations/20261105-docker-compose-proposal.md`
- `DOCS_TECH_STACK.md` §4
- ADR 005 (hosting)

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
