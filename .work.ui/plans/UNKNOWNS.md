# UNKNOWNS — UI planning registry

**Status:** Draft · **Updated:** 2026-11-05 · **Needs:** owner answers for UU1, UU3, UU4.

| ID | Question / blocker | Blocks | Owner | Status |
|----|-------------------|--------|-------|--------|
| UU1 | Does any channel ship a dark scheme in v1? Today `color-scheme: light` only. | token set (every semantic pair would need a dark value), visual verify | owner | Open |
| UU2 | Move the channel theme wire format from 6-digit hex to OKLCH? Backend validation is hex-only (`theme.py:70-74`). | token projection rule in doc 02 | owner + eng | Open |
| UU3 | Per-channel photography, illustration, or licensed webfonts: in or out for v1? | hero composition, font tokens, page weight budget | owner | Open |
| UU4 | Is the editorial console (`.work/admin-console`) in `.work.ui` scope for v1, or does it stay utilitarian and outside? | screen map S5, whether a console SPEC is written | owner | Open |
| UU5 | Does `search` get pagination? No page param exists in the domain SPEC today. | search screen SPEC, `Pagination` primitive (P2) | owner | Open |
| UU6 | Is there budget for Storybook? Catalog documentation is `CATALOG.md` + play tests until then. | primitive documentation standard | owner | Open |

## Next action

`@ui-design-foundation certify screen-spec-ready` — none of these block the gate; UU1/UU3/UU4 shape the first screen SPEC.
