# Reference scan: `leadpages`

**Status:** Draft evidence · **Needs:** author `REFERENCE_DNA.md` (interpretation is not automated).

> Derived facts only. This is **not** a design spec, and it must not be treated as permission to reuse assets, copy, logos, fonts, or layout wholesale.

## Source

- **Requested:** https://leadpages.com/
- **Final:** https://leadpages.com/ (HTTP 200)
- **Fetched:** 2026-11-05T21:34:04+00:00 · static HTML/CSS · no JS · no screenshot
- **Robots:** allowed — allow: /
- **Title:** The AI Landing Page Builder | Leadpages
- **Description:** Create high-converting landing pages with AI, templates, testing, analytics, and built-in marketing integrations. Launch faster with Leadpages.
- **Framework hints:** none detected

## Classification (two axes)

- **Primary type:** `saas-product`
- **All types:** `saas-product`
- **Conversion goal:** `free-trial` · **Funnel:** `decision`
- **Confidence:** high — saas-product: SaaS CTA/product language: platform; saas-product: JSON-LD SoftwareApplication; saas-product: platform + product; content-seo: 5 <article> elements

## Palette candidates (measured: CSS declaration frequency)

| Color | OKLCH | Role | Count |
|---|---|---|---|
| `#ffffff` | `oklch(100.0% 0.000 89.9)` | light surface | 167 |
| `#000000` | `oklch(0.0% 0.000 0.0)` | dark / text | 80 |
| `#613dff` | `oklch(53.7% 0.265 281.2)` | dark / text | 33 |
| `#e5e7eb` | `oklch(92.8% 0.006 264.5)` | neutral | 24 |
| `#603eff` | `oklch(53.7% 0.264 280.8)` | dark / text | 21 |
| `#666d7a` | `oklch(53.3% 0.022 262.9)` | dark / text | 15 |
| `#111827` | `oklch(21.0% 0.032 264.7)` | dark / text | 12 |
| `#ceff66` | `oklch(93.7% 0.186 124.9)` | light surface | 12 |
| `#0c0b14` | `oklch(15.6% 0.019 289.1)` | dark / text | 11 |
| `#ef4343` | `oklch(63.6% 0.209 25.4)` | accent | 10 |
| `#d1d5db` | `oklch(87.2% 0.009 258.3)` | neutral | 7 |
| `#374151` | `oklch(37.3% 0.031 259.7)` | dark / text | 5 |
| `#6245f2` | `oklch(53.5% 0.243 282.1)` | dark / text | 5 |
| `#f59f0a` | `oklch(77.0% 0.165 70.7)` | accent | 5 |
| `#21ca89` | `oklch(74.3% 0.160 160.5)` | accent | 5 |
| `#c4b5fd` | `oklch(81.1% 0.101 293.6)` | accent | 5 |
| `#eeeff2` | `oklch(95.2% 0.004 271.4)` | light surface | 5 |
| `#f0eeff` | `oklch(95.6% 0.023 291.4)` | light surface | 5 |

### Named color tokens (semantic hints)

| Token | Value |
|---|---|
| `--ad-canvas-bg` | `#f1f1ee` |
| `--ad-canvas-dot` | `#282828` |
| `--ads-checkbox-border` | `#141414` |
| `--ads-chip-bg` | `#ffffff` |
| `--ads-chip-border` | `#000000` |
| `--ads-chip-btn-bg` | `#ffffff` |
| `--ads-chip-btn-bg-hover` | `#ffffff` |
| `--ads-chip-btn-border` | `#000000` |
| `--ads-chip-fg` | `#000000` |
| `--ads-chip-fg-muted` | `#000000` |
| `--ads-panel-divider` | `#141414` |
| `--ads-platform-group-bg` | `#ffffff` |
| `--ads-platform-group-border` | `#141414` |
| `--ads-platform-group-border-hover` | `#141414` |
| `--ads-platform-group-shadow` | `#141414` |
| `--ads-row-header-fg` | `#000000` |
| `--ads-row-header-fg2` | `#1e1e28` |
| `--beta-border` | `#c4b5fd` |

## Type declarations

- Families: Inter, -apple-system, Georgia, Inter Fallback, lumenSans, lumenSans Fallback, Space Mono, Space Mono Fallback, Instrument Sans, Instrument Sans Fallback, Instrument Serif, Instrument Serif Fallback, Fraunces, Fraunces Fallback, DM Sans, DM Sans Fallback
- Sizes: ['8px', '12px', '13px', '10px', '11px', '15px', '14px', '13.5px', '17px', '18px', '12.5px', 'clamp(1.875rem, 3.1vw, 2.75rem)', '16px', '16.5px']
- Weights: ['500', '400', '760', '800', '650', '700', '600', '300', 'inherit', 'bolder']

## Layout / component signals

- Landmarks: {'header': 1, 'nav': 3, 'main': 1, 'section': 12, 'article': 5, 'footer': 1}
- Headings: 39 · nav labels: 39 · CTA labels: 37
- Sections: 12 · forms: {'forms': 0, 'inputs': 2, 'labels': 0, 'required': 0} · images: {'total': 153, 'missing_alt': 64, 'lazy': 58, 'srcset': 0, 'svg': 127}
- Radius values: ['12px', '10px', '16px', '20px', '8px', '14px', '9px', '999px', 'inherit', '18px']
- Breakpoints: ['min-width 360px', 'max-width 360px', 'max-width 380px', 'max-width 400px', 'max-width 420px', 'max-width 430px', 'max-width 560px', 'max-width 620px', 'max-width 639px', 'max-width 640px']
- Motion declarations: 88 transition values

## Limits

- Static HTML/CSS only: JavaScript-rendered DOM, computed style, hover/focus states, and animations are not observed.
- CSS declaration frequency is not visual usage: unused framework/reset rules can dominate the palette.
- CSS cascade/layers are not resolved; `<style>` blocks and linked stylesheets are analyzed independently.
- Cross-origin iframes, shadow DOM, canvas/WebGL, video, and image contents are skipped.
- Robots.txt is respected for the page fetch; no crawl, no forms, no auth, no paywall bypass.
- No screenshot was taken and no browser was launched. Browser/vision tiers need explicit operator authorization.
- No logos, images, fonts, icons, or page copy should be reused; this evidence supports principles, not assets.

## Next action

`@ui-reference-intake dna - leadpages` — author the DNA from this evidence + optional operator screenshot; keep claims tagged `measured` / `estimated` / `assumption`.
