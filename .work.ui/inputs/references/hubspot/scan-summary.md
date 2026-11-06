# Reference scan: `hubspot`

**Status:** Draft evidence · **Needs:** author `REFERENCE_DNA.md` (interpretation is not automated).

> Derived facts only. This is **not** a design spec, and it must not be treated as permission to reuse assets, copy, logos, fonts, or layout wholesale.

## Source

- **Requested:** https://www.hubspot.com/
- **Final:** https://www.hubspot.com/ (HTTP 200)
- **Fetched:** 2026-11-05T21:34:10+00:00 · static HTML/CSS · no JS · no screenshot
- **Robots:** allowed — no matching robots rule (allow)
- **Title:** HubSpot | Software & Tools for your Business - Homepage
- **Description:** HubSpot's customer platform includes all the marketing, sales, customer service, and CRM software you need to grow your business.
- **Framework hints:** none detected

## Classification (two axes)

- **Primary type:** `saas-product`
- **All types:** `saas-product`, `lead-generation`
- **Conversion goal:** `free-trial` · **Funnel:** `decision`
- **Confidence:** medium — lead-generation: sales CTA: get a demo; lead-generation: form on a sales-CTA page; saas-product: SaaS CTA/product language: get started free, platform, software; saas-product: platform + product

## Palette candidates (measured: CSS declaration frequency)

| Color | OKLCH | Role | Count |
|---|---|---|---|
| `#000000` | `oklch(0.0% 0.000 0.0)` | dark / text | 78 |
| `#ffffff` | `oklch(100.0% 0.000 89.9)` | light surface | 69 |
| `#1f1f1f` | `oklch(23.9% 0.000 89.9)` | dark / text | 63 |
| `#ff4800` | `oklch(66.3% 0.227 36.0)` | accent | 41 |
| `#f8f5ee` | `oklch(97.1% 0.010 87.5)` | light surface | 25 |
| `#c93700` | `oklch(55.4% 0.190 36.0)` | dark / text | 18 |
| `#fcfcfa` | `oklch(99.1% 0.003 106.4)` | light surface | 13 |
| `#9f2800` | `oklch(46.4% 0.161 35.6)` | dark / text | 12 |
| `#9b9897` | `oklch(68.2% 0.004 39.5)` | neutral | 11 |
| `#fcc6b1` | `oklch(86.9% 0.068 42.3)` | accent | 11 |
| `#cfcccb` | `oklch(84.7% 0.004 39.5)` | neutral | 10 |
| `#d9002b` | `oklch(55.8% 0.226 23.3)` | dark / text | 8 |
| `#2f7579` | `oklch(52.0% 0.070 200.4)` | dark / text | 7 |
| `#b9cdbe` | `oklch(82.9% 0.030 153.2)` | neutral | 7 |
| `#fcc3dc` | `oklch(87.5% 0.072 350.6)` | accent | 6 |
| `#292929` | `oklch(28.1% 0.000 89.9)` | dark / text | 5 |
| `#00823a` | `oklch(53.0% 0.146 150.0)` | dark / text | 5 |
| `#fcc5be` | `oklch(87.0% 0.064 26.8)` | accent | 5 |

### Named color tokens (semantic hints)

| Token | Value |
|---|---|
| `--a11y-contrast-toggle-background-color` | `#0000c5` |
| `--a11y-contrast-toggle-border-color` | `#2e475d` |
| `--a11y-contrast-toggle-enabled-color` | `#ffffff` |
| `--a11y-contrast-toggle-icon-color` | `#1f1f1f` |
| `--a11y-contrast-toggle-text-color` | `#1f1f1f` |
| `--cl-anchor-color` | `#1f1f1f` |
| `--cl-anchor-color-dark` | `#f8f5ee` |
| `--cl-anchor-hover-color` | `#1f1f1f` |
| `--cl-anchor-hover-color-dark` | `#f8f5ee` |
| `--cl-anchor-pressed-color` | `#1f1f1f` |
| `--cl-background` | `#fcfcfa` |
| `--cl-badge-background-color` | `#cfcccb` |
| `--cl-badge-background-color-default` | `#cfcccb` |
| `--cl-badge-border-color` | `#9b9897` |
| `--cl-button-background` | `#ff4800` |
| `--cl-button-color` | `#ffffff` |
| `--cl-button-disabled-color` | `#000000` |
| `--cl-button-hover-background` | `#c93700` |

## Type declarations

- Families: HubSpot Sans, HubSpot Serif, Zen Kaku Gothic New, HubSpot Serif Page Header Human
- Sizes: ['2em', '1em', '80%', '75%', '100%', 'var(--cl-text-font-size)', 'var(--cl-font-size-display-01)', 'var(--cl-font-size-display-02)', 'var(--cl-font-size-display-03)', 'var(--cl-font-size-h1)', 'var(--cl-font-size-h1-small)', 'var(--cl-font-size-h2)', 'var(--cl-font-size-h3)', 'var(--cl-font-size-h4)']
- Weights: ['bolder', '300 400', '500 600', '400 600', '300', '500', '700', 'var(--cl-text-font-weight)', 'var(--cl-font-weight-display-01)', 'var(--cl-font-weight-display-02)']

## Layout / component signals

- Landmarks: {'header': 1, 'nav': 3, 'form': 2, 'section': 22, 'main': 1, 'footer': 1}
- Headings: 40 · nav labels: 32 · CTA labels: 25
- Sections: 22 · forms: {'forms': 2, 'inputs': 2, 'labels': 2, 'required': 0} · images: {'total': 95, 'missing_alt': 26, 'lazy': 74, 'srcset': 46, 'svg': 222}
- Radius values: ['1rem', 'var(--cl-border-radius-container)', 'var(--cl-border-radius-medium)', '8px', '0 0 .1875rem .1875rem', 'calc(var(--a11y-contrast-toggle-px-height)*1px/2)', '50%', 'inherit', '0 50% 50% 0', 'var(--cl-border-radius-small)']
- Breakpoints: ['max-width 568px', 'max-width 1080px']
- Motion declarations: 36 transition values

## Limits

- Static HTML/CSS only: JavaScript-rendered DOM, computed style, hover/focus states, and animations are not observed.
- CSS declaration frequency is not visual usage: unused framework/reset rules can dominate the palette.
- CSS cascade/layers are not resolved; `<style>` blocks and linked stylesheets are analyzed independently.
- Cross-origin iframes, shadow DOM, canvas/WebGL, video, and image contents are skipped.
- Robots.txt is respected for the page fetch; no crawl, no forms, no auth, no paywall bypass.
- No screenshot was taken and no browser was launched. Browser/vision tiers need explicit operator authorization.
- No logos, images, fonts, icons, or page copy should be reused; this evidence supports principles, not assets.

## Next action

`@ui-reference-intake dna - hubspot` — author the DNA from this evidence + optional operator screenshot; keep claims tagged `measured` / `estimated` / `assumption`.
