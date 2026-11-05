# Skin system — per-channel design language

**What it is:** the mechanism that gives each of the seven channels its own visual identity without forking a page: a skin = composition + motif + surface grammar, resolved from the channel's slug.
**Status:** Approved (2026-11-05) — implemented for all 7 channels · **Needs:** nothing; per-channel screen SPECs refine copy only.
**Supersedes:** the informal "3 layout variants" assumption in foundation doc 01 §P2 — variants stay, skins sit on top.

## Why this exists

Before today every channel rendered the same page: same hero grid, same card, same app bar, same section rhythm — only 7 colours and 2 fonts differed (foundation doc 02 §Per-channel values). That is a palette swap, not a design.

A skin changes **structure and surface grammar**, not just colour:

| Dimension | What it controls | Example |
|-----------|------------------|---------|
| `hero` | composition of the first screen | split / ledger / poster / ribbon |
| `motif` | a generated SVG overlay behind hero and footer | arches, bars, rings, rules, routes, hexes, cells |
| `radius` | corner language | 2px (cyber) → 18px (health) |
| `rule` | section separator grammar | double / hairline / dotted / dashed / none |
| `eyebrow` | label treatment | letterspaced caps / mono ticks / numbered |
| `cta` | conversion panel shape | sidebar / banner / inset / corner block |
| `rail` | favourites strip behaviour | scroll-snap rail vs static grid |

Every channel gets a unique tuple. No two channels share a hero, a motif, and a radius at once. Adding a channel means choosing a tuple and drawing one motif — no page code changes.

## The seven skins

| Channel | Skin | Hero | Motif | Radius | Rule | Eyebrow | CTA panel | Reference basis |
|---------|------|------|-------|--------|------|---------|-----------|-----------------|
| legal | **Chambers** | split | arches | 6px | double | serif caps | sidebar | ellevest trust-first, nerdwallet disclosure |
| financial | **Terminal** | ledger | bars | 4px | hairline | mono ticks | banner | databox density, nerdwallet comparison |
| behavioral-health | **Sanctuary** | split | rings | 18px | none | soft caps | inset | ellevest calm, charitywater warmth |
| education | **Campus** | ribbon | rules | 10px | dotted | numbered | corner | hubspot segmentation, databox proof |
| logistics | **Network** | poster | routes | 8px | dashed | mono ticks | banner | basecamp plainness, calendly single job |
| cybersecurity | **Sentinel** | ledger | hexes | 2px | solid accent | mono ticks | sidebar | semrush data density, userpilot product-led |
| stem-cell | **Lab** | ribbon | cells | 14px | hairline | serif caps | inset | ellevest credibility, typeform form-first |

## Palettes and coverage rhythm

Each channel owns a colour scheme, not a tint of the same one. Contrast is gated per channel by `pnpm check` (5 pairs × 7 channels).

| Channel | Palette | Base | Primary | Accent | Coverage |
|---------|---------|------|---------|--------|----------|
| legal | ivory + burgundy | `#faf7f2` | `#5b2333` | `#a16207` | magazine (wide lead, then 2-up) |
| financial | cool white + navy | `#f7f9fb` | `#0f2f4f` | `#0e7490` | grid3 |
| behavioral-health | blush + plum | `#fdf7f5` | `#7c3f58` | `#b45309` | stack (single column, lead card accented) |
| education | parchment + forest | `#fbf8ef` | `#14532d` | `#b45309` | grid2 |
| logistics | mist + graphite green | `#f4f6f5` | `#1f3d33` | `#c2410c` | grid3 |
| cybersecurity | **dark** midnight + cyan | `#0b1220` | `#1e3a5f` | `#22d3ee` | grid2 |
| stem-cell | white + deep teal | `#ffffff` | `#0f4c5c` | `#9a3412` | magazine |

App bar: `split` for legal, financial, logistics, cybersecurity; `centered` for behavioral-health, education, stem-cell.

Design intent per channel:

- **Chambers** — an institution, not a blog. Serif headline, double rule under the hero, CTA in a margin column. Nothing urgent, nothing loud.
- **Terminal** — numbers first. Hairline grid, tabular figures, accent only as a marker on the active row. The CTA reads as a data request, not a sales pitch.
- **Sanctuary** — softness as a signal of safety: no hard rules, wide radius, rings that never close. CTA as an inset panel, low pressure.
- **Campus** — a course catalogue: ribbon header, numbered sections, dotted separators. CTA anchored in the corner of the hero block.
- **Network** — a dispatch board: poster hero, dashed route lines, mono labels, metric chips. CTA as a banner across the fold.
- **Sentinel** — an operations console: ledger layout, hex lattice, square corners, accent rail. CTA as a sidebar.
- **Lab** — a research brief: ribbon hero, cellular motifs, hairline rules, ethics note beside the CTA.

## Reference mapping (operator list)

| Reference | What was taken | Where it lands |
|-----------|----------------|----------------|
| userpilot | product-led hero + demo pairing | Sentinel hero, CTA sidebar |
| databox | dense proof above the fold | Terminal, Campus sections |
| hubspot | segmented CTA by intent | Campus hero ribbon |
| basecamp | plain-language single action | Network copy density |
| calendly | one job per page | Network poster hero |
| typeform | form-first conversion | Lab CTA panel |
| ellevest | trust-first copy for regulated audiences | Chambers, Sanctuary, Lab |
| nerdwallet | comparison clarity + disclosure placement | Terminal rules, legal disclaimer slot |
| monday | benefit-led cards | Campus card headers |
| leadpages | CTA repetition | Terminal banner, Network banner |
| charitywater | emotional proof + single CTA | Sanctuary inset |
| semrush | data-rich proof | Sentinel metric rail |
| mailchimp | tone-led voice | Network mono labels + plain lines |
| warbyparker | low-friction entry | Terminal two-field brief |

No third-party assets are copied and nothing is licensed in: motifs and scene illustrations are original vector art generated into this repo, so they are royalty-free by construction (project-owned, no attribution duty). Photography is still absent — there is no image-generation pipeline, and a licensed stock photo per channel would need a budget and a licence record.

## Implementation

| Layer | File | Role |
|-------|------|------|
| Registry | `apps/web/src/lib/skins.ts` | slug → skin tuple, typed, with a fallback for unknown channels |
| Motifs | `apps/web/public/skins/<slug>/motif.svg` | one generated line-art SVG per channel, used behind the hero card |
| Illustrations | `apps/web/public/skins/<slug>/scene.svg` | one original 1200×460 scene per channel, rendered as a caption band under the proof strip |
| Surface grammar | `apps/web/src/app/skins.css` | `[data-skin]` / `[data-hero]` rules; consumes channel tokens, never redefines colour |
| Wiring | `apps/web/src/app/[locale]/[industry]/layout.tsx` | sets `data-skin` + `data-hero` on the channel wrapper |
| Hooks | `Hero.tsx`, `CtaCard.tsx`, `Header.tsx`, `StoryCard.tsx` | stable class names (`sn-hero`, `sn-cta`, `sn-story`) the skin CSS targets |

Rules: skins consume `--sn-*` tokens only; a skin may change shape, spacing, borders, and which token is used, never invent a colour. Contrast gates still apply (`pnpm check`, 7 channels). No page forks, no per-channel components.

## Adding a channel

1. Pick a tuple that no existing channel uses (table above).
2. Draw one motif SVG (≤4 KB, `currentColor`-free, `#0f172a` stroke at 0.10–0.14 opacity + one accent shape).
3. Register it in `skins.ts` — unknown slugs fall back to the nearest layout variant, so a channel is never unstyled.

## Illustrations

Photography is the primary visual surface; line art is retained strategically for motifs, the masthead emblem, and as the no-photo fallback. Photos are cropped to 1600×640 (and 800×320) and served through `next/image`, so the band is one optimised request per breakpoint. Licences: CC0 / public domain where possible, CC BY-SA with an in-page attribution line where not — the record lives in `credits.json` and the credit renders inside the caption.

Each channel ships one `scene.svg` (columns for legal, skyline for financial, waves for health, an open book for education, containers for logistics, a circuit shield for cybersecurity, a petri dish for stem-cell). It renders in two placements:

| Placement | Variant | Size | Copy | Why |
|-----------|---------|------|------|-----|
| Channel home | `band` | 210–230px | channel name + tagline | identity moment before the reader scans content |
| Article page | `strip` | 118px (96px mobile) | channel name + quiet "More coverage →" link | closes the story with an identity beat and a path back, without competing with the headline or the CTA |

Article placement is deliberately **after** the related stories and **before** the CTA stack: illustration never sits above the headline, and never between the summary and the reading link. Contact and search pages get no illustration — those are task pages, and a decorative band there would push the form or results down for no gain.

## Verification

`pnpm lint`, `pnpm typecheck`, `pnpm check`, then screenshot each channel home and compare: hero, rule, radius, motif, CTA panel must differ on at least three dimensions between any two channels.

## Open questions

1. Once copy is rewritten per channel (per-channel screen SPECs), do titles need a per-skin type scale bump, or is one scale enough?
2. Photography: still absent by choice. If a channel later gets licensed imagery, it needs a SPEC and a performance budget.

## Next action

`@ui-screen-spec create - channel-home` — per-channel copy and hero composition on top of the skins.
