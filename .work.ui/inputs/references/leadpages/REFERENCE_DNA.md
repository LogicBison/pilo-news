# REFERENCE DNA — leadpages

**What this is:** Distilled design mechanics from one public website, used as inspiration for an original design.
**Status:** Draft · **Date:** 2026-11-05
**Needs:** operator review (approve or reject) before this DNA can feed an Approved direction.
**Rights basis:** operator asked to use the lead-generation references in the UI Design OS catalog; public-page analysis only, no assets/logos/copy/fonts licensed for reuse — 2026-11-05.
**Confidence:** high — the static page is content-rich and the palette/type/radii/section evidence is consistent; rendered interaction remains unobserved.

> Source URL, fetch date, scan method, and limits are mandatory in §1. Tag every claim `measured` / `estimated` / `assumption`. Do not paste page copy, testimonials, logos, or asset URLs.

## 1. Source & provenance

| Field | Value |
|---|---|
| Reference ID | `leadpages` |
| URL | https://leadpages.com/ |
| Fetched | 2026-11-05 · static HTML/CSS · no JS · no browser |
| Evidence | `.work.ui/inputs/references/leadpages/evidence.json` · HTTP 200 · sha256 recorded |
| Robots | allowed — `Allow: /` |
| Rights basis | operator instruction to use lead-generation references from the UI Design OS catalog; public pages, principles only, no cloning — 2026-11-05 |
| Scan limits | JS-rendered modules, computed styles, hover/focus, responsive states, and animation are unobserved; 39 headings / 12 sections / 5 articles were readable |

## 2. Identity & positioning

- **Primary site type:** `saas-product` (measured) — override to include `lead-generation` because the page sells lead capture and form collection
- **All types (multi-label):** `saas-product`, `lead-generation`
- **Conversion goal:** `free-trial` (measured) · **Secondary goals:** `demo-booking` (measured)
- **Funnel stage:** `decision` (measured)
- **Classification confidence:** high — SaaS CTA language, JSON-LD SoftwareApplication, platform/product framing
- **Audience & job:** small-business marketers building landing pages; job = launch a page that converts without a designer (`estimated`)
- **Promise / positioning:** an AI landing-page builder + CRO toolkit: create, test, measure in one place (`estimated`)
- **Proof style:** product capabilities, template gallery, numbers, customer outcomes (`estimated`)
- **Voice:** punchy, benefit-led, verb-first; short sentences (`estimated`)

## 3. Layout & information architecture

- **Nav model:** grouped product/resources navigation + `Create a page` CTA (`measured` labels; structure `estimated`)
- **Hero type:** oversized benefit headline + sub + primary CTA, product-led (`estimated`)
- **Section order:** hero → generate/optimize/measure loop → templates → capability grid → integrations → trust/CTA (`estimated`)
- **Grid / container / measure:** wide container, 3-up and 4-up card grids, clamped display type (`measured` `clamp()` sizes; grid `estimated`)
- **Density:** dense but chunked; 12 sections, 37 CTA labels (`measured`)
- **Measured structure:** 3 navs, 39 headings, 37 CTAs, 153 images, 127 SVGs, 5 articles

## 4. Color

**Measured palette (top roles):**

| Role | Value (OKLCH/hex) | Evidence | Notes |
|---|---|---|---|
| Canvas | `#ffffff` / `#f1f1ee` | measured | white + warm gray studio canvas |
| Ink | `#0c0b14` / `#111827` | measured | near-black |
| Primary accent | `#613dff` | measured | violet; darkens to `#603eff` |
| Secondary accent | `#ceff66` | measured | lime highlight |
| Neutral/border | `#e5e7eb`, `#d1d5db` | measured | cool neutrals |
| Soft tints | `#f0eeff`, `#c4b5fd` | measured | panel fills |

- **Named tokens:** `--ad-canvas-bg` (`#f1f1ee`), `--ads-panel-divider`, `--ads-platform-group-shadow` (measured)
- **Dark mode:** not observed on the marketing page
- **Contrast risks observed:** lime and violet-on-violet can drop below 4.5:1 for body text; the palette works only when accent is a fill, not text

## 5. Typography

| Field | Value |
|---|---|
| Display family | Instrument Serif / Fraunces fallbacks observed — open-source alternatives exist (measured) |
| Body family | Inter (measured) |
| Mono/utility | Space Mono / DM Mono (measured) |
| Scale | 10/12/13/14/15/16/17/18 px + `clamp(1.875rem, 3.1vw, 2.75rem)` display (measured) |
| Weights | 300–800; display 650–800 (measured) |
| Case/tracking | sentence case; tight display tracking (`estimated`) |
| Measure / line-height | short paragraphs, ~1.4 body (`estimated`) |

## 6. Space, shape & surface

- **Spacing base / rhythm:** 8 px family with 80 px hero blocks and 20–40 px card padding (measured declarations; rhythm `estimated`)
- **Section padding:** 80 px vertical on the hero (`measured 80px 20px 80px`)
- **Radii scale:** 8/10/12/14/16/18/20 px + pill (measured)
- **Borders:** 1 px black/alpha outlines; hard offset shadows as borders (`0 0 0 1px` + `0 10px 28px`)
- **Shadows/elevation:** two languages — hard offset/inset card shadow and soft glow around primary actions (measured)
- **Background treatment:** warm canvas + dot grid + gradient glass panels (`--ad-canvas-dot`, gradients measured)

## 7. Components & patterns

| Pattern | Observed behavior | Transfer? |
|---|---|---|
| Navigation | grouped product nav + single create CTA | partly — keep our thin nav |
| Primary CTA | high-contrast pill, repeated in hero and section ends | yes — repeat one verb |
| Cards | outlined cards with hard offset shadow; template thumbnails | yes — offset-shadow feature cards |
| Forms | landing-page product; 2 inputs on page (measured) | yes — 2-field capture |
| Pricing | plan CTA deeper in site | no |
| Proof/testimonials | capability grid + template gallery + numbers | yes — proof modules |
| Footer | dense sitemap | no |

## 8. Motion & interaction

- **Measured transitions/animations:** 88 transition declarations; 130–220 ms color/background/transform; hover shadow + lift (`measured`)
- **Unobserved:** scroll reveals, page transitions — not observed
- **Transfer candidates:** 160–200 ms hover lift on action cards; no scroll-triggered entitlement

## 9. Imagery & iconography

- **Mix:** product UI screenshots, template thumbnails, abstract gradient panels (`estimated`)
- **Aspect & treatment:** cards with rounded corners and inner screenshot frames (`estimated`)
- **Icon style:** simple line icons in pills (`estimated`)
- **Do not reuse:** violet/lime identity, template designs, screenshots, logos, copy

## 10. Copy & content patterns

- **Headline shapes:** outcome + mechanism ("landing pages that improve themselves with A/B testing") (`measured` heading pattern)
- **CTA verbs:** create, generate, optimize, measure, start (measured labels; paraphrase)
- **Proof types:** capability demos, template counts, outcomes (estimated)
- **Reading level/voice:** direct, verb-first, low jargon (`estimated`)
- **No verbatim reuse:** paraphrase only; short labels ≤10 words are observations, not copy

## 11. Transfer rules

### Adopt
- One repeated primary verb per page; the same action appears at hero and section end.
- Outlined cards with a hard offset shadow for feature/proof modules (not for reading cards).
- Oversized, tight display headline over short supporting copy.
- A visible loop: capture → qualify → respond, presented as three blocks.
- Dot-grid or paper texture as a quiet canvas layer (not a gradient wash).

### Adapt
- Keep the channel palette; violet/lime are not our identity.
- Use the offset-shadow language on the action panel and proof modules only; reading cards stay calm.
- Limit the page to 5–6 sections; Leadpages' density is too high for a news channel.
- Replace product screenshots with our own editorial photography and line-art motifs.

### Avoid
- Violet/lime trade dress, gradient glass panels, template thumbnails.
- 80 px hero padding with no content density on mobile.
- Hard shadows under every card (visual noise).
- Clone markers: violet hero + lime highlight + serif display + dot grid in the same arrangement.

### Originality constraints
- Own palette (channel), own composition, own imagery treatment, own copy.
- Recognition test: a viewer must not name Leadpages from the new screen.
- Minimum 3 differentiating moves: channel-tinted action surface; editorial photo band; a two-path CTA (consult vs brief) with different visual weight.

## 12. Evidence & confidence

| Claim | Tag | Evidence / gap |
|---|---|---|
| White + warm gray canvas, violet + lime accents | measured | palette frequency |
| Inter body + serif display + mono utility | measured | font declarations |
| 8–20 px radii, pill buttons | measured | radii declarations |
| Hard offset shadows + soft action glow | measured | shadow declarations |
| 80 px hero padding | measured | padding declarations |
| Repeated CTA / capability-grid structure | estimated | 37 CTA labels + section headings; layout not rendered |
| 64/153 images without alt | measured | image scan |

**What would raise confidence:** operator screenshot · authorized browser capture · responsive states · design-system page.

## Next action

`@ui-reference-intake synthesize - ellevest hubspot leadpages` — DNAs are Draft; synthesize a direction next.
