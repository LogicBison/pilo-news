# System News - probe ledger

**Scope:** foundation · **Updated:** 2026-11-05 · **Iterations:** 3 · **Coverage:** 87% (target 85%)

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
| D5 ★ | NFRs | confirmed | high | Doc 04 §5 - owner-ratified 2026-11-05 (latency, availability, cost, freshness) | 3 |
| D6 | Integrations & ext deps | partial | med | AI provider/model decided (`deepseek-flash`, ADR 010); publisher portfolio + terms still unknown (U5) | 2 |
| D7 | Data model & sensitivity | partial | med | Doc 04 §4 + data-classification; volumes assumed | 1 |
| D8 | Constraints (budget/timeline/team) | partial | med | Budget ratified (≤ USD 40/month + AI cap); timeline and team size still unverified (A14) | 3 |
| D9 ★ | Deploy / hosting / tenancy | confirmed | high | ADR 005, ADR 006 - decided (provider pending O2) | 1 |
| D10 ★ | Risks & assumptions | confirmed | high | RISK_REGISTRY R1-R16, ASSUMPTIONS A1-A14 | 1 |

Status: `confirmed` | `partial` | `unknown` · Conf: `high` | `med` | `low` · ★ = gate-blocking.

**Computation:** weights D1=2, D2=1, D3=2, D4=1, D5=2, D6=1, D7=1, D8=1, D9=2, D10=2 → Σ weight = 15.
Σ weight×confidence = 2 + 0.5 + 2 + 1 + 2 + 0.5 + 0.5 + 0.5 + 2 + 2 = 13.0 → **86.7%**.

> Figure after the owner approvals of 2026-11-05 (NFRs, budget, ADRs). Remaining gap is D2/D6/D7/D8 (personas, publisher portfolio, volumes, team size).

## Target status

| Check | Result |
|-------|--------|
| Coverage ≥ 85% | **yes** (87%) |
| No ★ below partial | **yes** (all ★ confirmed) |
| Consequence | Target met; the remaining partial dimensions stay listed as residual risk and owner questions in HANDOFF O5. |

## Open probes (carried to next iteration)

- **D6:** first publisher per channel + terms → blocks source seeding and M1 acceptance.
- **D8:** confirm timeline and team size (budget now approved) → blocks milestone sizing in plan-master.
- **D2:** confirm whether the primary reader is a licensed professional or a general audience → affects disclaimers/copy.
- **D7:** confirm article volumes per channel (10k vs 100k/month) → blocks index/sizing review.

## Deferred (→ UNKNOWNS.md)

- U4: AI provider · owner=owner · blocks=ADR 010 execution.
- U5: publisher portfolio · owner=owner · blocks=source seeding/legal.
- U9: analytics posture · owner=owner · blocks=consent UI.
- U10: traffic expectation · owner=owner · blocks=sizing.

## Iteration log

| Iter | Date | Coverage | Dimensions touched | Notes |
|------|------|----------|--------------------|-------|
| 1 | 2026-11-05 | 80% | D1-D10 | Initial assessment from brief + repo evidence; product + tech questions remained unanswered by owner, so D2/D5/D6/D8 stay partial |
| 2 | 2026-11-05 | 80% | D5, D6, D8 | Reference-alignment pass: refresh cadence (12 h + manual), language partition, and DeepSeek `deepseek-flash` decided; budget/publisher/targets still owner-open |
| 3 | 2026-11-05 | 87% | D5, D8 | Owner approved ADRs 001-012, budget, and NFR targets; D5 confirmed, D8 budget part confirmed |

---

## Next action

None - residual owner-validation gaps are tracked in `.work/context/HANDOFF.md` O5.
