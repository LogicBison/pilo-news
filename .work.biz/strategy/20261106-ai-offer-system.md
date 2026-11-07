# AI-generatable free offers - analysis and recommendations

**What it is:** what each channel should give away, why the current offer is too thin, what AI can honestly generate, and the rollout that turns the offer into subscribers and inquiries.
**Status:** Recommendation (2026-11-06).
**Needs:** owner approval of the offer architecture and the named reviewers; email delivery remains U8.
**Companion artifacts:** `strategy/offer-inventory.md` (generated), `strategy/offer-guides/` (one guide per channel), `strategy/offers/catalog.json` (machine-readable plan).

---

## 1. Verdict

The system does not have a free-offer problem. It has a **differentiation and delivery** problem.

Every channel already captures something: nine take a weekly-brief signup, two take a gated-asset waitlist. None publishes an issue, and none sends email. The weekly brief is a digest of the same feed the channel already shows, so it asks for an email without giving the reader anything they cannot get by loading the page. The two asset cards are better, but neither has a published issue behind it.

Recommendation: **make the free offer a dated decision document, not a newsletter.** Two formats, one per channel:

- **Reference** (asset): a dated table of deadlines, rule changes, recalls, or queue milestones, scoped to a stated jurisdiction. AI extracts rows from primary sources. A named reviewer signs the issue. This is the stronger offer where public data exists.
- **Brief**: a five-item weekly decision note with three sections: what changed, what date matters, what to ask. AI drafts it from the channel's feeds plus one primary-source check. This is the honest offer where a reference cannot be built or reviewed yet.

The asset is the product. The email is its delivery. This resolves the one-secondary-offer rule: the reference is the secondary rung, and the weekly send is how subscribers receive it, not a second competing offer.

Confidence: high on the diagnosis, medium on the per-channel split. Review at 2027-01-05.

---

## 2. What exists today

Measured on 2026-11-06 against the live API (`/v1/industries/{slug}`) and the channel config.

| Channel | Primary CTA | Secondary offer today | Capture | Published issue | Delivery |
|---|---|---|---|---|---|
| legal | consultation | asset `legal-regulatory-calendar` | waitlist | none | none |
| financial | consultation | weekly brief | signup | none | none |
| behavioral-health | consultation | weekly brief | signup | none | none |
| education | brief (kind `brief`) | weekly brief | signup | none | none |
| logistics | consultation | weekly brief | signup | none | none |
| cybersecurity | consultation | asset `cybersecurity-kev-digest` | waitlist | none | none |
| stem-cell | consultation | weekly brief | signup | none | none |
| manufacturing | consultation | weekly brief | signup | none | none |
| energy | consultation | weekly brief | signup | none | none |
| retail | consultation | weekly brief | signup | none | none |
| digital-technology | consultation | weekly brief | signup | none | none |

Evidence:
- The offer switches are in `industries.offers`; the live inventory generator reads them from the API (`strategy/offer-inventory.md`).
- The two assets are registry entries with `waitlist: true` (`apps/web/src/lib/assets.ts`).
- The briefs archive renders an honest empty state (`apps/web/src/app/[locale]/[industry]/briefs/page.tsx`).
- Email delivery is deferred; `pilo-mail`/Brevo is chosen but not wired (D-002; `.work.biz/plans/UNKNOWNS.md`).
- The channel brief copy promises a Monday send that no code performs (feasibility V1).

So the current ladder is **capture without fulfilment**. That is the gap to close before adding more capture surfaces.

---

## 3. The idea, stated plainly

A professional does not subscribe to "news". They subscribe to **a recurring decision they do not want to miss**. The free offer has to pass three tests:

1. **Different from the site.** If the deliverable is a list of the same articles, the reader can skip it. It must add filtering, dates, a jurisdiction, or an action.
2. **Saves a decision, not just time.** "Here are five stories" is time-saving. "This rule takes effect on 12 March and changes your intake form" is decision-saving.
3. **AI can draft it from cited sources.** Every row must trace to a URL a reviewer can open. If the data is proprietary or the claim is advice, AI cannot carry it.

The offer ladder becomes:

```
news page (attention)
  -> free dated reference or brief (the reason to subscribe)
  -> email issue (the recurring habit)
  -> ask one question or consultation (the lead)
```

The reference is not a "lead magnet" in the pejorative sense. It is the smallest useful professional document the desk can produce every month with a citable source and a human signature.

---

## 4. Gaps

| # | Gap | Why it matters | Evidence |
|---|-----|----------------|----------|
| G1 | No issue is published or delivered | The capture promises something that does not arrive; a dead promise burns trust | briefs archive empty; D-002 deferred |
| G2 | The weekly brief is generic | It repeats the channel feed; no reason to give an email | brief copy; bundle items |
| G3 | Only 2 of 11 channels have a specific asset | Nine channels compete on the weakest offer | live API |
| G4 | No named reviewer or sign-off | A wrong deadline is a false statement, not a typo | D-005 open |
| G5 | No per-offer measurement | Funnel events stop at CTA submit; no issue open/click/join by offer | `/v1/admin/funnel` |
| G6 | No primary-source adapters | The system reads RSS only; regulator JSON/XML is a build | `sources.feed_url`; feasibility §6 |
| G7 | No rights/attribution policy for generated rows | Republishing paywalled standards or licensed rates is a legal risk | feasibility §2-§4 |
| G8 | No ES generation policy | Translation of a deadline/action is a liability if unreviewed | EN/ES parity requirement |
| G9 | No offer inventory or admin view of the deliverable | Admin toggles offers but cannot see what the subscriber gets | admin Channels tab |
| G10 | No kill rule per offer | An asset can drift for months without demand | no per-offer metric |
| G11 | Education's primary CTA is `kind: "brief"` | the main form asks for a newsletter, not an inquiry, so the channel has no consultation path in the form kind | `apps/api/config/deployments/education.json:44` |

---

## 5. The architecture

### 5.1 Two formats, one secondary rung

| Format | Reader promise | Cadence | AI role | Human role | Best for |
|--------|----------------|---------|---------|------------|----------|
| Reference (asset) | "the dated table you keep" | monthly or weekly | extract, normalize, draft rows, translate | verify every date, source, and jurisdiction; sign | regulated, deadline-driven channels |
| Brief | "the five-minute decision note" | weekly | select, summarize, draft the question | verify claims and tone; sign | fast-moving or fragmented channels |

Both formats use the same discipline:
- one issue date and one scope line in the title;
- every row has a source URL and a "what changed" line;
- a named reviewer signs the issue;
- EN is reviewed before ES is translated;
- no autopublish;
- a dated correction note, never a silent edit.

### 5.1.1 Jurisdiction policy

**v1 is US-first.** A scope is a property of the source adapter, not a marketing claim. The Federal Register is a US source, so the legal issue is `US`. The SEC and Fed are US sources, so the financial issue is `US`. CISA KEV is a US catalog about vulnerabilities that affect vendors worldwide, so the cybersecurity issue is `global`, and the title says `CISA KEV`.

EU is a later adapter with its own scope. A `US + EU` issue is allowed only after both adapters run and the combined table is reviewed. No v1 title says `US + EU` for a regulatory reference. The three brief channels keep a lighter scope label: behavioral-health and education are `US`; digital-technology is `US + EU` because it summarizes public policy news, not a regulated calendar.

This keeps the first build honest and small. The alternative, shipping `US + EU` on day one, would require EUR-Lex, national transposition portals, and a second reviewer before the first issue.

### 5.2 Per-channel recommendation

The catalog holds the machine-readable version (`strategy/offers/catalog.json`). This is the plan a human reads.

| Channel | Free offer | Type | Status | Cadence | Scope | Why this one |
|---------|------------|------|--------|---------|-------|--------------|
| legal | US Regulatory Calendar | reference | waitlist | monthly, first Tuesday | US | deadline-driven, public source, already configured |
| financial | US Rule-Change Tracker | reference | planned | monthly, second Wednesday | US | rules change operations; SEC and Fed publish |
| behavioral-health | Practice & Payer Brief | brief | live capture | weekly, Thursday | US | a clinical reference is liability-heavy; payer and safety notices are safe to summarize |
| education | Enrollment Deadline Brief | brief | live capture | weekly in term | US | registrar data is fragmented; dates are usable, predictions are not |
| logistics | US Port & Customs Notice Digest | reference | planned | weekly, Monday | US | CBP and port notices exist; rate indices are licensed and banned |
| cybersecurity | CISA KEV Digest | reference | waitlist | weekly, Wednesday | global | strongest public dataset; already configured |
| stem-cell | US Trial & Regulatory Digest | reference | planned | monthly, third Tuesday | US | ClinicalTrials.gov and FDA publish status changes; no clinical claims |
| manufacturing | US Recall & Regulator Notice Tracker | reference | planned | monthly, second Thursday | US | CPSC and FDA recalls are citable; standards are paywalled |
| energy | US Grid Queue & Docket Digest | reference | planned | monthly, first Thursday | US | queues and dockets are public; EU is a later adapter |
| retail | US Consumer Policy & Recall Calendar | reference | planned | monthly, fourth Tuesday | US | FTC and CPSC policy and recalls are public; demand data is proprietary |
| digital-technology | AI Infrastructure & Policy Brief | brief | live capture | weekly, Tuesday | US + EU | fast-moving, fragmented; a dated brief beats a false tracker |

Why three channels stay on the brief: behavioral-health and education carry review or data-fragmentation risk that a monthly reference would expose too early; digital-technology changes faster than a monthly table can stay true. They can graduate to a reference after the first six weeks of briefs produce a stable source list and a named reviewer.

**Technical status (2026-11-06):** the legal and cybersecurity generators are implemented (US Federal Register and CISA KEV) and have produced 12-row drafts. The public cards still show waitlists because no issue has been signed and published yet; the reviewer-gated publish and public pages are built, email is not. The other six reference offers are plans with guides, not running adapters. See `.work/features/offer-generation/20261106-SPEC.md`.

### 5.3 What each offer is not

- It is not a feed dump. Five rows beat twenty.
- It is not advice. It reports what a regulator, registry, or standards body published.
- It is not global unless the title says so.
- It is not a rate index, a demand forecast, or a clinical recommendation.
- It is not gated email content that the reader cannot inspect. The archive stays public; the email is the habit.

---

## 6. What AI can and cannot generate

### Can

- Extract dates, entities, jurisdictions, product names, and status changes from official records.
- Deduplicate records that describe the same event across feeds.
- Draft a one-line plain-language "what changed" with a citation.
- Translate reviewed English into Spanish.
- Validate a JSON schema, check links, and reject missing fields.
- Produce the issue page, the email body, and the archive metadata from the same structured issue.

### Cannot

- Invent a deadline, a rule number, a product, or a jurisdiction.
- Decide whether a rule applies to a specific reader.
- Give legal, financial, clinical, or safety advice.
- Replace the named reviewer.
- Republish paywalled standards or licensed rate data.
- Guarantee an outcome, a rate, a return, or a response time.

The practical rule: **AI drafts rows, a human signs the issue.** If a row has no citation, it does not ship.

---

## 7. The generation pipeline

One pipeline, two output formats. Full prompt pack and schema: `strategy/offer-guides/README.md`.

1. **Collect.** Pull new records since the last issue from the channel feeds plus the primary source for the offer. Record the source version and fetch time.
2. **Normalize.** Map each record to `{title, date, jurisdiction, entity, action, source_url, source_name}`. Drop anything missing a URL or a date.
3. **Select.** Keep only what changed and what a professional must act on. Cap at 5 rows for a brief, 12 for a reference.
4. **Draft.** LLM returns JSON matching the issue schema. It may paraphrase the source; it may not add a fact.
5. **Validate.** Schema, date parse, link check, duplicate check, banned-claim scan, row count, and a "no source, no row" gate. Fail closed.
6. **Review.** A named human checks every row against the source, edits the copy, and signs the issue. The reviewer name is part of the published page.
7. **Translate.** Only after EN sign-off. Translate commentary, keep proper nouns and source titles in English, and require a second read of every action/date row.
8. **Publish.** Write the dated issue page, the archive entry, and the email body from the same JSON. Send through `pilo-mail` with double opt-in and unsubscribe.
9. **Measure.** Issue open, row click, brief subscribe, asset join, question, and consultation. Attribute by offer slug and channel.

Build seam: add `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`, unique on channel + offer + date), a CLI command `python -m news_api.cli offer build|publish`, and source adapters per family. The existing `AssetOffer` waitlist becomes the email CTA; the public issue page is the honest fallback while delivery is being wired.

---

## 8. Ranked recommendations

Ranked by leverage per unit of work.

| # | Recommendation | Why it moves the business | Effort | Dependency |
|---|----------------|---------------------------|--------|------------|
| R1 | **Reframe the free offer as a dated decision document** | fixes the "why subscribe" problem without new code | S | none |
| R2 | **Publish one issue per live asset channel** (legal, cybersecurity) before adding offers | proves the promise and gives the waitlist something real | M | named reviewer, issue table |
| R3 | **Build the two next reference generators** (financial, manufacturing) | the strongest source sets after the first two; broadens the offer without new traffic | M | R2, reviewer per channel |
| R4 | **Keep three channels on a weekly brief, with the five-item template** | avoids forcing a false reference on weak or risky data | S | copy + email |
| R5 | **Wire delivery through `pilo-mail`** | capture without delivery is the largest trust leak | M | U8/D-002 |
| R6 | **Add a named reviewer gate and fail-closed validation** | the only thing that makes AI-generated regulated content safe | S | owner names |
| R7 | **Ship the offer inventory + check** | makes the offer plan visible and keeps it from drifting | S | done in this session |
| R8 | **Add per-offer funnel events** (`offer_view`, `issue_open`, `issue_click`, `issue_subscribe`) | the current funnel cannot tell which offer works | S | engineering |
| R9 | **Add a dated correction policy and a "last verified" line** | a wrong row handled badly is worse than the wrong row | S | R2 |
| R10 | **Add ES translation only after EN sign-off** | protects the promise in the second locale | S | R6 |
| R11 | **Fix education's primary CTA kind to `consultation`** and keep the brief as the secondary offer | restores the inquiry path on the channel; the current config duplicates the free offer | S | owner confirms intent |

What I would not do:
- Build eleven generators at once. Review capacity is the constraint, not generation.
- Gate the news. The articles are the acquisition surface.
- Promise "daily" or "real-time" for a weekly dataset.
- Republish rate indices, ISO standards, or demand forecasts.
- Add a second competing CTA on a page with an asset.

---

## 9. Rollout

| Tier | Channels | Outcome | Exit rule |
|------|----------|---------|-----------|
| T0 (now) | legal, cybersecurity | publish issue 1 at both locales | issue 1 live, reviewer named, every source 200 |
| T1 (30 days) | financial, manufacturing | generators + issue 1 | 2 issues each, 2 named reviewers, 0 broken citations |
| T2 (60-90 days) | logistics, energy, retail, stem-cell | reference generators | 1 issue each, scope stated, correction policy used |
| T3 (now, review in 90 days) | behavioral-health, education, digital-technology | weekly five-item brief | 6 consecutive weeks, stable source list, then decide reference vs stay brief |

Assets do not all ship because the source exists. They ship when a reviewer is named and the first issue passes validation. That is the brake.

---

## 10. Measurement

Per offer, not per channel only:

| Event | Definition | Use |
|-------|------------|-----|
| `offer_view` | asset/brief card seen | denominator |
| `offer_join` | waitlist or brief signup | capture rate |
| `issue_published` | dated issue live | supply |
| `issue_open` | email open (when delivery exists) | habit |
| `issue_click` | click to a source/row | usefulness |
| `question_submit` | ask-one-question | low-friction lead |
| `consultation_submit` | consultation form | revenue path |

Decision rule for each offer after 8 weeks:
- **keep** if ≥ 1% of offer views join and at least one consultation is attributed;
- **fix** if joins happen but no inquiry, or opens are high and clicks are near zero;
- **kill** if no issue ships for 8 weeks, the reviewer is missing for two issues, or joins are below 0.2% of views.

Do not tune the rule after the first read. Record the read in `DECISIONS.md`.

---

## 11. Risks and guardrails

| Risk | Mitigation |
|------|------------|
| A wrong date or rule reaches a professional reader | named reviewer, every row cited, correction policy, fail closed |
| AI invents a row | schema requires `source_url`; validator fetches it; no source, no row |
| Clinical or financial advice | banned-claim scan per channel; referral language only |
| Paywalled or licensed data republished | source allow-list per channel; no rate indices, ISO text, or demand data |
| Spanish translation changes a deadline | translate commentary only; keep source titles; second read |
| Review capacity becomes the bottleneck | one issue per month per channel, 4 channels in the first quarter |
| Offer drifts from the site | generated inventory + `--check`; admin shows the same switch |
| Capture outruns delivery again | do not enable a new asset card until issue 1 is live |

---

## 12. Decisions needed

1. **Approve the two-format architecture** (reference where public data exists, brief where it does not).
2. **Name one reviewer per reference channel**; without a name the generator must not publish.
3. **Confirm the first two reference builds** after the live pair: financial and manufacturing.
4. **Confirm no paid tier** remains in v1.
5. **Confirm the jurisdiction policy:** US-only reference issues in v1; EU is a later adapter with its own scope.

## Open questions

1. Does the partner for a channel want the subscriber list, or only inquiries? This changes the value of the free offer.
2. Is the archive public or email-gated? Recommendation: public. The email is the habit, not the paywall.
3. Who writes the correction note, the reviewer or the operator?
4. Is a paid data vendor ever in scope? Recommendation: no for v1.

---

## 13. Honesty ledger

| Claim | Grade | Evidence |
|-------|-------|----------|
| Every current offer is capture-only | A | 0 issue pages; briefs archive empty; no sender |
| The weekly brief is a feed digest | A | `BriefSignup` captures; no separate issue content exists |
| Two assets are configured | A | live API `offers.asset` on legal and cybersecurity |
| AI can draft cited rows from public sources | B | feasibility §2-§4; KEV and Federal Register are machine-readable |
| A reference beats a generic newsletter | C | directional; no first-party test yet |
| Review capacity is the binding constraint | B | feasibility §2; KEV review estimate 30-60 min/issue |
| The offer inventory matches the site | A | generated from the live API in this session |

---

## 14. Next action

Approve the architecture and name the first two reviewers. Then publish issue 1 for legal and cybersecurity before building a third generator. The inventory and the eleven guides are ready; the missing input is human sign-off, not more AI.
