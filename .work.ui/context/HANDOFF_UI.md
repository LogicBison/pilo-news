# HANDOFF_UI — UI design session boundary

> **Path:** `<repo-root>/.work.ui/context/HANDOFF_UI.md` · Maintained by **`ui-*` skills**. Session bookends: **`@session-control`** when `.ai/` is present (full repo); `.work.ui`-scoped session verbs (start / status / context / add / commit / close / push) via **`@ui-session`**.

**Status:** **screen-spec-ready: yes** (certified 2026-11-05, all seven channels) · **Needs:** `@ui-design-system init`, then the first channel SPEC.

## Session status

**Open:** 2026-11-05 - goal: per-channel UI skin refresh (foundation first)

**Updated:** 2026-11-05

**Closed:** -

**UI layer state:** Foundation written - vision/principles, tokens (DTCG + CSS map), pattern inventory, screen map. No screen SPECs, no catalog primitives yet.

**Recommended pick-up:** `.work.ui/plans/NEXT_UI.md`

**Lost or new?** Read `.ai.ui/START_HERE.md`

---

## UI readiness

| State | Value | Date |
|-------|-------|------|
| ui-foundation-complete | **yes** | 2026-11-05 |
| screen-spec-ready | **yes** - certified, coverage = 7 channels (incl. `stem-cell`) | 2026-11-05 |
| ui-implementation-ready | no - needs component build + verify | |

## Active UI milestone

- **Milestone:** S0 - catalog primitives (starts after certify; see `20261105-04-screen-map.md`)
- **NEXT_UI:** [.work.ui/plans/NEXT_UI.md](../plans/NEXT_UI.md)

---

## Foundation record (doc 01)

| Field | Value |
|-------|-------|
| Archetype | hybrid - public news/marketing sites + editorial console |
| Complexity | L (7 channels x 2 locales x 7 page types + console) |
| Style stack | tailwind 4.1.6 + CSS custom properties |
| Craft tier | **refined** (console = utilitarian, mixed-tier exception recorded) |
| Example ids | W2 (split hero), W3 (tiered CTA cards), W6 (content grid), W9 (long-form reading) |
| Token source | `.work.ui/design-system/tokens.json` (DTCG, 74 tokens, schema-valid) → `apps/web/src/app/globals.css` |

---

## Fresh start — first actions (UI)

1. **`@session-control start`** when `.ai/` is present.
2. Read **`.cursorrules`** (UI block or full UI template).
3. Read **this file** and `.work.ui/plans/NEXT_UI.md`.
4. If foundation missing: **`@ui-design-foundation greenfield`**.
5. Close with **`@session-control close`** (optional commit).

### Conditional reads

| If the task touches… | Read first |
|----------------------|------------|
| Tokens / theme | `.work.ui/plans/foundation/*-02-design-tokens.md` |
| Screen map | `.work.ui/plans/foundation/*-04-screen-map.md` |
| Building UI | Approved `.work.ui/screens/<slug>/*-SCREEN-SPEC.md` |
| API behaviour | `.work/features/<slug>/*-SPEC.md` (link only) |
| Stack / commands | `DOCS_UI_STACK.md` |
| Charts / data viz | Foundation doc 03, `resources/control-platforms.md`, SPEC §14 |

---

## Open owner actions (UI)

| # | Action | Blocks | Owner |
|---|--------|--------|-------|
| - | (none) | | |

---

## What this cycle produced (UI)

| Date | Session | Artifacts |
|------|---------|-----------|
| YYYY-MM-DD | bootstrap | `.work.ui/` skeleton |

---

## Repository UI state

- **Token file:** `apps/web/src/app/globals.css` (runtime CSS vars) · `.work.ui/design-system/tokens.json` (DTCG source)
- **Chart library:** none - no analytical screen exists
- **Catalog:** `.work.ui/design-system/CATALOG.md` (still scaffold - `@ui-design-system init` pending)
- **Last visual verify:** -
- **Last a11y audit:** -
- **ADR location:** `.work.ui/decisions/` (default)

---

## Cross-link (Agent OS)

Keep **### UI layer** in `.work/context/HANDOFF.md` in sync when milestones close.

---

## Next action

`@ui-design-foundation certify screen-spec-ready`

---

## Latest action (@ui-design-foundation)

**Date:** 2026-11-05
**Run:** `greenfield` then `certify screen-spec-ready`
**Executed:**
1. `.work.ui/plans/foundation/20261105-01-ui-vision-and-principles.md` - archetype hybrid, complexity L, craft tier **refined**, 7 principles
2. `.work.ui/plans/foundation/20261105-02-design-tokens.md` - token map, surface stack, 7-channel measured contrast, 1.4.11 border gap
3. `.work.ui/plans/foundation/20261105-03-pattern-inventory.md` - 15 existing components triaged, 20 patterns needed (12 at P0)
4. `.work.ui/plans/foundation/20261105-04-screen-map.md` - 8 screens, channel coverage fixed at 7, milestones S0-S5
5. `.work.ui/design-system/tokens.json` - 74 DTCG tokens, `token-schema-verify.sh` ok
6. **Certified screen-spec-ready** - gate evidence: 4/4 docs present, token file present (`apps/web/src/app/globals.css`), DTCG source validates, `pnpm check` green on 7 channels
**Blockers:** none
**Next recommended:** `@ui-design-system init` (bind tokens, register P0 primitives), then `@ui-screen-spec create - channel-home`

---

## Latest action (@ui-director)

**Date:** 2026-11-05
**Request:** "One of the main goals of this system is to get leads ... the call to action (professional and appropriate) must be embedded into the build."
**Classified bucket:** design-system + copy (cross-cutting)
**Executed:**
1. @ui-screen-spec intake -> classified **cross-cutting** (screen-spec-ready: no) -> foundation first
2. CTA/lead-capture component brief -> `.work.ui/design-system/20261105-CTA-BRIEF.md`
**Blockers:** `ui-foundation-complete: no`, `screen-spec-ready: no`; brief cannot be promoted to `.work.ui/screens/` yet
**Next recommended:** `@ui-design-foundation greenfield` (then promote the brief to a screen SPEC)

---

## Latest build (@x-director)

**Date:** 2026-11-05
**Request:** "implement all recommendations by biz-director"
**Executed (R1-R3 of `.work.biz/strategy/20261105-lead-magnet-recommendations.md`):**
1. `ProofStrip` - verifiable channel facts from the bundle (stories, languages, updated, no paywall/ads)
2. `TrustBlock` - three-step process + no-resale line, above the primary form
3. `BriefSignup` - L2 rung (`kind=brief`, name + email + consent), after the primary form so it never competes
4. Copy in `messages/{en,es}.json` (246 keys, parity checked); wired to channel home + article for all 7 channels
**Design debt for S0:** the three components use raw Tailwind utilities + `sn-*` classes, not catalog primitives; `ConsentField`, `TextField`, `Notice` extraction still pending. `LeadForm` now renders a native `<select>` for the channel qualification question (R4) — that is the `Select` primitive in disguise and must be extracted in S0.
**Not built (blocked):** R4 per-channel qualification field (needs channel CTA config migration), R5 gated asset (needs U8 email), R6 partner SLA loop (needs U18).
**Next recommended:** `@ui-design-system init`, then a screen SPEC that folds these three surfaces into the documented primitives.

---

## Latest build (@ui-director)

**Date:** 2026-11-05
**Request:** "real professional web design for each industry... no skin/ui/design should be the same as another industry's"
**Executed:**
1. `.work.ui/design-system/20261105-skin-system.md` - the skin system: 7 named skins, 7 dimensions, reference mapping
2. `apps/web/src/lib/skins.ts` - typed registry (slug -> skin), layout fallback for channels with no skin entry
3. `apps/web/public/skins/<slug>/motif.svg` - 7 generated line-art motifs (arches, bars, rings, rules, routes, hexes, cells)
3b. `apps/web/public/skins/<slug>/scene.svg` - 7 original illustration bands, captioned with the channel tagline (`SkinScene`)
4. `apps/web/src/app/skins.css` - `[data-skin]` / `[data-hero]` surface grammar: hero composition, app bar, eyebrow, section rule, story cards, CTA panel, footer, motif placement
5. Wiring: `[locale]/[industry]/layout.tsx` sets `data-skin` + `data-hero`; hooks in `Hero`, `CtaCard`, `StoryCard`; `skins.css` imported in the root layout; middleware now exempts `skins/`
**Evidence:** screenshots of all 7 homes (desktop) + 2 mobile; `pnpm lint`, `pnpm typecheck`, `pnpm check` green; 7/7 channels 200 with distinct `data-skin`
**Deferred:** photography/illustration beyond generated line-art - no image-generation pipeline exists; a channel that needs licensed imagery needs a SPEC + performance budget
**Next recommended:** `@ui-screen-spec create - channel-home` for per-channel copy and hero composition; then `@ui-visual-verify`
