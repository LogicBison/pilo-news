# NEXT — Tactical Next Actions

**Status:** Active (2026-11-06)
**Needs:** product priority decision (7-day brief vs public reference page first); jurisdiction filter decision; email delivery (U8).

## Current Phase

| Phase | Status |
|-------|--------|
| Strategy | Offer architecture + AI product catalog written |
| Product catalog | `strategy/20261106-ai-generated-products.md` (8 products, jurisdiction options, 7-day brief MVP) |
| Offer inventory | Generated: `strategy/offer-inventory.md` (11 channels) |
| Generation guides | 11 channel guides + common pipeline in `strategy/offer-guides/` |
| Brand | Pending (U1 name) |
| Pipeline | Pending (U18 partner model) |
| Delivery | Pending (U8 / D-002) |
| Execution | Capture live; 0 issues published |

## Next action

1. **First step:** build the 7-Day Desk Brief for one channel and put it in front of ten readers before adding another adapter. Then add the public issue page and jurisdiction filter to the existing legal draft.

## Active tasks

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Approve reference-vs-brief architecture | Open | `strategy/20261106-ai-offer-system.md` §5, §12 |
| 2 | Name legal reviewer | Open | blocks issue 1; D-005 |
| 3 | Name cybersecurity reviewer | Open | blocks KEV issue 1; D-005 |
| 4 | Publish legal issue 1 | Draft generated 2026-11-03; publish path not built | `strategy/offer-guides/legal.md` |
| 5 | Publish cybersecurity KEV issue 1 | Draft generated 2026-11-04; page/publish not built | `strategy/offer-guides/cybersecurity.md` |
| 6 | Wire `pilo-mail` delivery | Blocked | U8 / D-002 |
| 7 | Build financial Rule-Change Tracker | Planned | tier 1 |
| 8 | Build manufacturing Recall Tracker | Planned | tier 1 |
| 9 | Add per-offer funnel events | Planned | `offer_view`, `issue_open`, `issue_click`, `offer_join` |
| 12 | Build the public issue page and publish gate | Not built | drafts live in `offer_issues`; no public route |
| 10 | Run `offers.sh --check` in the local gate | Ready | append to `./bin/start.sh test` via engineering |
| 11 | Fix education `cta.kind` from `brief` to `consultation` | Open | current primary form duplicates the secondary brief; see analysis G11 |
| 13 | Build the 7-Day Desk Brief MVP | Ready | 5 sourced items, 7 days, one channel; `strategy/20261106-ai-generated-products.md` §8 |
| 14 | Add a public issue page + jurisdiction filter | Not built | reuses the legal draft; filter, not one calendar per country |
| 15 | Add a change log between issues | Planned | new/updated/closed rows; after the public page |
| 16 | Decide the next adapter: EU, recall, or energy | Open | one adapter, one scope, one reviewer |

## Done this session (2026-11-06)

| Item | Artifact |
|------|----------|
| Offer analysis + recommendations | `.work.biz/strategy/20261106-ai-offer-system.md` |
| Machine-readable offer plan | `.work.biz/strategy/offers/catalog.json` |
| Offer inventory (generated) | `.work.biz/strategy/offer-inventory.md` |
| Inventory generator/check | `.work.biz/scripts/offer-inventory.mjs`, `offers.sh` |
| Common generation pipeline | `.work.biz/strategy/offer-guides/README.md` |
| 11 channel generation guides | `.work.biz/strategy/offer-guides/<slug>.md` |
| AI product catalog | `.work.biz/strategy/20261106-ai-generated-products.md` |

## Done before this session

| Item | Status |
|------|--------|
| UTM capture, funnel read-out, ask-one-question, asset waitlist, briefs archive, topic hubs | shipped |
| Legal + cybersecurity asset cards | shipped, capture-only |
| R3/R4/R9/R10 from the offer brief | shipped |

## Blocked on owner

| # | Item | Notes |
|---|------|-------|
| 1 | Reviewer names | the generator refuses to publish without one |
| 2 | Delivery date | capture without delivery is the largest trust leak |
| 3 | Partner subscriber-list intent | changes the value of the free offer |
