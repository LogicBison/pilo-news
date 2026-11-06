# REFERENCE DNA — hubspot

**What this is:** Distilled design mechanics from one public website, used as inspiration for an original design.
**Status:** Draft · **Date:** 2026-11-05
**Needs:** operator review (approve or reject) before this DNA can feed an Approved direction.
**Rights basis:** operator asked to use the lead-generation references in the UI Design OS catalog; public-page analysis only, no assets/logos/copy/fonts licensed for reuse — 2026-11-05.
**Confidence:** medium — palette, type, radii, and section count are measured; rendered hierarchy and interaction are inferred.

> Source URL, fetch date, scan method, and limits are mandatory in §1. Tag every claim `measured` / `estimated` / `assumption`. Do not paste page copy, testimonials, logos, or asset URLs.

## 1. Source & provenance

| Field | Value |
|---|---|
| Reference ID | `hubspot` |
| URL | https://www.hubspot.com/ |
| Fetched | 2026-11-05 · static HTML/CSS · no JS · no browser |
| Evidence | `.work.ui/inputs/references/hubspot/evidence.json` · HTTP 200 · sha256 recorded |
| Robots | allowed — no matching disallow rule |
| Rights basis | operator instruction to use lead-generation references from the UI Design OS catalog; public pages, principles only, no cloning — 2026-11-05 |
| Scan limits | JS-rendered modules, computed styles, hover/focus, responsive states, and animation are unobserved; 40 headings / 22 sections / 2 forms were readable |

## 2. Identity & positioning

- **Primary site type:** `saas-product` (measured)
- **All types (multi-label):** `saas-product`, `lead-generation` (measured)
- **Conversion goal:** `free-trial` (measured) · **Secondary goals:** `demo-booking` (measured)
- **Funnel stage:** `decision` (measured)
- **Classification confidence:** medium — reasons cite demo CTA, form on a sales page, and platform/product language
- **Audience & job:** B2B teams choosing a customer platform; job = understand the product family and pick a starting point (`estimated`)
- **Promise / positioning:** one platform across marketing, sales, service, content, data, and revenue (`estimated`)
- **Proof style:** customer logos, product breadth, free tools, ratings (`estimated`)
- **Voice:** plain, benefit-led, specific; little jargon (`estimated`)

## 3. Layout & information architecture

- **Nav model:** mega-menu product-family navigation + login + two CTAs (`get a demo`, `get started free`) (`measured` labels; structure `estimated`)
- **Hero type:** centered platform proposition with a segmented product-family grid below (`estimated`)
- **Section order:** platform hero → hubs/products → proof → free tools → use cases → CTA (`estimated`)
- **Grid / container / measure:** wide container, 3–4-up product cards, generous section gaps (`estimated`)
- **Density:** comfortable, but high section count and many entries (`measured` 22 sections, 40 headings)
- **Measured structure:** 3 navs, 2 forms, 25 CTA labels, 95 images, 222 SVGs

## 4. Color

**Measured palette (top roles):**

| Role | Value (OKLCH/hex) | Evidence | Notes |
|---|---|---|---|
| Canvas | `#fcfcfa` / `#f8f5ee` | measured | warm off-white, not pure white |
| Ink | `#1f1f1f` / `#000000` | measured | near-black |
| Accent | `#ff4800` | measured | orange; dark hover `#c93700` |
| Neutral/border | `#9b9897`, `#cfcccb` | measured | warm-neutral borders |
| Secondary accent | `#fcc6b1`, `#fcc3dc` | measured | soft tints, not identity |

- **Named tokens:** `--cl-background`, `--cl-button-background`, `--cl-anchor-color`, `--cl-button-hover-background` (measured)
- **Dark mode:** not observed for the marketing page
- **Contrast risks observed:** white text on `#ff4800` is near the 3:1 UI threshold and below 4.5:1 for small text — use a darker action fill for text-bearing buttons

## 5. Typography

| Field | Value |
|---|---|
| Display family | HubSpot Serif — proprietary, do not ship (measured) |
| Body family | HubSpot Sans — proprietary, do not ship (measured) |
| Mono/utility | none observed (measured) |
| Scale | token-driven display 01–03 + h1–h4; body 16 px floor (measured tokens) |
| Weights | 300–700, display heavier (measured) |
| Case/tracking | sentence case; small caps for eyebrows (`estimated`) |
| Measure / line-height | comfortable, ~1.5 body (`estimated`) |

## 6. Space, shape & surface

- **Spacing base / rhythm:** 4/8/16/24 px family with large section blocks (measured declarations; rhythm `estimated`)
- **Section padding:** 48–80 px vertical (`estimated`)
- **Radii scale:** 8 px controls, ~16 px cards, pill buttons (measured `8px`/`1rem`/`50%`)
- **Borders:** 1 px card borders, often `0 0 0 1px` outlines instead of shadows (measured)
- **Shadows/elevation:** soft and restrained — `0 1px 24px rgba(33,51,67,.12)` (measured)
- **Background treatment:** warm flat canvas with alternating tinted/card sections; no heavy gradients (measured/estimated)

## 7. Components & patterns

| Pattern | Observed behavior | Transfer? |
|---|---|---|
| Navigation | mega-menu by product family + two intent CTAs | partly — keep our simple nav |
| Primary CTA | solid orange pill, one per section, repeated at section ends | yes — repeat the same primary verb |
| Cards | product tiles with 1 px outline and soft shadow; icon + name + one line | yes — outline cards, short labels |
| Forms | 2-field demo/free-trial form (measured 2 inputs) | yes — short first step |
| Pricing | plan comparison deeper in the site | no |
| Proof/testimonials | logo wall + numbers | yes — proof band before the ask |
| Footer | dense multi-column sitemap | no — keep sparse |

## 8. Motion & interaction

- **Measured transitions/animations:** 36 transition declarations; color/shadow/transform at 150–250 ms (`measured`)
- **Unobserved:** hover, focus, scroll, page transitions — not observed
- **Transfer candidates:** hover shadow lift on cards; no scroll-jacking

## 9. Imagery & iconography

- **Mix:** product UI screenshots, illustrations, and customer photography (`estimated`)
- **Aspect & treatment:** cards and screenshots in soft containers; illustration-led empty states (`estimated`)
- **Icon style:** simple line/solid icons inside circular chips (`estimated`)
- **Do not reuse:** orange trade dress, illustrations, product screenshots, logos, or copy

## 10. Copy & content patterns

- **Headline shapes:** product-family name + one-line job; benefit first, feature second (`estimated`)
- **CTA verbs:** get a demo, get started free, learn more (measured labels; paraphrase)
- **Proof types:** logos, counts, free tools, ratings (estimated)
- **Reading level/voice:** plain, workmanlike, specific (`estimated`)
- **No verbatim reuse:** paraphrase only; short labels ≤10 words are observations, not copy

## 11. Transfer rules

### Adopt
- Warm off-white canvas; cards read as raised without heavy shadow.
- One strong accent; all other color is neutral or a soft tint.
- Proof before features and before the ask.
- Segmented entry paths so different intents do not share one generic CTA.
- Two-field first step; more fields only after intent is known.

### Adapt
- The accent stays the channel's accent, not orange.
- Keep our two-CTA model (consultation + brief) instead of a product-family mega-menu.
- Use original illustration/motif, not HubSpot's product screenshots.
- Keep section count low: an editorial page, not a platform catalogue.

### Avoid
- Orange as identity, HubSpot illustrations, product UI screenshots, copy.
- Logo-wall proof we cannot substantiate (no invented customers).
- Mega-menu density on a single-channel page.
- White text on a mid-orange fill for small labels.

### Originality constraints
- Own palette (per channel), own composition (asymmetric editorial hero), own proof band, own copy.
- Recognition test: a viewer must not name HubSpot from the new screen.
- Minimum 3 differentiating moves: channel-owned accent rule; a two-path action panel; a live-data proof band with tabular figures.

## 12. Evidence & confidence

| Claim | Tag | Evidence / gap |
|---|---|---|
| Warm off-white canvas + near-black ink + orange accent | measured | palette frequency |
| 8 px controls, ~16 px cards, pill buttons | measured | radii declarations |
| 1 px outlines + soft shadow elevation | measured | shape/shadow declarations |
| Two-field form | measured | 2 inputs + 2 forms |
| Proof-before-features ordering | estimated | section/heading order; rendered layout not observed |
| Mega-menu product-family nav | estimated | 32 nav labels; markup not fully rendered |
| 26/95 images without alt | measured | image scan |

**What would raise confidence:** operator screenshot · authorized browser capture · responsive states · design-system page.

## Next action

`@ui-reference-intake synthesize - ellevest hubspot leadpages` — DNAs are Draft; synthesize a direction next.
