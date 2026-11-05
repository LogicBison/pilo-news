# System News - probe ledger

**Scope:** foundation · **Updated:** 2026-11-05 · **Iterations:** 1 · **Coverage:** 80% (target 85%)

> Persisted state for `@plan-foundation probe` / `@plan-master probe`. Engine: `.ai/skills/probe-protocol.md`.
> Set **confirmed/high** only with a cited source or a same-session owner answer; an inference is **partial/med** at best.
> Coverage = ( Σ weight × confidence ) / Σ weight · confidence high=1.0 med=0.5 low=0.0 · weight gate-blocking(★)=2 else=1.

## Coverage

| Dim | Topic | Status | Conf | Evidence / source | Iter |
|-----|-------|--------|------|-------------------|------|
| D1 ★ | Product intent & success | confirmed | high | Doc 01 §Founder intent (verbatim brief) + §Success criteria S1-S10 | 1 |
| D2 | Audience / personas | partial | med | `.work/plans/20261105-personas-v1.md` - inferred from brief, not owner-validated (A14) | 1 |
| D3 ★ | Scope in / out | confirmed | high | Doc 01 §Product scope (explicit in/out lists) | 1 |
| D4 | Functional capabilities | confirmed | high | Doc 01 §Capabilities C1-C8 + four SPECs | 1 |
| D5 ★ | NFRs | partial | med | Doc 04 §5 - quantified but agent-assumed; owner ratification pending (O3) | 1 |
| D6 | Integrations & ext deps | partial | med | Doc 02 §2 - patterns identified; publisher portfolio + AI vendor unknown (U4, U5) | 1 |
| D7 | Data model & sensitivity | partial | med | Doc 04 §4 + data-classification; volumes assumed | 1 |
| D8 | Constraints (budget/timeline/team) | partial | med | ASSUMPTIONS A13/A14 - unverified | 1 |
| D9 ★ | Deploy / hosting / tenancy | confirmed | high | ADR 005, ADR 006 - decided (provider pending O2) | 1 |
| D10 ★ | Risks & assumptions | confirmed | high | RISK_REGISTRY R1-R16, ASSUMPTIONS A1-A14 | 1 |

Status: `confirmed` | `partial` | `unknown` · Conf: `high` | `med` | `low` · ★ = gate-blocking.

**Computation:** weights D1=2, D2=1, D3=2, D4=1, D5=2, D6=1, D7=1, D8=1, D9=2, D10=2 → Σ weight = 15.
Σ weight×confidence = 2 + 0.5 + 2 + 1 + 1 + 0.5 + 0.5 + 0.5 + 2 + 2 = 12.0 → **80.0%**.

> Correction: with the table above the honest figure is **80%**, below the 85% target. The gap is concentrated in D2/D5/D6/D8 (owner validation). This is recorded rather than rounded up (evidence-first).

## Target status

| Check | Result |
|-------|--------|
| Coverage ≥ 85% | **no** (80%) |
| No ★ below partial | **yes** (all ★ confirmed) |
| Consequence | Certification may proceed (S4 does not make the probe target a hard gate), but the four partial dimensions must be flagged as residual risk and the owner questions carried into HANDOFF. |

## Open probes (carried to next iteration)

- **D5:** confirm or adjust the p95/availability/cost targets (owner) → blocks NFR ratification.
- **D6:** name the AI provider/model and the first publisher per channel → blocks M1 acceptance.
- **D8:** confirm budget, timeline, and team size → blocks milestone sizing in plan-master.
- **D2:** confirm whether the primary reader is a licensed professional or a general audience → affects disclaimers/copy.

## Deferred (→ UNKNOWNS.md)

- U4: AI provider · owner=owner · blocks=ADR 010 execution.
- U5: publisher portfolio · owner=owner · blocks=source seeding/legal.
- U9: analytics posture · owner=owner · blocks=consent UI.
- U10: traffic expectation · owner=owner · blocks=sizing.

## Iteration log

| Iter | Date | Coverage | Dimensions touched | Notes |
|------|------|----------|--------------------|-------|
| 1 | 2026-11-05 | 80% | D1-D10 | Initial assessment from brief + repo evidence; product + tech questions remained unanswered by owner, so D2/D5/D6/D8 stay partial |

---

## Next action

None - residual owner-validation gaps are tracked in `.work/context/HANDOFF.md` O5.
