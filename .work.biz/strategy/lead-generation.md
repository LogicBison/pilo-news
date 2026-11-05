# Lead generation - offer, CTA ladder, and funnel

**What it is:** the business case for lead capture on System News: who the lead is, what is offered, how the CTA ladder works per industry, and how the funnel is measured.
**Status:** Draft (2026-11-05) · **Needs:** owner review of the partner model and per-vertical offers.
**Voice:** prose follows `.work/voice/README.md`; UI labels follow `.work.ui` copy rules (sentence case, direct, no hype).

---

## 1. Why leads are the product

The sites publish news to earn attention; the revenue is in qualified inquiries routed to partner professionals per industry. A reader who needs help after reading a legal, financial, health, education, or logistics story is the asset. The build must therefore treat the CTA as a first-class feature, not a footer link.

**Success is not pageviews.** Success is qualified leads per channel at an acceptable cost per lead.

## 2. Buyer and lead

| Element | Definition |
|---------|------------|
| **Lead** | A person who asks to be contacted by a professional in the channel they are reading |
| **Buyer of the lead** | A partner firm or independent professional in that industry (per channel) |
| **Qualification** | Valid contact + stated need + channel match + consent + not spam |
| **Exclusions** | Job seekers, vendors selling to us, students, journalists, obvious bots |

The reader is not the buyer. Do not optimize the CTA for the reader's entertainment; optimize for a real need that a partner can serve.

## 3. Offer ladder

| Tier | Offer | Friction | Used for |
|------|-------|----------|----------|
| **L1 primary** | "Request a consultation" / "Talk to a specialist" → short form | name, email, phone (optional), need, consent | High-intent readers on article + channel home |
| **L2 secondary** | "Get the weekly brief" → email only | email + consent | Readers not ready to buy; builds the list |
| **L3 tertiary** | "Send this story to a colleague" / save | none | Engagement, not revenue |

One primary CTA per page. Secondary and tertiary never compete visually with it.

## 4. Per-channel CTA and ethics

| Channel | Primary CTA | Form asks | Copy guardrails |
|---------|-------------|-----------|-----------------|
| Legal | "Request a free consultation" | name, email, phone, matter type, brief description | not legal advice; attorney advertising disclosure; no outcome promises; no "we win" language |
| Financial | "Speak with a licensed advisor" | name, email, phone, goal, brief description | not investment advice; risk disclosure; no return promises |
| Behavioral health | "Request an appointment" | name, email, phone, preferred time, brief note | not medical advice; no PHI requested; crisis line shown; "if this is an emergency call 911" |
| Education | "Request program information" | name, email, program interest | no accreditation/outcome guarantees |
| Logistics | "Talk to a supply-chain specialist" | name, email, company, lane/volume | no rate guarantees |

**Universal:** no fake urgency, no hidden fees, no pre-checked consent, no "someone just requested" social-proof fabrication, no medical/legal/financial advice.

## 5. CTA ladder placement (business intent)

| Surface | Primary CTA | Secondary | Notes |
|---------|-------------|-----------|-------|
| Channel home | hero card + sticky mobile bar | brief signup | hero CTA must be visible above the fold on mobile |
| Article | inline after the summary, plus end-of-article card | brief signup | never interrupt reading mid-paragraph |
| Search/topic | inline CTA block after results | brief signup | - |
| About | contact card | - | trust and credentials |
| Footer | text link | brief signup | always available, never the only path |

## 6. Funnel metrics

| Stage | Metric | Target (v1, assumed) |
|-------|--------|----------------------|
| Exposure | CTA impressions per channel/session | - |
| Interest | CTA click-through rate | ≥ 2% of sessions |
| Intent | form start rate | ≥ 40% of clicks |
| Capture | submit rate | ≥ 50% of starts |
| Quality | qualified lead rate | ≥ 60% of submits |
| Partner | routed within 24 h | ≥ 95% |
| Economics | cost per qualified lead | tracked, no target until 3 months of data |

**Instrumentation is part of the CTA spec**, not an afterthought: every impression, click, start, submit, and qualification is an event.

## 7. Consent and privacy (business view)

- Explicit opt-in checkbox (never pre-checked), purpose stated in one line, privacy link.
- Store consent text version + timestamp.
- Double opt-in for the brief; single opt-in for a consultation request is acceptable because the reader initiated contact.
- No sale of the list; partner routing only for the requested channel.
- Deletion on request within 30 days; 24-month retention for lead records unless the partner contract says otherwise.
- No sensitive data in free-text fields; the form warns not to include it.

## 8. Partner model (v1)

- One partner per industry at launch (owner-managed), routed by channel; geo routing deferred.
- Delivery: email notification + admin inbox; partner acknowledges within 24 h (SLA), status tracked.
- No partner sees another partner's leads. No public partner directory at v1.
- Contract must state: consent basis, retention, no resale, response SLA.

## 9. Voice and copy

- UI labels: sentence case, verb-first, concrete. "Request a consultation", not "Unlock expert help".
- Prose around the CTA: one sentence of why, one of what happens next, no hype.
- Banned: "act now", "limited spots", "guaranteed", "risk-free", "expert secrets".
- Professional audience: raise formality one notch, keep directness. No exclamation marks.

## 10. Open questions

1. Is the lead sold per lead, per qualified lead, or subscription? (Pricing decision.)
2. Is there a partner per channel at launch, or one multi-industry partner?
3. Do we offer phone callback or email only?
4. Is the brief (newsletter) in v1 or Phase B?
5. Which channel pilots lead capture first? (Recommendation: legal.)

## Next action

Owner review of §4 offers and §8 partner model; then the engineering contract (ADR 013, SPEC rules, plan tasks) is applied.
