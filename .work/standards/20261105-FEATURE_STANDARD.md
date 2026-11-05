# Feature Standard - System News

**What it is:** the lifecycle every feature-sized change follows, from proposal to archive.
**Status:** Approved for implementation (2026-11-05) · **Needs:** nothing.

**Scope:** changes that add/modify a user-visible capability, change a domain invariant, add a persisted table or public port, or touch a high-risk area. Bug fixes follow `.cursorrules` § Verification and do not need this lifecycle unless they change an invariant.

---

## 1. What counts as a feature

A feature is any unit of work that:

- Adds, modifies, or removes a user-visible capability, **or**
- Changes a domain invariant (article lifecycle, scoring, retention, isolation), **or**
- Adds a bounded-context module, public port, table, or API endpoint, **or**
- Touches a high-risk area listed in `.work/standards/20261105-threat-model.md` §2.

## 2. Lifecycle

| Stage | Required artifact | Gate |
|-------|-------------------|------|
| 1. Proposal | `.work/plans/proposals/YYYYMMDD-<slug>.md` or owner request in-session | Scope acknowledged by owner |
| 2. SPEC | `.work/features/<slug>/YYYYMMDD-SPEC.md` (§3 template) | Reviewed; threat-model areas need owner review |
| 3. Implementation | Code, tests, migrations, observability | PR references SPEC; `.cursorrules` gates pass |
| 4. Release notes | `.work/features/<slug>/CHANGELOG.md` + HANDOFF note | Deployed through environments |
| 5. Archive | SPEC frozen; later changes as `YYYYMMDD-SPEC-amendment-NN.md` | In production |

**Rule:** a SPEC never lands after its code. If code ships first, write the SPEC and mark the residual verification honestly.

## 3. SPEC template (mandatory sections)

```markdown
# <Feature Name> - Feature SPEC

**Status:** Draft | Approved | Implemented | Superseded
**Owner:** <role>
**ADRs referenced:** <list>
**Related plans:** <list>

## 1. Purpose
## 2. In scope / Out of scope
## 3. Domain language
## 4. Behavioural spec (numbered rules R1...)
## 5. Data model
## 6. APIs
## 7. Invariants
## 8. Error model
## 9. Observability
## 10. Security
## 11. i18n
## 12. Test plan
## 13. Implementation map (routes/files)
## 14. Open questions
## 15. Residual verification
```

## 4. Rules and numbering

- Every behavioural rule is numbered (`R1`, `R2`, ...) and testable: a reader can write a test from the sentence alone.
- Invariants (`I1`...) are properties that must always hold; violations are bugs, not feature requests.
- Rules are normative ("MUST", "MUST NOT") for anything a client can observe; "SHOULD" for internal guidance.
- Each rule names its acceptance test or test file when implemented.

## 5. Traceability (mandatory)

Every SPEC includes a table:

| Rule | ADR | Test | Implementation |
|------|-----|------|----------------|
| R4 | 006 | `tests/contract/test_isolation.py::test_industry_filter` | `publishing/http/news.py` |

No orphan rules; no code without a rule (except pure refactors, which cite the rule they preserve).

## 6. High-risk SPECs

The following areas require an explicit §10 Security section and an owner review before implementation:

- Channel isolation / any query that returns articles.
- Ingestion fetcher (SSRF, parsing, retention).
- AI summarization (prompt injection, output validation, cost).
- Auth, API keys, admin mutations.
- Contact-form PII handling.

## 7. Amendments

- Never edit an `Approved`/`Implemented` SPEC in place.
- Add `YYYYMMDD-SPEC-amendment-NN.md` with: what changed, why, affected rules, migration/rollback.
- The original SPEC gets a one-line pointer to the amendment.

## 8. Review checklist

- [ ] Purpose ties to a foundation goal or risk.
- [ ] In/out scope is explicit (no "TBD" without an UNKNOWNS ID).
- [ ] Rules are numbered and testable.
- [ ] Data model lists PII/data class per field.
- [ ] Errors use RFC 7807.
- [ ] Observability names metrics/logs.
- [ ] i18n handled (strings, dates, fallbacks).
- [ ] Test plan covers every rule and the security section.
- [ ] ADRs referenced; conflicts resolved in favour of the ADR.

## 9. Definition of done (feature)

1. All SPEC rules have passing tests.
2. Contract tests updated for API changes.
3. Docs updated (`docs/api`, `.work/docs/` where user-facing).
4. Observability verified in the dev stack.
5. Release note in the feature `CHANGELOG.md`.
6. No `REPLACE:` tokens, no secrets, no attribution markers.

---

## Next action

None - binding as written; amend with a new dated standard when the stack, threat model, or API contract changes.
