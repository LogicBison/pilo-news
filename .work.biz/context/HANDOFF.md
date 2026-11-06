# HANDOFF — Session Bookmark

> **Date:** 2026-11-06
> **Status:** Open — 2026-11-06 — goal: design AI-generatable free offers per channel, per-channel generation guides, and an offer inventory
> **Needs:** owner approval of the offer architecture; named reviewers per reference channel; D4-D6 still open

## Current session

| Step | Status |
|------|--------|
| Context load (strategy, gates, earlier recommendations, live API) | done |
| Offer analysis + recommendations | done - `.work.biz/strategy/20261106-ai-offer-system.md` |
| Offer inventory + generator/check | done - `.work.biz/strategy/offer-inventory.md` |
| 11 channel generation guides | done - `.work.biz/strategy/offer-guides/` |
| Owner approval + named reviewers | pending |

## Pending for next session

| # | Task | Priority |
|---|------|----------|
| 1 | Approve the two-format offer architecture | high |
| 2 | Name legal and cybersecurity reviewers | high |
| 3 | Publish issue 1 for legal and cybersecurity | high |
| 4 | Wire delivery through `pilo-mail` (U8/D-002) | high |
| 5 | Build financial and manufacturing generators | medium |

## Key decisions (locked in)

| # | Decision |
|---|----------|
| D-001 | Three surfaces first (brief capture, proof strip, trust block), review 2027-01-05 |
| D-002 | Email gateway = `pilo-mail` (Brevo upstream); integration deferred |
| D2 (proposed) | No paid subscription in v1 — partner-funded leads only |
| D-015 | One jurisdiction-tagged offer dataset with a visible filter; no one-calendar-per-country; IP default only with override |

## Next action

Approve the architecture and name the legal and cybersecurity reviewers; then publish issue 1 for both before building a third generator.

---

## Latest action (@biz-director)

**Date:** 2026-11-05
**Request:** "All approved with one caveat: One of the main goals of this system is to get leads, this is critical component, and the call to action (professional and appropriate) must be embedded into the build."
**Classified intent:** strategy / offer + lead generation (cross-framework with .ai.ui and .ai)
**Executed:**
1. @biz-strategy analysis -> `.work.biz/strategy/lead-generation.md` (offer ladder, per-vertical CTA + ethics, funnel metrics, partner model)
2. Voice spec applied: prose follows `.work/voice/README.md` (binding per `.cursorrules` § Voice and prose)
**Blockers:** lead pricing and partner model open (U18); partner contracts not started
**Next recommended:** owner review of `.work.biz/strategy/lead-generation.md` §4/§8; then `@biz-pricing` once the model is chosen

---

## Latest action (@biz-director)

**Date:** 2026-11-05
**Request:** "provide additional recommendations on how to make this system a real lead-magnet."
**Classified intent:** advisory (lead-generation growth) → implementation handed to `@x-director`
**Executed:**
1. `@biz-advisory advise` → `.work.biz/strategy/20261105-lead-magnet-recommendations.md` (6 ranked recommendations R1-R6, reframes, outside view, anti-advice, assumptions)
2. Implementable set scoped: R1 brief capture, R2 proof strip, R3 process/trust block — no backend, no migration
3. Decision recorded: `D-001` in `.work.biz/decisions/DECISIONS.md` (three surfaces first, review 2027-01-05)
**Blockers:** R4 (per-channel qualification field) needs a channel CTA config extension = migration approval; R5 (gated asset) needs U8 email; R6 (partner SLA loop) needs U18
**Next recommended:** `@x-director` implements R1-R3 (this session); then owner answers D2/D3 in the recommendations doc

---

## Latest action (@x-director)

**Date:** 2026-11-05
**Request:** "implement all recommendations by biz-director"
**Executed:**
1. R1 brief capture, R2 proof strip, R3 trust block -> `apps/web/src/components/{BriefSignup,ProofStrip,TrustBlock}.tsx` wired to channel home + article, EN/ES copy, all 7 channels
2. Checks: `pnpm lint`, `pnpm typecheck`, `pnpm check` (246 catalog keys, 7 themes) pass; 7/7 channel pages render 200 with the new blocks
**Blockers:** R4 built (migration 008). R5 needs email delivery - `pilo-mail` chosen (D-002), integration deferred. R6 needs U18 partner model
**Next recommended:** `@biz-market-validate design` for the brief-rung test; integrate `pilo-mail` when v1 capture numbers are in

---

## Latest action (@biz-session start)

**Date:** 2026-11-05
**Request:** "what can be offered to visitors to appeal to their subscription/inquiry? Additionally what other improvements can be done in order to improve lead-generation? Generate a report file I can provide to 'ai' and 'ui' to implement the improvements."
**Classified intent:** strategy / offer design + lead-gen backlog → implementation handed to `.ai` and `.ai.ui`
**Executed:**
1. Read `lead-generation.md` + `20261105-lead-magnet-recommendations.md`; checked the live surfaces (`LeadForm.tsx`, `BriefSignup.tsx`, `leads.py`, `analytics.ts`, brief copy).
2. Wrote `.work.biz/strategy/20261105-offer-and-leadgen-brief.md`: 4 subscription offers (S1–S4), 5 inquiry offers (I1–I5), per-channel offer table, 12 ranked improvements (R1–R12), two work packages (`ai` A1–A6, `ui` U1–U8), sequencing in 4 waves, honesty ledger, guardrails.
**Findings worth flagging:** the brief copy promises a Monday send that no code performs; `POST /v1/leads` accepts `utm` but the form never sends it; funnel events fire but there is no read-out.
**Blockers:** D1 email delivery (U8), D3 asset choice, U18 partner model for R6.
**Next recommended:** owner answers D1–D3; then `ai` R3+R4, `ui` R9+R10.

---

## Latest action (@biz-director)

**Date:** 2026-11-05
**Request:** "Are the offered products technically possible to generate (with AI for example)? For any jurisdiction (America + Europe + Asia)? if not, find products for each channel that can be generated so we can keep our promises. Make a full verification of the recommendations / strategy."
**Classified intent:** product feasibility + strategy verification (cross-framework: engineering already shipped the rungs)
**Executed:**
1. Wrote `.work.biz/strategy/20261105-product-feasibility-verification.md`: per-channel verdict, jurisdiction matrix (US/EU/SG/JP/KR/IN/CN), replacement products, claim-by-claim verification V1–V10, generation pipeline with human sign-off, decisions D4–D6.
2. Implemented the offer rungs in the app (engineering, outside `.work.biz` scope): migration 010 (`question`/`asset` lead kinds, 3 new funnel events), `/v1/admin/funnel` + admin Funnel tab, UTM capture on all lead forms, ask-one-question rung on articles, gated asset waitlist (legal), `/{industry}/briefs` archive, `/{industry}/topic/{slug}` hubs, disposable-domain rejection.
**Evidence:** API `pytest` 108 passed; web `lint`/`typecheck`/`check` (306 keys, 10/10 contrast) pass; production build + Playwright 57 passed / 1 skipped; axe 0 violations on 7 URLs incl. the new pages.
**Blockers:** D4–D6; U18 partner model for the SLA loop; U8 email delivery (owner: pre-production).
**Next recommended:** approve D4–D6; build the cybersecurity KEV digest as the first real asset; commit the app changes.

---

## Latest action (@biz-products scope)

**Date:** 2026-11-06
**Request:** "scope the cybersecurity KEV digest as the first gated asset"
**Mode:** scope (one concept, MVP depth)
**Executed:**
1. Loaded context: offer brief, feasibility verification, lead-generation strategy, gates/decisions, tech fingerprint (RSS-only sources, no issue table, waitlist asset card, inert SMTP).
2. Measured the live CISA KEV feed (2026-11-06): 1,768 rows, catalog 2026.11.04, 6.6 additions/week, 6 rows with a future due date, top-20 vendors cover 64%.
3. Wrote `.work.biz/plans/plan_kev-digest.md`: verdict, evidence table, 7-item MVP, out-of-scope list, DoD, first users, 30-day metric, build shape (migration 011 + `news_api.digests` + CLI + two endpoints + one page), 4–6 day estimate, variant matrix, 14-day card test, kill criteria, graded open questions.
4. Corrected the cadence claim in the offer brief (`daily` → `weekly, Wednesday`, D-003 pending).
**Findings worth flagging:** the deadline angle is dead (1,762/1,768 due dates past, US-federal only); the list is a commodity already republished by free tools; the recurring cost is human review, not generation; the asset card is hardcoded to the legal channel (`apps/web/src/app/[locale]/[industry]/page.tsx:57`).
**Blockers:** D-003…D-006; no named reviewer (D6); email delivery deferred (D-002); traffic baseline unknown (U10).
**Next recommended:** approve D-003…D-006 and run the 14-day card test before any generator work.

---

## Latest action (@x-director) — gap resolution

**Date:** 2026-11-06
**Request:** "resolve all gaps"
**Frameworks involved:** .ai, .ai.biz
**Executed:**
1. D-008 recorded: where a channel offers a gated asset, the asset card is the single secondary rung; the brief signup no longer renders there (one email-list ask per page).
2. D-009 recorded: the asset a channel offers now lives in channel config (`cta.asset`), superseding D-007; seeded by `apps/api/migrations/011_seed_asset_offers.sql` and the legal/cybersecurity profiles.
3. M9 added to the master plan §19 (v1.2) with a traceability row, so the iteration is no longer off-plan.
**Blockers:** D-005 (named reviewer) still gates the digest generator; the 14-day window opened 2026-11-06 and closes 2026-11-20.
**Next recommended:** read the funnel at 2026-11-20 against the pre-registered rule in `.work.biz/plans/plan_kev-digest.md` §11.

---

## Latest action (@biz-products scope)

**Date:** 2026-11-06
**Request:** "scope - digital technology channel"
**Mode:** scope (one concept, MVP depth)
**Executed:**
1. Probed ten candidate feeds (8 EN, 2 ES) — all answered 200 with 10–50 items.
2. Wrote `.work.biz/plans/plan_digital-technology-channel.md`: verdict, evidence, 6-item MVP, out-of-scope, DoD, users, metric, 1.5–2 day build shape, variants, a 21-day topic test that costs about an hour, kill criteria, graded questions, D-010…D-013.
3. Corrected the record on two points the evidence did not support: channel build is config-only, but the e2e channel arrays are hardcoded; and liveness of feeds is not quality — `verify-sources` still has to grade them.
**Findings worth flagging:** the real risk is not the build, it is overlap with the cybersecurity channel and saturated AI coverage. A topic hub on cybersecurity is the cheaper demand test.
**Blockers:** D-010 (sequence), partner for the inquiry (U18), asset reviewer (D-005), traffic baseline (U10).
**Next recommended:** approve D-010 and run the 21-day topic test before writing a profile.


---

## Latest action (@biz-session start)

**Date:** 2026-11-06
**Request:** "what improvements can be made to the system, including the free offer on each channel, that makes sense and can be generated using AI, and generate a guide on for each channel on how to generate the deliverables for the subscribers... and include the inventory of offers (similarly to the channel inventory)."
**Classified intent:** strategy / free-offer architecture + per-channel generation guides + offer inventory.
**Executed:**
1. Loaded `.work.biz` context, the offer brief, the feasibility verification, the KEV plan, and the live API for all 11 channels.
2. Found the real gap: every current offer is capture-only. Nine channels capture a generic weekly brief, two capture an asset waitlist, zero publish an issue, and email delivery is still deferred.
3. Wrote `.work.biz/strategy/20261106-ai-offer-system.md`: verdict, current-state table, 10 gaps, two-format architecture (reference vs brief), per-channel recommendation, AI boundaries, pipeline, 10 ranked recommendations, rollout, measurement, risks, decisions.
4. Wrote `.work.biz/strategy/offers/catalog.json` (11 channels) and `.work.biz/strategy/offer-inventory.md` (generated from the live API + catalog).
5. Wrote `.work.biz/strategy/offer-guides/README.md` plus 11 channel guides, each with reader/job, deliverable, sources, AI scope, prompt values, validation, review, distribution, metrics, build notes, and banned claims.
6. Added `.work.biz/scripts/offer-inventory.mjs` + `offers.sh` with `--write` / `--check`.
7. Engineering follow-through (same day): built the offer issue pipeline in `.work/features/offer-generation/20261106-SPEC.md`; legal (Federal Register, scope `US`) and cybersecurity (CISA KEV, scope `global`) drafts exist with 12 rows each; the worker queues due drafts automatically; no publish or email.
**Findings worth flagging:** the weekly brief is a feed digest, not a reason to subscribe; the two asset cards had no published issue behind them; review capacity, not generation, is the binding constraint; three channels should stay on a brief rather than fake a reference.
**Blockers:** a public issue page and publish path are not built; named reviewers are needed only for publish; email remains U8/D-002.
**Next recommended:** review the two drafts (`./bin/offers.sh list`, `show <id> --markdown`), then build the public issue page and publish path. Email stays owner-owned.


---

## Latest action (@biz-director)

**Date:** 2026-11-06
**Request:** "we need to focus on what AI can do — for example, something that it can do is make a selection of the top news of the last 7 days and sent the briefing to the reader, that's something really easy to do, what other products can be generated similarly, that needs to be determined, for example, for legal, a calendar was offered, so, maybe the calendar of events can be generated in a way that we don't need to generate one per country, or maybe per country might be easy, based on the reader's IP address, set up a calendar based on the source data from some free API with the information, or, just put the information together based on regular searches by the AI. What other products can be put together similarly?"
**Classified intent:** product ideas / AI-generatable products → `@biz-products generate`
**Executed:**
1. Loaded the offer analysis, offer inventory, per-channel guides, live draft pipeline, and the existing source adapters.
2. Wrote `.work.biz/strategy/20261106-ai-generated-products.md`: AI capability ladder, jurisdiction decision, 8 product concepts, prioritization matrix, per-channel map, and the 7-Day Desk Brief MVP.
3. Recommendation: one dataset with jurisdiction-tagged rows and a filter, not one calendar per country. IP sets a default with a visible override; AI search is discovery only, never a source.
4. Product order: 7-Day Desk Brief, public issue page + jurisdiction filter, change log, personalized watchlist, then EU/recall/checklist/answer pack/export.
5. Recorded D-015: one jurisdiction-tagged dataset with a visible filter; IP default only with an override; no per-country generator.
**Findings worth flagging:** the 7-day brief is cheap and universal but weakly differentiated; the calendar cost is source acquisition and review, not generation; a per-country generator multiplies maintenance and hides gaps.
**Blockers:** product priority decision; email U8; traffic baseline U10; partner intent U18.
**Next recommended:** build the 7-Day Desk Brief for one channel and test it with ten readers before adding another adapter.

---

## Cross-framework action (@x-director)

**Date:** 2026-11-06
**Request:** "all approved - any questions you answer them with your recommendations - verify the uncomitted code, provide professional/valuable improvements to the system, make sure all is ready, completed, operational."
**Frameworks involved:** .ai, .ai.ui, .ai.biz
**Classified bucket(s):** engineering + ui + business
**Executed:**
1. Accepted the product catalog and D-015 as the jurisdiction direction: one dataset with jurisdiction tags and a visible filter, no per-country generator.
2. Confirmed the renderer now exposes the two drafts through the admin Offers tab; no publish or email yet.
3. Kept the next product choice open: 7-Day Desk Brief vs public reference page.
**Coordination notes:** the technical pipeline is live; the business promise still waits on a public page and delivery.
**Blockers:** public issue page, publish/reviewer, email (U8), product priority.
**Next recommended:** choose the next build and keep the 7-Day Desk Brief as the baseline.
