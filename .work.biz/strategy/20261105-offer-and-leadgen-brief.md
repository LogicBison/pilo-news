# Offer and lead-generation brief — for `.ai` and `.ai.ui`

**What it is:** what to offer readers so they subscribe or inquire, plus the ranked build backlog that turns those offers into leads. Written as an implementation brief: every item names an owner (`ai` / `ui`), files, acceptance criteria, and the promise it makes to the reader.
**Status:** In review (2026-11-05) — R2/R3/R4/R10/R12, the ask-question rung, the asset waitlist, the briefs archive, and topic hubs are built; R1/R6/R11 remain open. Feasibility of every gated product is verified in `.work.biz/strategy/20261105-product-feasibility-verification.md`.
**Needs:** D4–D6 in the feasibility doc (jurisdiction scope, logistics product, asset reviewer); D1 email delivery is owner-owned and lands before production.

---

## 1. What we are actually selling

The reader does not want news. They want to know whether something changed that affects them, before it costs them. Two offers follow from that, and only two:

1. **"Tell me first."** A recurring, short, channel-specific update — subscription.
2. **"Answer me when it matters."** A route to one vetted professional — inquiry.

Everything else (proof strip, trust block, sticky bar) exists to make those two believable. Anything that does not feed one of them is decoration.

## 2. What to offer

### 2.1 Subscription offers

| ID | Offer | What the reader gets | Friction | Status today | Ethics guardrail |
|----|-------|----------------------|----------|--------------|------------------|
| S1 | **Weekly brief** (per channel) | one email, Monday, the stories that moved the field | name + email + consent | capture shipped (`BriefSignup.tsx`), **delivery missing** | copy promises a Monday send — see §6 R1 |
| S2 | **First alert** (breaking, opt-in per channel) | an instant email when a high-impact item publishes in your channel | same as S1 + topic choice | not built | only for items an editor pins; never auto-fired on volume |
| S3 | **Reference asset** (gated, per channel) — jurisdiction must be in the title; see the feasibility verdict | a durable document the reader keeps: regulatory calendar (legal), rule-change tracker (financial), enrollment deadlines (education), rate/lane index (logistics), vigilance notice format (health), retention/clinic protocols (stem-cell, behavioral health), recall tracker (manufacturing, retail), grid interconnection queue digest (energy) | email + consent | not built; needs content owners | must be genuinely useful and dated; no "report" that is a repackaged feed |
| S4 | **Archive** | past briefs, public, indexed | none | not built | proof that S1 is real |

Recommendation: ship S1 properly, then S3 for one channel, then S2. S4 ships with S1 (built: `/{industry}/briefs`).

Feasibility changed the pick: the legal calendar is buildable for US + EU only, and the cheapest honest proof is the **cybersecurity KEV digest** (free, global; **weekly, Wednesday** — measured at 6.6 additions/week, see `.work.biz/plans/plan_kev-digest.md`; D-003 pending). The logistics rate index cannot be built at all — replacement in the feasibility doc §4.

**Paid subscription: no.** No payment surface, no traffic baseline, and the partner-funded model (U18) is not signed. A paid tier now would convert nothing and cost a checkout flow.

### 2.2 Inquiry offers

| ID | Offer | What the reader gets | Friction | Status today | Ethics guardrail |
|----|-------|----------------------|----------|--------------|------------------|
| I1 | **Consultation** | one vetted partner replies in one business day | name, email, qualification, consent | shipped (`LeadForm.tsx`, `POST /v1/leads`) | no advice in copy; referral, not representation |
| I2 | **Ask one question** | a written answer without a call | email + one question field | not built | answer is general information, not legal/financial/medical advice; says so in the form |
| I3 | **Shortlist / checklist** | a vetted shortlist or a document checklist for the reader's situation | email + qualification | not built | partners pay for routing; the list is not sold to the reader |
| I4 | **Callback** | a time window instead of a form monologue | phone + window | not built (phone field exists) | never pre-check "call me"; the reader picks the window |
| I5 | **Second opinion** | review of a document or decision the reader already has | upload is **out of scope**; describe + email | not built | no document upload in v1 (PII risk) |

I2 is the highest-leverage addition: it lowers the ask from "talk to a stranger" to "ask a question", and a written answer is a lead with a stated need.

### 2.3 Offer by channel

| Channel | Subscription hook | Inquiry hook | Never say |
|---------|------------------|--------------|-----------|
| legal | weekly regulatory calendar | ask one question about a filing/clause | "we win", outcome promises |
| financial | rule-change tracker | speak with a licensed advisor | returns, "risk-free" |
| behavioral-health | weekly practice brief | request an appointment | medical advice, PHI requests |
| education | enrollment deadline calendar | request program information | accreditation/outcome guarantees |
| logistics | rate and lane index | talk to a supply-chain specialist | rate guarantees |
| cybersecurity | CVE/threat digest | incident readiness review | "we'll stop the breach" |
| stem-cell | protocol and trial digest | lab partnership inquiry | clinical claims |
| manufacturing | recall and standards tracker | automation readiness assessment | compliance certification claims |
| energy | interconnection queue digest | grid/PPA advisory inquiry | tariff or price guarantees |
| retail | holiday/consumer-demand calendar | retail operations review | sales-lift promises |

## 3. Ranked backlog

Ranked by leverage per unit of work; "impact" is directional until traffic is known (U10 open).

| # | Improvement | Why it moves leads | Owner | Effort | Depends on |
|---|-------------|--------------------|-------|--------|-----------|
| R1 | **Keep the subscription promise** — deliver the Monday brief (double opt-in, unsubscribe, archive) or soften copy today | the page currently promises a send that cannot happen; a dead promise burns the only trust asset we have | `ai` (+ `ui` copy) | L | D1 |
| R2 | **Ask one question** (I2) as the article-level rung | lowers the ask; produces a lead with a stated need | `ui` + `ai` | M | - |
| R3 | **UTM + referrer capture** on every lead and funnel event | attribution is impossible now; `POST /v1/leads` already accepts `utm`, the form never sends it | `ai` + `ui` | S | - |
| R4 | **Funnel read-out** — `/v1/admin/funnel` (impressions → clicks → starts → submits → qualified, by channel/placement) | we ship CTA changes blind; 4 events already fire | `ai` | M | - |
| R5 | **One reference asset** (S3) for legal, gated | converts intent into a real exchange, creates the archive | `ui` + owner content | M | D3 |
| R6 | **Partner SLA loop** (R6 in the earlier doc): notify, acknowledge timer, 24 h reminder, status surfaced in admin | a lead nobody answers is negative revenue | `ai` | M | U18 |
| R7 | **First alert** (S2) per channel, editor-pinned only | highest-intent subscription for regulatory verticals | `ai` + `ui` | M | D1, R1 |
| R8 | **Topic hub pages** (SEO + CTA) per channel | brings intent earlier in the search funnel | `ui` + `ai` | M | - |
| R9 | **Micro-truth in the CTA** — "replies within one business day" only when measured | unverifiable claims age badly and partners notice | `ui` | S | R6 |
| R10 | **Form resilience** — inline field errors, keep values on failure, autofill hints, "2 of 3" progress on the brief | every failed submit is a lost lead | `ui` | S | - |
| R11 | **ES parity for retail** (10 EN vs 1 ES) | half the funnel is starved on one channel | `ai` (feeds) | M | feeds |
| R12 | **Spam and duplicate hardening** — disposable-domain check, same-email-per-channel dedupe surface in admin | protects partner trust and CPL math | `ai` | S | - |

## 4. Work packages

### Package `ai` — backend, data, delivery

| Task | Files / surfaces | Acceptance criteria |
|------|------------------|---------------------|
| A1 brief delivery | `apps/api/src/news_api/publishing/`, new `subscriptions` table via numbered migration under `apps/api/migrations/`, `pilo-mail`/Brevo adapter, `./bin/start.sh` env keys | double opt-in: `pending → confirmed`; unsubscribe link works; ack + Monday send queued; secrets only via `.env.*` |
| A2 UTM capture | `POST /v1/leads` (already accepts `utm`), `cta-events` payload, `leads` storage | a lead created from `?utm_source=x` stores it and shows in admin; no PII in logs |
| A3 funnel read-out | `GET /v1/admin/funnel?industry=&from=&to=` | returns the 5 stage counts by channel and placement; contract test with ETag; OpenAPI snapshot updated |
| A4 partner SLA | `leads` status transitions, notification adapter, 24 h reminder job | status visible in admin; reminder fires once; no email leaves without a partner record |
| A5 ask-a-question endpoint | extend `LeadRequest` with `question` or reuse `message` + `kind="question"` | validation 10–600 chars; rate limit unchanged; stored with `kind` |
| A6 dispatch | `subscriptions` + `topics` join, per-channel segment | one send per confirmed subscriber per week; bounce/complaint marks `bounced` |

### Package `ui` — surfaces, copy, states

| Task | Files / surfaces | Acceptance criteria |
|------|------------------|---------------------|
| U1 brief flow states | `BriefSignup.tsx`, new confirm/unsubscribe routes, `messages/{en,es}.json` | pending, confirmed, already-subscribed, invalid-link states; cadence copy matches reality; no "Monday" until A1 ships |
| U2 ask-a-question rung | article page + new component under `components/ui/` | one field + email + consent; ≤3 fields total; renders on all 10 channels; axe clean |
| U3 asset card | channel home + article, gated | card names the asset, the date, and what arrives; waitlist when content is not ready |
| U4 archive page | `/{industry}/briefs` (EN/ES) + sitemap | lists past briefs with dates; indexable; empty state honest |
| U5 topic hub | `/{industry}/topic/{slug}` + sitemap | lists items, carries one CTA; no duplicate content vs search |
| U6 CTA truth | `CtaCard.tsx`, `messages/*` | response-time string comes from a measured value or drops the promise |
| U7 form resilience | `components/ui/text-field.tsx` + forms | field errors inline + associated; values kept on server failure; autofill hints correct |
| U8 funnel events | `lib/analytics.ts` | adds `brief_confirm`, `question_submit`, `asset_interest`; UTM passed through |

## 5. Sequence

| Wave | Items | Why this order |
|------|-------|----------------|
| 1 (days) | R3, R4, R9, R10 | measurement + honesty; no new surface, no backend risk |
| 2 (1–2 weeks) | R1 (A1+U1), R2 (A5+U2) | keeps the promise, then lowers the ask |
| 3 | R5, R6, R8, R12 | asset, partner loop, SEO |
| 4 | R7, R11 | alerts and locale parity |

## 6. Honesty ledger

| Claim | Grade | Note |
|-------|-------|------|
| The brief copy promises a Monday send that no code performs | **A (first-party)** | `messages/en.json` `brief.value1` / `brief.success`; no sender exists (U8 deferred, `.work/plans/UNKNOWNS.md:L14`) |
| UTM is accepted by the API but never sent by the form | **A (first-party)** | `leads.py` `utm: dict[str, str] | None`; `LeadForm.tsx` body has no `utm` |
| Lower-friction asks raise conversion | **C (directional)** | standard funnel behaviour; no first-party test yet. Test with R2 before widening |
| One asset beats a generic newsletter | **C (directional)** | publisher benchmarks are vendor-reported; treat as hypothesis |
| Alerts raise retention | **D (assumption)** | no data; only ship editor-pinned alerts |

## 7. Guardrails (binding on both packages)

- One primary action per page; the second rung never competes visually.
- No popups, exit-intent, countdowns, fake scarcity, invented social proof.
- Marketing email is double opt-in; consultation email is single opt-in because the reader initiated it.
- No PHI and no document upload; free-text fields carry a "do not include sensitive details" line.
- Legal/financial/health copy stays referral language, never advice.
- Every promise on screen must be a fact in the system, or it gets removed.

## Decisions needed

1. **D1 — wire email delivery now (pilo-mail/Brevo) or soften the brief copy to "join the list"?** R1 is blocked on this.
2. **D2 — confirm no paid subscription in v1.**
3. **D3 — first gated asset: legal regulatory calendar, or financial rule-change tracker?**

## Open questions

1. Which channel pilots I2 (ask one question) — legal (widest portfolio) or financial (highest intent)?
2. Is partner routing email-only at v1, or does the partner get a console login?
3. Who owns content production for the gated asset, and on what cadence?

## Next action

Approve D1; then `ai` ships R3 + R4 (measurement, one day) while `ui` ships R9 + R10 (copy truth, form resilience).
