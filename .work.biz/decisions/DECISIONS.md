# Decision Ledger — what we decided, what we expected, what happened

**Status:** Draft — <YYYY-MM-DD>
**Needs:** one row per consequential decision, appended at decision time

**Purpose:** make judgment measurable instead of remembered. The framework already measures voice (`VOICE_PROFILE` → `VOICE_RETRO`) and assumptions (`@biz-review monthly`). This is the third loop, and the one that scores *advice*: a decision that cannot be wrong cannot be scored, and an unscored decision teaches nothing.

**Why the shape is what it is.** A decision recorded as prose ("we'll focus on LinkedIn") is unfalsifiable, so nobody can ever say whether it was a good call. A decision recorded as *"12 conversations from LinkedIn by 2026-12-31"* can be scored, and a run of scored decisions tells you whether this operator is over- or under-confident. That calibration is the only thing that makes advice get better over time rather than merely more confident.

**How to use it.** Append one row when the decision is made, never afterward. Keep `Expected outcome` falsifiable: a number and a date, or an explicit observable event. Write the `Kill / review trigger` before you are emotionally invested. `@biz-review quarterly` scores every row past its `Review by` date. Never rewrite a scored row: superseding a decision appends a new row and marks the old one in `Outcome`.

**Discipline:** a `pending` row past its `Review by` date is a debt. Three of them mean the loop has stopped running.

---

## Ledger

Append only. `D-NNN` ids are never reused.

| ID | Date | Decision | Options considered | Rationale | Expected outcome | Confidence | Reversibility | Kill / review trigger | Review by | Outcome | Lesson |
|----|------|----------|--------------------|-----------|------------------|------------|---------------|-----------------------|-----------|---------|--------|
| D-001 | 2026-11-05 | Ship the lead magnet as three UI surfaces first: proof strip, process block, email-only brief capture | (a) wait for email vendor (U8) and build the full asset ladder; (b) add per-channel qualification fields now; (c) ship proof + process + capture now | R2/R3 need no backend and fix placement/trust, which gate every later number | Brief capture live on all 7 channels; ≥1% of channel-home sessions start the brief by 2027-01-05 | 70% | two-way | If after 30 days no channel clears 0.2% brief starts and CTA click stays under 1%, drop the rung and revisit R5 | 2027-01-05 | pending | — |
| D-002 | 2026-11-05 | Send all transactional and brief email through the `pilo-mail` gateway (Brevo upstream); do not integrate yet | (a) wire pilo-mail now; (b) pick a SaaS ESP; (c) defer integration and keep capturing leads | The gateway already exists and avoids a second vendor; capture does not need sending | Lead capture stays live with no send path until the gateway is wired; first brief send after integration | 75% | two-way | If a partner needs email notification before the gateway is wired, integrate then; if pilo-mail lacks a needed API by 2027-01-05, re-open the vendor choice | 2027-01-05 | pending | — |

### Column definitions

| Column | Rule |
|--------|------|
| `ID` | `D-NNN`, zero-padded, assigned in order, never reused. |
| `Date` | ISO date the decision was actually made. |
| `Decision` | One line, specific enough that a stranger could tell whether it was executed. |
| `Options considered` | The alternatives that were genuinely live. `forced` only when no alternative existed. |
| `Rationale` | Trace it to evidence (a ledger row, a call, a publish result), not to a feeling. |
| `Expected outcome` | **Falsifiable**: a number and a date, or an observable event. "Grow the business" is not a row. |
| `Confidence` | The percentage you would have bet at the time. This is what makes calibration possible; without it the hit rate has nothing to be compared against. |
| `Reversibility` | `two-way` (cheap to undo) or `one-way` (costly or impossible to undo). One-way decisions earn more analysis, more evidence, and a lower confidence bar for pausing. |
| `Kill / review trigger` | The evidence that would prove the decision wrong, and the action then. Written *before* commitment. |
| `Review by` | ISO date the row must be scored. Set it to when the expected outcome should be visible. |
| `Outcome` | `pending` · `hit` · `partial` · `miss` · `unclear` · `superseded by D-NNN`. Filled only by the audit. |
| `Lesson` | One line, only after scoring. What the *reasoning* got wrong, not what the market did. |

---

## Calibration

The actual output of this file. Scored rows only. Update during `@biz-review quarterly`.

| Decision class | Scored rows | Hit rate | Mean confidence | Gap | Reading |
|----------------|-------------|----------|-----------------|-----|---------|
| Strategy / positioning | | | | | |
| Pricing | | | | | |
| Channel | | | | | |
| Product / offer | | | | | |

**Gap** = mean confidence − hit rate. A positive gap is over-confidence on that class of decision; a negative gap means the operator is leaving upside on the table by under-committing.

**Insufficient data:** with fewer than three scored rows in a class, write `insufficient scored rows` and do not draw a conclusion. Two data points are an anecdote with a table around it.

---

## Repeating misses

Three misses in the same class are a *rule* problem, not a luck problem: amend the protocol (or the strategy) rather than resolving to be more careful. Record the amendment here.

| Miss class | Times seen | Rule changed |
|------------|-----------|--------------|

## Next action

Next action: none — rows accumulate as decisions are made and are scored by `@biz-review quarterly`
