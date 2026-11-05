# Lead magnet — additional recommendations

**What it is:** advisory pass on how to turn the seven news channels into a working lead magnet, ranked, with what gets built now versus what is blocked.
**Status:** Draft (2026-11-05) · **Needs:** owner decision on the brief rung (D1) and on the gated-asset asset (D2).
**Builds on:** `.work.biz/strategy/lead-generation.md` (offer ladder, funnel targets, partner model). This doc does not restate it.

## Context summary

```
LOADED CONTEXT
  Operator:     solo operator + agent, no sales team; partner firms are the lead buyers
  Situation:    how to raise qualified-lead volume without new spend
  Assets:       7 live channels, 32 verified feeds, EN/ES, DeepSeek summaries, editorial console,
                lead API that already accepts kind=consultation|brief, consent + DSAR plumbing,
                funnel events (cta_impression, cta_click, lead_form_start, lead_submit)
  Constraints:  no email vendor chosen (U8), no lead pricing model (U18), no paid acquisition budget
  Active strategy: lead-generation.md - L1 consultation primary, L2 brief secondary (unbuilt)
  Live decisions:  none recorded before today
  Gaps:         traffic level (U10) and partner count (U18) - both change what "works" means
```

## Reframes

**Reframe 1 — don't sell "news", sell "the five minutes before you need a professional".** The reader is not shopping for articles; they are checking whether something changed that affects them. The magnet is not more content, it is *being told first*, with a person to ask. Usable sentence: "The stories that move your field, plus one person who will answer when you need it."

**Reframe 2 — don't sell a "contact form", sell a "response promise".** A form is friction; a promise is the offer. Today the CTA says what to do but not what happens next, which is the exact gap the CTA brief already names (`.work.ui/design-system/20261105-CTA-BRIEF.md:33`). Usable sentence: "Send this, and a vetted [legal/financial/clinical] partner replies within one business day."

## Recommendations (ranked)

### R1 — Add the L2 brief rung as real UI, not a label

**What:** a two-field capture ("weekly brief": first name + email + consent) on channel home and article pages, posting `kind=brief`. The lead API requires a non-empty name (`apps/api/src/news_api/publishing/http/leads.py:23`), so the pure email-only variant would need a backend change; two fields is the cheapest honest version.
**Why:** the offer ladder promises L2 (`.work.biz/strategy/lead-generation.md:30-32`) and the CTA config already carries `secondary_label`, but no UI exists — the rung is fiction. The API already accepts `kind: "brief"` (`apps/api/src/news_api/publishing/http/leads.py:22`), so no backend work is needed to capture interest.
**Evidence:** A (first-party code + config).
**Effort:** S. **Blocked on:** nothing to capture; delivery/sending waits on U8.
**Build now:** yes.

### R2 — Put verifiable proof above the fold

**What:** a four-fact strip per channel: stories live now, sources monitored, last updated, "no paywall, no ads".
**Why:** every claim is checkable from the bundle response, so it is honest proof, not a testimonial nobody can verify (`.work.biz/strategy/lead-generation.md:46` bans fabricated social proof). It also answers the reader's first question — is this current and independent.
**Evidence:** A (bundle payload carries `total`, `sources`, `generated_at`).
**Effort:** S. **Blocked on:** nothing.
**Build now:** yes.

### R3 — Show the process beside the CTA

**What:** a three-step "how this works" block (send the form → we route to one vetted partner in your channel → you get a reply within one business day) plus the no-resale line.
**Why:** the CTA brief requires "what happens next + timing" and an explicit trust line; the current CTA card carries only a one-sentence body and a disclaimer (`.work.ui/design-system/20261105-CTA-BRIEF.md:29-36`). Trust is the conversion lever for regulated verticals.
**Evidence:** A (project requirement) + `C` for the general claim that process transparency raises form completion — single secondary source, directional only.
**Effort:** S. **Blocked on:** nothing.
**Build now:** yes.

### R4 — Ask one qualifying question per channel

**What:** a required select on the consultation form — matter type (legal), goal (financial), program (education), lane/volume (logistics), concern (health, non-clinical wording).
**Why:** the funnel target is ≥60% qualified (`.work.biz/strategy/lead-generation.md:66`); partner routing without a qualification field cannot hit it. The CTA brief already specifies the field (`20261105-CTA-BRIEF.md:49`) but channel config has no options list.
**Evidence:** A (funnel target) — the conversion lift from one added field is `D` and not claimed.
**Effort:** M. **Blocked on:** nothing — approved 2026-11-05, migration 008 + API field + UI select shipped.
**Build now:** **built 2026-11-05** — migration `008_channel_qualification.sql`, `qualification` on `leads`, select in `LeadForm`, 7 channel option sets.

### R5 — Make the brief a real asset, not a promise

**What:** a per-channel gated briefing (e.g. "regulatory calendar", "funding rounds digest") as an actual deliverable behind the L2 capture.
**Why:** a named asset converts better than "newsletter", but only if it exists. Nothing ships today: no email vendor (U8), no content production schedule, no archive page.
**Evidence:** `C` — publisher benchmark of ~0.9% signup from newsletter prompts (5-publisher study, vendor-reported, [leakypaywall.com PDF](https://leakypaywall.com/wp-content/uploads/2026/08/Publishers-AI-Survival-Guide.pdf)); treated as directional, not as a target.
**Effort:** L. **Blocked on:** delivery — `pilo-mail` gateway chosen (D-002) but integration deferred; content production; archive surface.
**Build now:** no.

### R6 — Close the loop on the partner side

**What:** partner notification with an acknowledgement timer and a status the console already tracks (`new → routed → contacted`).
**Why:** "routed within 24 h ≥95%" is a funnel target with no mechanism behind it (`.work.biz/strategy/lead-generation.md:67`); a lead that is never answered is a cost, not revenue.
**Evidence:** A (target exists), `D` on partner behaviour until a partner is signed.
**Effort:** M. **Blocked on:** U18 (partner model) and an email/integration transport.
**Build now:** no.

## Outside view (base rate)

Reference class: a small publisher network bolting lead capture onto news traffic with no paid acquisition. What normally happens: consultation forms convert at low single-digit percent of *sessions that see them*, brief capture runs below 1% of readers, and most of the loss is upstream — the CTA is seen too late or not at all. Grade `directional` (no first-party traffic data yet; U10 open). Consequence for this plan: fix *placement and proof* (R2, R3) before adding capture surface (R5), because capture on unproven placement just measures the placement.

## Anti-advice

- **Do not add popups or exit-intent modals.** Banned by R18 and by the voice rules; they also trade long-term trust for a short-term bounce metric.
- **Do not gate the news itself.** The articles are the magnet; paywalling them kills the funnel that feeds the CTA.
- **Do not invent social proof** ("1,200 readers requested this week") — R18 forbids it and a partner will check.
- **Do not build the email pipeline before picking a vendor.** Sending is U8; capturing is free.
- **Do not add a second competing CTA.** One primary action per page is an invariant (SPEC I7).

## Arithmetic (does it close?)

Unknown traffic (U10), so this is a sensitivity, not a forecast. At 5,000 channel sessions/month, a 2% CTA click rate (the v1 target) gives 100 clicks; 40% form start and 50% submit gives ~20 leads/month across the network, which is below one partner's capacity but enough to prove routing. The plan therefore targets *quality per lead* (R3, R4) over volume (R5) until traffic is known. `assumption`.

## What I would actually do

Ship R2 and R3 first — they are one file each, need no backend, and they fix the two things that make a CTA convert: proof and process. Then R1, so the L2 rung stops being fiction. Hold R4/R5/R6 behind the three owner decisions below. Confidence 70%, two-way door (all three are UI changes revertible in a day).

## Assumption ledger

| Assumption | Label | If wrong |
|------------|-------|----------|
| Proof and process move conversion more than a new asset | Inference | R5 gets prioritised earlier and needs U8 |
| Trailers of traffic exist to measure (U10) | Unknown | Funnel numbers stay unreadable; ship is still safe |
| A brief capture with no delivery is acceptable short-term | Inference | Readers who opt in get nothing; U8 becomes urgent |
| Partner can respond within one business day | Unknown | The R3 promise becomes a broken promise — soften the copy until a partner is signed |

## Decisions needed

1. **D1 — ship R1–R3 now?** The brief rung captures emails before any delivery mechanism exists. Alternative: wait for U8.
2. **D2 — is the gated asset (R5) in scope for v1?** It is the strongest magnet and the largest effort.
3. **D3 — approve a channel CTA config extension** (migration + seed) for per-channel qualification fields (R4).

## Open questions

1. Which channel pilots the qualification field — `legal` (widest portfolio) or `logistics` (phone/company already required)?
2. Does the brief promise a cadence ("every Monday") before a send mechanism exists? Copy currently avoids it.

## Next action

Approve D1; R1–R3 are implemented in this session behind it (`apps/web/src/components/`).
