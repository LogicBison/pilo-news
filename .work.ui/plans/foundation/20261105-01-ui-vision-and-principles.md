# System News — UI vision and principles

**What it is:** UI foundation doc 01 — what the product UI is for, who reads it, and the bar every screen is held to.
**Status:** Draft (2026-11-05) · **Needs:** operator confirmation of craft tier (§Craft tier) and of the dark-mode deferral (D2).

## Project classification

| Field | Value | Evidence |
|-------|-------|----------|
| **Archetype** | hybrid — public marketing/news sites (primary) + editorial admin console | `apps/web/src/app/[locale]/[industry]/page.tsx`, `apps/web/src/app/[locale]/admin/page.tsx` |
| **Complexity** | L — 7 channels × 2 locales × 7 page types + 1 console | `.work/plans/20261105-ui-skin-refresh.md:44-52`, route tree under `apps/web/src/app/[locale]` |
| **Style stack** | tailwind + CSS custom properties (`tailwindcss` 4.1.6, `@tailwindcss/postcss` 4.1.6) | `apps/web/src/app/globals.css:1`, `apps/web/package.json:24,30` |
| **Primary surfaces** | web responsive, mobile-first | `DOCS_UI_STACK.md` (template unfilled — see UA4) |

## Product UI intent

Founder intent, verbatim (P0 capture):

> Each news site/landing-page must be single-themed, and professionally suited (UI+UIX+SKIN+STYLING+CSS+LOOKS) for each specific industry
> English and Spanish must be supported, default language on entry is the system's (browser's/environment's) setting, but can be changed manually by the user on a click.

Current gap, verbatim from the skin-refresh brief: "current styling is one material-inspired system shared by all channels; the gap is per-industry character, not base quality" (`.work/plans/20261105-ui-skin-refresh.md:8-10`).

The UI exists to earn a lead: a professional lands from search or social, understands what matters in their field in under five minutes, and can ask for help without leaving the reading flow.

## Design principles

1. **One primary action per page.** Home, article, search, and about each carry exactly one lead CTA; a secondary action never competes visually. (SPEC R16, I7)
2. **Channel character through data, never forks.** Skins (`.work.ui/design-system/20261105-skin-system.md`) sit on top of the layout variants: composition, motif, corners, rules, and CTA shape per channel. Themes come from `industries.theme` plus three layout variants (`editorial`, `professional`, `academic`); no per-channel page tree. (SPEC R4/R5, `apps/api/src/news_api/channels/domain/theme.py:21`)
3. **Tokens or nothing.** Components consume semantic tokens; raw colour literals live only in the token file. Known violations to retire in the build milestone: `apps/web/src/app/globals.css:201`, `apps/web/src/app/globals.css:250`, `apps/web/src/components/Notices.tsx:9,45`.
4. **Reading comes first.** 16px body floor, ≤65ch article measure, summary above the fold, no interstitials, no sticky element covering prose.
5. **States are designed.** Every list has loading, empty, fallback, and error treatments; an API failure renders a degraded shell, never a blank page. (SPEC R10, `apps/web/src/components/Notices.tsx`)
6. **Accessible by construction.** WCAG 2.2 AA: visible 3px focus ring, 44px touch targets, 3:1 non-text contrast on control boundaries. Border-only inputs currently measure 1.35:1 and fail WCAG 1.4.11 (measured, §Craft tier).
7. **Trust is visible.** Source label, recency, and the channel disclaimer sit beside the CTA; consent is unchecked and versioned. (ADR 013, SPEC R18)

## Density and tone

| Attribute | Value |
|-----------|-------|
| Density | comfortable |
| Craft tier | **refined** (see below) |
| Motion | minimal — 160–320ms transitions, `prefers-reduced-motion` already honoured (`apps/web/src/app/globals.css:303-324`) |
| Brand voice in UI copy | answer-first, plain, lowercase-leaning; no hype, no urgency theatre. Banned words: "act now", "limited", "guaranteed", "risk-free", "unlock", "exclusive" (`.work.ui/design-system/20261105-CTA-BRIEF.md:38`) |

## Craft tier

**refined.** Reasons: customer-facing and lead-generating; a surface/elevation layer already exists (`apps/web/src/app/globals.css:104-192`); controls are still native with a styled shell (`globals.css:270-287`), which is exactly what refined forbids without a waiver.

Costs of refined: `--surface-*` tokens are mandatory in doc 02; catalog primitives are required for selects, toggles, and sliders on primary flows; `@ui-concept-run - UIS-07` is required at each milestone close (`.ai.ui/skills/SKILL_DEPENDENCIES.md:62`).

`premium` is not justified: no photography system, no icon set, no brand asset pack (`.ai.ui/inputs/brand/` is empty).

The editorial console (`apps/web/src/app/[locale]/admin`) runs at **utilitarian** tier — back-office, one operator. That mixed-tier exception is recorded here and must be restated in the console's screen SPEC.

## Out of scope (UI v1)

- Dark mode or `prefers-color-scheme` switching — `color-scheme: light` only (`globals.css:14`); deferred as UU1.
- Per-channel photography, illustration, or iconography — no asset inputs exist.
- Newsletter signup (Phase B in the industry-sites SPEC).
- A third content language (extension point only, `docs/customization.md` §3).
- Native apps (deferred U15).

## References

Example ids picked from `examples/INDEX.md` (playbook §Phase A, 2–4 ids):

| Id | Source | Extracted rule used here |
|----|--------|--------------------------|
| **W2** | `examples/websites/manifest.md` | Split hero, single clear H1 + one CTA, alternating section rhythm |
| **W3** | `examples/websites/manifest.md` | Feature/card grid below hero, tiered CTAs (primary vs ghost) |
| **W6** | `examples/websites/manifest.md` | Content grid: title + excerpt + date + category chip, pill filters, hover elevation |
| **W9** | `examples/websites/manifest.md` | Long-form reading: ≤65ch measure, sticky TOC, heading anchors |

Operator site references (14 URLs, lead-gen patterns) stay in `.work/plans/20261105-ui-skin-refresh.md:26-40` — they inform per-channel direction at screen-spec time, not the shared foundation.

## Decisions needed

1. **Craft tier = refined** — it adds catalog primitives and a UIS-07 gate at every milestone. Downgrading to utilitarian would cut the control work but leave the lead forms on native controls.
2. **Dark mode deferred** — confirm channels ship light-only in v1 (UU1).

## Open questions

1. Per-channel imagery: none planned; the skin refresh assumes type, colour, and composition carry the character. Confirm.
2. Per-channel font budgets: two families per theme is enforced (`theme.py:95-97`); custom webfonts would add a licensing decision nobody has made yet.
3. Console design: does the console get a screen SPEC at all in v1, or stay out of `.work.ui` scope?

## Next action

`@ui-design-foundation greenfield` — continue with foundation doc 02 (design tokens).
