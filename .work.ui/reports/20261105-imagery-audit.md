# Imagery audit — ten channel bands

**What it is:** verification of every channel image, the replacements for the three SVG bands, and the licence trail.
**Status:** Done (2026-11-05) — 10/10 channels carry a photograph; no unintelligible band remains.
**Needs:** nothing.

## 1. What was checked

Each channel home was rendered at 1280×900 and its hero band captured (`figure.sn-scene`). Article strips reuse the same file through `SkinScene variant="strip"`, so one check covers both placements.

| Channel | Before | Verdict | After |
|---------|--------|---------|-------|
| legal | photo, guildhall courtroom ceiling | pass — legible, on-topic | unchanged |
| financial | photo, NYSE facade | pass | unchanged |
| behavioral-health | photo, lake pier at sunset | pass | unchanged |
| education | photo, university library reading room | pass | unchanged |
| logistics | photo, container yard | pass | unchanged |
| cybersecurity | photo, data-centre racks | pass | unchanged |
| stem-cell | photo, pipette tip boxes | pass — legible lab context | unchanged |
| manufacturing | **SVG line-art** — factory silhouette, no photographic detail | fail — reads as an abstract gradient | photo, GM assembly line |
| energy | **SVG line-art** — three turbine glyphs, flat gradient | weak — recognisable but not realistic | photo, transmission lines at sunset |
| retail | **SVG line-art** — brown gradient with rectangles | fail — unintelligible (operator report) | photo, supermarket aisle |

## 2. Replacements

All three are Wikimedia Commons files, cropped to the 2.5:1 band (1600×640 and 800×320), JPEG q82, recorded in `apps/web/public/photos/credits.json`.

| Channel | File | Creator | Licence |
|---------|------|---------|---------|
| manufacturing | `002 Production line - car assembly line in General Motors Manufacturing Poland - Gliwice, Poland.jpg` | Marek Ślusarczyk | CC BY 3.0 |
| energy | `Transmission Lines at Sunset.jpg` | Kkiefuik | CC BY 4.0 |
| retail | `Coffee in K-citymarket Järvenpää.jpg` | Arkke | CC BY-SA 4.0 |

Attribution renders in-band through `skin.credit` (`apps/web/src/lib/skins.ts`), so the CC BY / BY-SA condition is satisfied without leaving the page.

## 3. Print and layout rules kept

- Band height 360 px at 1280 wide, 2.5:1 crop, so the caption scrim keeps its contrast budget.
- Caption text stays white on the skin scrim; axe reports no contrast violation on the three new bands.
- The old `band.svg` files for the three channels are left in place as the documented fallback but are no longer referenced by `skins.ts`; `SkinScene` still handles an SVG source if a future channel needs one.
- Decorative role unchanged: `alt=""`, `aria-hidden`, caption carries the meaning.

## 4. Evidence

| Check | Result |
|-------|--------|
| Band screenshots, 10 channels | 10/10 photographic, captions legible |
| `pnpm build` | pass |
| `pnpm lint` / `pnpm typecheck` | pass |
| `npx playwright test` (production build, :3100) | **57 passed, 1 skipped** |
| axe (WCAG 2.2 AA + best-practice) on 11 URLs incl. the three new bands | 0 violations |
| `credits.json` | 10 entries, one per channel, all with source + licence |

## Open questions

1. Photography is now the only art layer on all ten channels; do the SVG motifs and masthead emblems stay as the brand layer (current behaviour), or should the three new channels get bespoke emblems too?

## Next action

None — imagery is consistent; next UI work is content coverage, then S1 screens.
