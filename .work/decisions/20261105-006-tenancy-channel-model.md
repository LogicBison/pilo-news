# ADR 006 - Tenancy and channel model: one deployment, many channels

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** how "multiple industries" is represented in data and deployment.

## Context

The brief says: deploy these sites for any industry supported by the system, each single-themed, fed by one centralized news site. That is **one operator publishing N channels**, not N customers each with isolated data. No requirement mentions per-customer separation, per-customer billing, or customer-managed deployments.

## Decision

- **Single-tenant deployment**, **multi-channel rows**: `industries` is a first-class table; `articles`, `sources`, `topics`, `pins`, and `contact_messages` all carry `industry_id`.
- **Isolation is enforced in the read layer**, not by separate schemas: every public query MUST filter `industry_id`; contract tests assert it.
- **No Postgres RLS in v1** (single trusted application role); revisit if a per-customer deployment is ever offered.
- **Adding a channel** = insert industry row + theme JSON + sources + topics; no code change, no new deployment.
- **Public API** exposes `industry` as a required or defaulted query parameter; there is no cross-channel response.

## Consequences

- **Positive:** one deploy, one backup, one bill; new industries ship as data; simple ops.
- **Negative:** a code bug can leak across channels (mitigated by R7 + tests); noisy-neighbor effects between channels (acceptable at v1 volume); no hard per-channel resource quota.
- **Neutral:** white-label per-customer deployments would require a new ADR and likely schema-per-tenant; explicitly out of scope.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| Schema-per-tenant | No tenants; adds migration fan-out for no benefit |
| Row-level security | Real defense-in-depth, but a single app role with disciplined queries suffices at v1; can be added later |
| One deployment per industry | Multiplies ops cost and defeats "centralized" source of news |

## References

- Doc 01 § in-scope item 1
- Doc 04 §2, §4
- SPEC `.work/features/news-api/20261105-SPEC.md` R4

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
