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
| D-003 | 2026-11-06 | Publish the KEV digest weekly on Wednesday and drop "daily" from the offer brief | (a) daily; (b) weekly Wednesday; (c) biweekly | Measured: the catalog gains 6.6 entries/week and additions cluster Tue/Wed; a daily send would be empty most days | Three Wednesday issues published by 2026-12-31, no gap over 7 days | 80% | two-way | If more than 30% of weeks yield 0-1 rows, move to biweekly or kill the asset | 2027-01-05 | pending | — |
| D-004 | 2026-11-06 | Ship a public dated issue page plus the existing waitlist first; gate email later | (a) email-gated from day one (blocked on D-002); (b) public page + waitlist; (c) no page until delivery exists | Delivery is deferred and the earlier brief promise was already ahead of the system; a real page keeps the promise honest while the list builds | Issue 1 is publicly reachable at both locales before any page promises a send date | 75% | two-way | If joins stay flat for 4 weeks with the page live, re-test the gate shape or drop the asset | 2027-01-05 | pending | — |
| D-005 | 2026-11-06 | Every digest issue carries a named human reviewer; the generator refuses to publish without one | (a) AI-only, no signer; (b) named reviewer per issue, enforced in the CLI | A wrong row on a security list is a false statement to a professional reader | Issue 1 shows a reviewer name; a publish attempt without `--reviewer` fails | 70% | two-way | If no reviewer is available for two consecutive issues, stop publishing rather than ship unreviewed | 2027-01-05 | pending | — |
| D-006 | 2026-11-06 | Build the digest for cybersecurity only until issue 3 ships; no second channel's asset before then | (a) multi-channel assets at once; (b) cybersecurity first, others after issue 3 | Review capacity and one proven pipeline beat nine half-built assets | No second channel asset card exists before the third cybersecurity issue | 85% | two-way | If issue 1-3 land on schedule and review capacity holds, open the next channel earlier | 2027-01-05 | pending | — |
| D-007 | 2026-11-06 | Use a channel-keyed static asset registry for the 14-day card test instead of moving asset copy into channel config (JSONB) now | (a) channel config JSONB + migration now; (b) static registry keyed by channel, copy in `messages/{locale}.json`; (c) leave the hardcoded legal slug | R16 asks for channel config, but the test needs two hours, not a migration; the registry removes the hardcoded JSX and keeps copy out of components (CONVENTIONS §10) | Card renders on cybersecurity and legal only, from the registry; no JSX literal names an asset slug | 70% | two-way | If a channel needs a different asset, or the test passes and the digest page enters the build, move asset definitions to channel config in that iteration | 2026-11-20 | superseded by D-009 | — |
| D-008 | 2026-11-06 | Where a channel offers a gated asset, the asset card is its single secondary rung and the brief signup does not render | (a) asset replaces the brief; (b) keep both, demote the asset; (c) keep both and fix attribution only | Two list-capture asks on one page split the same reader and made the 14-day test ambiguous; the asset is the more specific promise | Legal and cybersecurity render no `#brief-signup`; the other eight channels keep it; e2e asserts both | 75% | two-way | If legal's brief starts fall by more than half over four weeks with no matching asset joins, restore the brief placement | 2027-01-05 | pending | — |
| D-009 | 2026-11-06 | Move the asset offer into channel config (`cta.asset`) and seed it; supersedes D-007 | (a) keep the static channel-keyed registry; (b) channel config `cta.asset` + idempotent seed | R16 asks for channel config; `industries.cta` is already JSONB and already served, so the literal fix costs one migration and two profile lines | No asset slug appears in JSX; `/v1/news/bundle` carries `cta.asset` for exactly legal and cybersecurity; migration 011 re-runs with `applied: 0` | 80% | two-way | If a second asset per channel is needed, extend `cta.asset` to a list in the same iteration | 2027-01-05 | pending | — |
| D-010 | 2026-11-06 | Test demand for a digital-technology channel with three topic hubs on cybersecurity before building the channel | (a) topic test first; (b) build the channel now; (c) skip the channel | The build is 1.5-2 days and the demand is unproven; topic hubs already ship, so the test costs about an hour | Channel go/no-go decided on 2026-11-27 from the topic read-out; no channel profile, skin, or source written before then | 70% | two-way | If the topic pages exceed the bar earlier, build sooner; if the funnel cannot attribute topic placement, fix the placement before reading results | 2026-11-27 | superseded by D-014 | — |
| D-014 | 2026-11-06 | Build the digital-technology channel now; the 21-day topic window becomes a keep/kill check instead of a build gate (supersedes D-010) | (a) wait for the topic read-out; (b) build now, keep the window as a kill check | The operator states the channel is an expected result; the window still costs nothing and now tests retention rather than existence | Channel live by 2026-11-13; keep/kill decided 2026-11-27 from topic placement plus channel inquiries | 65% | two-way | If the channel holds under 1% of sessions and no inquiry by 2026-11-27, set `enabled: false` and keep the topics | 2026-11-27 | pending | — |

| D-015 | 2026-11-06 | Use one jurisdiction-tagged offer dataset with a visible reader filter; do not generate one calendar per country. IP may set a default only, with an override. | (a) one calendar per country; (b) one dataset + filter; (c) AI-search-only calendar | Adapter and reviewer cost is per source, not per country; a filter scales without a false completeness claim; AI search is not a stable source | Legal filter used by at least 25% of readers who open the issue by 2027-01-05; no separate country generator exists | 75% | two-way | If filter use stays under 10% after two issues, or readers report wrong-country defaults, simplify to a US-only page and drop the IP default | 2027-01-05 | pending | — |

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
