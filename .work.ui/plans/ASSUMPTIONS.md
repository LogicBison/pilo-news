# ASSUMPTIONS — UI planning registry

> Maintained by `ui-*` skills. Labels: **Confirmed** | **Inference** | **Unverified** | **Rejected**.

**Status:** Draft · **Updated:** 2026-11-05 · **Needs:** operator confirmation of UA1 and UA3.

| ID | Assumption | Label | Source | Notes |
|----|------------|-------|--------|-------|
| UA1 | Craft tier **refined** is the right bar for public channels; `premium` is not justified | Inference | `.work.ui/plans/foundation/20261105-01-ui-vision-and-principles.md` §Craft tier | existing surface/elevation layer supports it; costs a UIS-07 gate per milestone |
| UA2 | Example ids W2/W3/W6/W9 represent the target composition set | Inference | `/mnt/work/Projects/pilo.ai.ui.logicbison/examples/websites/manifest.md` | chosen from manifest text, not PNGs (text-only agent) |
| UA3 | The 14 operator reference sites map onto the 7 channels as the skin-refresh brief proposes | Unverified | `.work/plans/20261105-ui-skin-refresh.md:44-52` | binding only after each channel's screen SPEC is approved |
| UA4 | The real front-end stack is Next 15.1.8 + Tailwind 4.1.6, run through the `web` compose service | Confirmed | `apps/web/package.json:17,24,30` | `DOCS_UI_STACK.md` is still the unfilled template - fill it before the first SPEC cites it |
| UA5 | Channels ship light-only in v1 | Confirmed | `apps/web/src/app/globals.css:14` (`color-scheme: light`) | revisit via UU1 |
| UA6 | Channel character rides on 7 colour tokens + 2 font families + radius + layout variant | Confirmed | `apps/api/migrations/002_seed_industries.sql:8-40`, `apps/api/src/news_api/channels/domain/theme.py:63-98` | `behavioral-health` already tints its surface (`#faf5ff`) |

## Rejected

| ID | Assumption | Reason |
|----|------------|--------|
| UA7 | axe "0 critical/serious" means the UI is accessible | axe does not test WCAG 1.4.11; control borders measure 1.26-1.48:1 (foundation doc 02, UR1) |

## Next action

`@ui-design-foundation certify screen-spec-ready` — nothing here blocks the gate; UA1/UA3 confirm during the first SPEC review.
