# Offer inventory

**What this is:** the canonical list of free offers per channel: the recommended deliverable, its type and cadence, what the site captures today, and the generation guide.
**Status:** Generated 2026-11-06 · **Needs:** re-generate after any offer, channel, or catalog change; a stale file fails the local check.
**Source:** `GET /v1/industries` + `GET /v1/industries/{slug}` joined with `strategy/offers/catalog.json`. The live capture column is evidence; the recommendation column is a plan.

## Inventory

<!-- OFFER_INVENTORY_BEGIN -->
**API:** http://127.0.0.1:46105 · **Channels:** 11 · **Plan:** 8 reference (2 waitlist, 6 planned), 3 brief · **Live capture:** 2 asset waitlist, 9 brief signup · **Published issues:** 0
**Reading rule:** the catalog is the recommendation; the API column is what the site captures today. A row with `planned` is not a promise to readers.

| # | Channel | Slug | Free offer (recommended) | Type | Status | Cadence | Scope | AI draft | Capture today | Guide |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Legal Services & Corporate Governance | `legal` | US Regulatory Calendar | asset | asset, waitlist | monthly, first Tuesday | US | extract US federal dates and entities from primary notices | asset waitlist `legal-regulatory-calendar` | [guide](offer-guides/legal.md) |
| 2 | Financial Services & Banking | `financial` | US Rule-Change Tracker | asset | asset, planned | monthly, second Wednesday | US | extract US rule status, dates, and affected entities | brief signup | [guide](offer-guides/financial.md) |
| 3 | Psychiatry & Clinical Psychology | `behavioral-health` | Practice & Payer Brief | brief | brief, live capture | weekly, Thursday | US | summarize regulator and payer notices | brief signup | [guide](offer-guides/behavioral-health.md) |
| 4 | Education & Higher Academics | `education` | Enrollment Deadline Brief | brief | brief, live capture | weekly during term, monthly otherwise | US | extract dates and institution names | brief signup | [guide](offer-guides/education.md) |
| 5 | Logistics & Supply Chain | `logistics` | US Port & Customs Notice Digest | asset | asset, planned | weekly, Monday | US | extract US notice dates, ports, and effective windows | brief signup | [guide](offer-guides/logistics.md) |
| 6 | Cybersecurity & Threat Intelligence | `cybersecurity` | CISA KEV Digest | asset | asset, waitlist | weekly, Wednesday | global | filter, dedupe, and paraphrase the required action | asset waitlist `cybersecurity-kev-digest` | [guide](offer-guides/cybersecurity.md) |
| 7 | Stem Cell Treatments | `stem-cell` | US Trial & Regulatory Digest | asset | asset, planned | monthly, third Tuesday | US | extract US registry status, phase, sponsor, and dates | brief signup | [guide](offer-guides/stem-cell.md) |
| 8 | Manufacturing & Industrial Operations | `manufacturing` | US Recall & Regulator Notice Tracker | asset | asset, planned | monthly, second Thursday | US | extract US product, hazard, and remedy | brief signup | [guide](offer-guides/manufacturing.md) |
| 9 | Energy & Utilities | `energy` | US Grid Queue & Docket Digest | asset | asset, planned | monthly, first Thursday | US | extract US queue status, dates, and jurisdictions | brief signup | [guide](offer-guides/energy.md) |
| 10 | Retail & E-commerce | `retail` | US Consumer Policy & Recall Calendar | asset | asset, planned | monthly, fourth Tuesday | US | extract US dates, products, and obligations | brief signup | [guide](offer-guides/retail.md) |
| 11 | Digital Technology | `digital-technology` | AI Infrastructure & Policy Brief | brief | brief, live capture | weekly, Tuesday | US + EU | summarize official releases and policy text | brief signup | [guide](offer-guides/digital-technology.md) |

**Offer rules:** one secondary offer per channel · asset needs a citable source and a named reviewer · every row carries a URL and an issue date · no autopublish · EN is reviewed before ES is translated · no offer promises advice, a rate, a return, or an outcome.

### Rollout
| Tier | Channels |
|---|---|
| T0 | `legal` (asset, waitlist) · `cybersecurity` (asset, waitlist) |
| T1 | `financial` (asset, planned) · `manufacturing` (asset, planned) |
| T2 | `logistics` (asset, planned) · `stem-cell` (asset, planned) · `energy` (asset, planned) · `retail` (asset, planned) |
| T3 | `behavioral-health` (brief, brief live) · `education` (brief, brief live) · `digital-technology` (brief, brief live) |

**Live delivery:** 0 published issues. Every current offer is capture-only; see the analysis at `strategy/20261106-ai-offer-system.md`.
<!-- OFFER_INVENTORY_END -->

## Drafts

This table shows the public capture state and the offer plan. It does not show
generated drafts. Legal and cybersecurity drafts are stored in `offer_issues`;
inspect them with `./bin/offers.sh list` and render one with
`./bin/offers.sh show <id> --markdown`. A draft is not published and has no
reviewer signature.

## How to keep it updated

1. Change the offer plan in `strategy/offers/catalog.json`, or change a channel's offers in the admin console.
2. Run `.work.biz/scripts/offers.sh --write` with the stack up.
3. Run `.work.biz/scripts/offers.sh --check`; it fails when this file is stale or a channel is missing from the catalog.
4. Commit the catalog, the guide, and the regenerated inventory together.

The generated block is the only machine-owned part. Edit the prose outside the markers by hand.

## Next action

`.work.biz/scripts/offers.sh --write` after any offer change.
