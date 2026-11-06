# REFERENCE DNA — ellevest

**What this is:** Distilled design mechanics from one public website, used as inspiration for an original design.
**Status:** Draft · **Date:** 2026-11-05
**Needs:** operator review (approve or reject) before this DNA can feed an Approved direction.
**Rights basis:** operator asked to use the lead-generation references in the UI Design OS catalog; public-page analysis only, no assets/logos/copy/fonts licensed for reuse — 2026-11-05.
**Confidence:** medium — static HTML/CSS evidence is strong on palette/type/radii, thin on rendered layout and interaction.

> Source URL, fetch date, scan method, and limits are mandatory in §1. Tag every claim `measured` / `estimated` / `assumption`. Do not paste page copy, testimonials, logos, or asset URLs.

## 1. Source & provenance

| Field | Value |
|---|---|
| Reference ID | `ellevest` |
| URL | https://www.ellevest.com/ |
| Fetched | 2026-11-05 · static HTML/CSS · no JS · no browser |
| Evidence | `.work.ui/inputs/references/ellevest/evidence.json` · HTTP 200 · sha256 recorded |
| Robots | allowed — no matching disallow rule |
| Rights basis | operator instruction to use lead-generation references from the UI Design OS catalog; public pages, principles only, no cloning — 2026-11-05 |
| Scan limits | JS-rendered modules, computed styles, hover/focus, responsive states, and animation are unobserved; 20 headings / 3 sections / 2 forms were readable |

## 2. Identity & positioning

- **Primary site type:** `forms-surveys` (measured; quiz-led entry) — override to `lead-generation` for this intake because the page's job is lead capture
- **All types (multi-label):** `forms-surveys`, `finance`, `lead-generation`
- **Conversion goal:** `contact-quote` (measured) · **Secondary goals:** `lead-magnet` (measured)
- **Funnel stage:** `decision` (measured)
- **Classification confidence:** medium — taxonomy reasons cite quiz language, finance identity, and wealth/planning content
- **Audience & job:** women and families planning wealth; job = find the right service without a sales call first (`estimated`)
- **Promise / positioning:** wealth management tailored to the reader's situation, with expertise and credentials as proof (`estimated`)
- **Proof style:** credentials, named expertise, audience-specific outcomes; no star-rating theatre (`estimated`)
- **Voice:** warm, direct, second person, question-led; low pressure (`estimated`)

## 3. Layout & information architecture

- **Nav model:** goal-based horizontal nav (goals, insights, life events, login) + primary CTA (`measured` labels; structure `estimated`)
- **Hero type:** editorial split with a question-shaped entry and a quiz/CTA (`estimated`)
- **Section order:** value proposition → quiz/lead capture → audience segments → proof and expertise → secondary CTA (`estimated`)
- **Grid / container / measure:** full-width warm bands with a centered content column; measure not observable (`assumption` until screenshot)
- **Density:** comfortable to airy; large type, generous vertical padding (`estimated`)
- **Measured structure:** 3 sections, 20 headings, 6 nav labels, 19 CTA labels, 2 forms, 50 images

## 4. Color

**Measured palette (top roles):**

| Role | Value (OKLCH/hex) | Evidence | Notes |
|---|---|---|---|
| Canvas | `#fbf3e7` (`--cashmere`) | measured | warm cream; second cream `#f8e8cf` |
| Ink | `#2b2928` (`--charcoal`) | measured | near-black, low chroma |
| Primary | `#0f9a8e` / `#034b45` / `#26724d` | measured | teal + deep green family |
| Accent | `#c66e4e` | measured | terracotta; secondary highlight `#e9ffb3` |
| Neutral/border | `#979797`, `#c5d8be` | measured | warm-neutral dividers |

- **Named tokens:** `--cashmere`, `--charcoal`, `--ellevest-green`, `--cyprus`, `--ev-green`, `--highlight`, `--papaya-whip` (measured)
- **Dark mode:** not observed
- **Contrast risks observed:** lime highlight and light green surfaces can sit below 4.5:1 for body text; 46 of 50 images lack alt text (measured) — do not inherit

## 5. Typography

| Field | Value |
|---|---|
| Display family | GT Super Display — proprietary, do not ship (measured) |
| Body family | Maison Neue Book/Demi/Light — proprietary, do not ship (measured) |
| Mono/utility | Maison Neue Mono (measured) |
| Scale | 12/14/15/18/24/32/38 px + `2em` display (measured); serif display over sans body |
| Weights | 300–800; light body, heavy display (measured) |
| Case/tracking | sentence-case headings; uppercase only in small labels (`estimated`) |
| Measure / line-height | long-form measure, generous leading (`estimated`) |

## 6. Space, shape & surface

- **Spacing base / rhythm:** 8 px family with 20/30/60 px padding steps (measured declarations; rhythm `estimated`)
- **Section padding:** ~60 px vertical on desktop (measured `60px 30px` and `80px` blocks)
- **Radii scale:** mixed 0/2/3/40/100 px; buttons pill, cards mostly near-square (measured)
- **Borders:** hairline 1 px + occasional inset accent underline (measured shadows include inset accent bars)
- **Shadows/elevation:** soft only — `0 6px 16px #00000014`, `0 2px 7px #00000021` (measured)
- **Background treatment:** flat warm color blocks, occasional highlight swash; no gradient system (measured/estimated)

## 7. Components & patterns

| Pattern | Observed behavior | Transfer? |
|---|---|---|
| Navigation | goal-based entries + login + primary CTA; language switch | yes — goal-first entry |
| Primary CTA | pill button, `Take our quiz` / `Become a client` | yes — one low-friction action |
| Cards | warm surface panels, minimal border, generous padding | yes — surface rhythm |
| Forms | quiz/question flow plus a contact form (2 forms measured) | yes — progressive capture |
| Pricing | not observed | no |
| Proof/testimonials | credentials and expertise, not star ratings | yes — evidence over theatre |
| Footer | dense link groups (`estimated`) | no — keep ours sparse |

## 8. Motion & interaction

- **Measured transitions/animations:** 18 transition declarations; mostly color/shadow, 150–300 ms (`measured`)
- **Unobserved:** hover, focus, scroll, page transitions (state clearly) — not observed
- **Transfer candidates:** only the calm 150–200 ms color/shadow timing; no scroll theatre

## 9. Imagery & iconography

- **Mix:** lifestyle photography + editorial portraiture + illustration accents (`estimated`)
- **Aspect & treatment:** large warm-toned photos, rounded or full-bleed bands (`estimated`)
- **Icon style:** thin line icons (`estimated`)
- **Do not reuse:** logos, portraits, photography, icon sets, or recognizable compositions

## 10. Copy & content patterns

- **Headline shapes:** question first ("Need help finding the right product?"), then audience-specific promise (measured headings)
- **CTA verbs:** take, discover, become, get (measured labels; paraphrase)
- **Proof types:** named expertise, credentials, client outcomes (estimated)
- **Reading level/voice:** plain, warm, second person; low urgency (estimated)
- **No verbatim reuse:** paraphrase only; short labels ≤10 words are observations, not copy

## 11. Transfer rules

### Adopt
- Warm off-white canvas with a deep, calm primary and one warm accent.
- Question-shaped entry that leads to a low-friction capture step.
- Proof before the ask: credentials and process ahead of the form.
- Large serif display over quiet sans body.
- Flat color blocks and soft elevation, not gradient mush.

### Adapt
- Keep each channel's own palette; do not import cream/teal as identity.
- Replace the quiz with the channel's qualification select or a two-step form.
- Use our existing type stack (Georgia/system) to avoid a webfont dependency.
- Keep the CTA panel visually distinct without copying Ellevest's composition.

### Avoid
- Proprietary GT Super / Maison Neue fonts.
- Low-contrast lime highlights for text; decorative-only use if at all.
- Photography with missing alt text; our images must carry alt + credit.
- Clone markers: cream + teal + serif headline + pill CTA in the same arrangement.

### Originality constraints
- Own palette (per channel), own hero composition (asymmetric front page), own imagery treatment (channel-tinted scrim), own copy.
- Recognition test: a viewer must not name Ellevest from the new screen.
- Minimum 3 differentiating moves: channel-specific color blocking; a proof band with tabular figures; a two-path action panel (consultation vs brief).

## 12. Evidence & confidence

| Claim | Tag | Evidence / gap |
|---|---|---|
| Warm cream canvas + deep green primary + terracotta accent | measured | palette frequency in `evidence.json` |
| Proprietary serif/sans families | measured | font declarations |
| 8 px spacing family with 60 px section padding | measured | padding declarations |
| Soft shadows, mixed radii | measured | shape/shadow declarations |
| Quiz-led, low-friction capture | estimated | CTA labels + 2 forms; rendered flow not observed |
| Audience-specific, warm voice | estimated | headings + description; not a full copy audit |
| 46/50 images without alt | measured | image scan |

**What would raise confidence:** operator screenshot · authorized browser capture · responsive states · design-system page.

## Next action

`@ui-reference-intake synthesize - ellevest hubspot leadpages` — DNAs are Draft; synthesize a direction next.
