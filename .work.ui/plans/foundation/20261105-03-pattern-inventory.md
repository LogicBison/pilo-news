# System News — Pattern inventory

**What it is:** UI foundation doc 03 — what UI already exists in the repo, what must be built, and which reference each new pattern follows.
**Status:** Draft (2026-11-05) · **Needs:** operator acceptance of the P0 primitive list (D1) before `@ui-design-system init`.

## Existing (in repo today)

`apps/web/src/components/` — 15 files, 941 lines total. Verdict per file; "reuse" means keep the API, "refactor" means keep the behaviour and rebuild the surface on tokens, "replace" means the file goes away.

| Pattern | Location | Reuse? | Note |
|---------|----------|--------|------|
| App bar + nav | `apps/web/src/components/Header.tsx` | refactor | becomes `AppBar` pattern; brandmark and nav-link come from tokens, not `.sn-*` classes |
| Footer | `apps/web/src/components/Footer.tsx` | refactor | disclaimer + privacy/terms/contact links stay content-driven |
| Channel hero | `apps/web/src/components/Hero.tsx` (116 lines) | refactor | needs named hero variants (split / typographic) from doc 01 references |
| Story card | `apps/web/src/components/StoryCard.tsx` | reuse | add source/recency `Badge`; hover elevation already tokenised |
| Topic rail | `apps/web/src/components/TopicRail.tsx` | refactor | needs scroll affordance (`.ai.ui/standards/20260523-UI-PATTERNS.md` § Navigation) |
| Desk brief | `apps/web/src/components/DeskBrief.tsx` | reuse | editorial summary block; typography only |
| CTA button + sticky bar | `apps/web/src/components/Cta.tsx` (96 lines) | refactor | split `StickyCta` into its own file; it reuses `--sn-bg` for a missing overlay token |
| CTA card | `apps/web/src/components/CtaCard.tsx` (50 lines) | refactor | variants `hero` \| `inline` \| `compact` from the CTA brief exist as a boolean today |
| Lead form | `apps/web/src/components/LeadForm.tsx` (195 lines) | refactor | extract field primitives, consent block, and states; honeypot stays invisible |
| Contact form | `apps/web/src/components/ContactForm.tsx` (100 lines) | refactor | stop duplicating field markup with `LeadForm` — share the primitives |
| Notices (degraded / empty / fallback) | `apps/web/src/components/Notices.tsx` | refactor | hardcoded `amber-*` / `blue-*` / `red-700` palette classes → `color.state.*` |
| Locale switch | `apps/web/src/components/LocaleSwitch.tsx` | reuse | keyboard path already present; verify focus order in SPEC |
| Search box | `apps/web/src/components/SearchBox.tsx` | refactor | becomes `SearchField` compound (label + input + submit) |
| JSON-LD / hydration marker | `apps/web/src/components/JsonLd.tsx`, `HydrationMarker.tsx` | reuse | no visual surface |
| Admin console | `apps/web/src/app/[locale]/admin/AdminConsole.tsx` | reuse | utilitarian tier; native `<select>` is an accepted waiver, restated in its SPEC |
| Route states | `apps/web/src/app/[locale]/[industry]/loading.tsx`, `error.tsx` | refactor | align to `Skeleton` + `Notice` patterns |
| Proof strip | `apps/web/src/components/ProofStrip.tsx` | keep | first build of R2 (verifiable facts from the bundle); becomes a primitive in S0 |
| Trust block | `apps/web/src/components/TrustBlock.tsx` | keep | R3 process + no-resale copy; absorbs the planned `TrustLine` |
| Brief capture | `apps/web/src/components/BriefSignup.tsx` | keep | R1 L2 rung (`kind=brief`); `ConsentField` extraction is S0 debt |

## Needed (net-new)

| Pattern | Tier | Priority | Screen(s) | Example id | Catalog primitive |
|---------|------|----------|-----------|------------|-------------------|
| `Button` (primary/ghost/quiet, 3 sizes) | primitive | P0 | all | W3 | Button |
| `Card` (surface.elevated + elevation.1) | primitive | P0 | all | W6 | Card |
| `Chip` (filter / label / topic) | primitive | P0 | home, article, search | W6 | Chip |
| `SectionHeader` (title + optional description) | primitive | P0 | home, about | — | SectionHeader |
| `TextField` | primitive | P0 | contact, lead, search | — | TextField |
| `TextArea` | primitive | P0 | contact, lead | — | TextArea |
| `Select` | primitive | P1 | lead (qualification), console | — | Select |
| `ConsentField` (unchecked, versioned text) | primitive | P0 | lead, contact | — | Checkbox |
| `FieldError` + form status (`aria-live`) | compound | P0 | lead, contact | — | FieldError |
| `TrustLine` (disclosure + response expectation) | primitive | P0 | lead card, article | — | TrustLine |
| `CtaCard` (hero/inline/compact) | pattern | P0 | home, article, search, about | W3 | CtaCard |
| `StickyCta` (mobile, dismissible, after 60% scroll) | pattern | P0 | all public, mobile | — | StickyCta |
| `StoryGrid` (1/2/3-column, hover elevation) | pattern | P0 | home, search | W6 | StoryGrid |
| `Skeleton` (home, article, search shapes) | compound | P1 | home, article, search | — | Skeleton |
| `Notice` (degraded / empty / fallback / error) | pattern | P1 | all | — | Notice |
| `Toc` (sticky, scroll-spy, ≤65ch measure) | compound | P1 | article | W9 | Toc |
| `ArticleBody` (lede + summary + prose rhythm) | pattern | P1 | article | W9 | ArticleBody |
| `AppBar` (sticky, blur fallback) | pattern | P1 | all | W2 | AppBar |
| `SearchField` (label + input + submit) | compound | P1 | all | W6 | SearchField |
| `Pagination` | compound | P2 | search | W6 | Pagination |

Example ids used: **W2, W3, W6, W9** (`examples/websites/manifest.md`). They cover the four compositions this product needs: split hero (W2), tiered CTA in a card grid (W3), content grid with filters (W6), long-form reading with TOC (W9).

## Duplication and debt to retire in S0

1. **Field markup duplicated** between `LeadForm.tsx` and `ContactForm.tsx` — both hand-roll label/input/error. One `TextField`/`TextArea` + `FieldError` pair replaces both.
2. **Two CTA entry points** (`CtaCard` narrow `compact` boolean) — the brief specifies three named variants; a boolean cannot express `hero`.
3. **Off-token colour** in `Notices.tsx` (amber/blue/red Tailwind palette) and in `globals.css:201,250` — these are the only places a channel theme cannot reach.
4. **No skeleton on article and search** — `loading.tsx` exists only for the channel layout; article and search render blank during fetch.
5. **Inline `<select>` for the qualification question** (`LeadForm.tsx`) — shipped in R4 to prove the flow; extract into the `Select` primitive in S0 rather than growing a second control style.

## Catalog

Detailed rows, props, and a11y notes: `.work.ui/design-system/CATALOG.md` — refreshed 2026-11-05 by `@ui-design-system init` (21 rows: shipped patterns + planned P0/P1/P2 primitives, token names, behavior source, APG pattern, states, a11y notes).

## Decisions needed

1. **P0 primitive list** — 12 patterns at P0 is the build floor for a certified skin; approving fewer means a channel ships without its CTA composition.

## Open questions

1. Search has no pagination today; does the search SPEC add it (P2 `Pagination`) or keep single-page results?
2. Does the console get a screen SPEC in v1, or stay outside `.work.ui` scope at utilitarian tier?
3. Storybook is not installed; catalog documentation lands in `CATALOG.md` + play tests only until someone budgets Storybook.

## Next action

`@ui-design-foundation greenfield` — continue with foundation doc 04 (screen map).
