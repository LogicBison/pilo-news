# HANDOFF_UI — UI design session boundary

> **Path:** `<repo-root>/.work.ui/context/HANDOFF_UI.md` · Maintained by **`ui-*` skills**. Session bookends: **`@session-control`** when `.ai/` is present (full repo); `.work.ui`-scoped session verbs (start / status / context / add / commit / close / push) via **`@ui-session`**.

**Status:** UI v2 implemented and verified; direction **Approved**; **11 channel SPECs Approved**; **visual verify: pass with gaps**; **a11y milestone: pass**; **S0 primitives shipped**; **S1 screens shipped** (contact, about, admin-console; 78 Playwright green) · **Needs:** P1 primitives, S4 SPECs.

## Session status

**Closed:** 2026-11-06 - S1 screens shipped: contact, about and admin-console implemented from approved SPECs; production build + 80 Playwright tests green; axe 0 critical/serious on 21 URLs.

**Updated:** 2026-11-06

**UI layer state:** Foundation certified. Eleven skins live (photo bands on every channel); the conversion spine is open/editorial (full-bleed proof, photo, conversion bands; balanced 2-column coverage; filled fields). Eleven channel-home SPECs are `Approved`; the three S1 screens are `Implemented` (2026-11-06). S0 primitives shipped; P1 (`Skeleton`, `Toc`) remain planned.

**Recommended pick-up:** `.work.ui/plans/NEXT_UI.md`

**Lost or new?** Read `.ai.ui/START_HERE.md`

---

## UI readiness

| State | Value | Date |
|-------|-------|------|
| ui-foundation-complete | **yes** | 2026-11-05 |
| screen-spec-ready | **yes** - certified, coverage = 10 channels | 2026-11-05 |
| ui-implementation-ready | **yes (v2 conversion spine)** - build + e2e verified | 2026-11-05 |
| direction-bound | **yes** - `editorial-conversion` Approved; 10/10 SPECs §13/§11 + reference map | 2026-11-05 |
| spec-review | **10/10 Approved** - all channel SPECs amended, re-checked, operator-approved | 2026-11-05 |
| visual-verify | **pass with gaps** - 10 channels, 0 visual regressions; gaps: CATALOG, Storybook, vision tier | 2026-11-05 |
| accessibility-audit | **pass** - 30 URLs, 0 critical/serious; F1/F2 fixed 2026-11-05, re-scan 0 violations | 2026-11-05 |
| catalog | **S0 shipped** - 10 primitives built under `components/ui/`, 21 catalog rows, forms refactored onto them | 2026-11-05 |
| s1-screens | **implemented** - contact, about, admin-console built from approved SPECs; 78 Playwright pass | 2026-11-06 |
| imagery | **pass** - 10/10 photographic bands; retail/energy/manufacturing replaced SVG line-art; credits recorded | 2026-11-05 |

## Active UI milestone

- **Milestone:** S1 - contact, about, admin-console: **complete 2026-11-06**. Next: P1 primitives (`Skeleton`, `Toc`) or S4 SPECs (`search`, `privacy`, `terms`).
- **NEXT_UI:** [.work.ui/plans/NEXT_UI.md](../plans/NEXT_UI.md)

---

## Foundation record (doc 01)

| Field | Value |
|-------|-------|
| Archetype | hybrid - public news/marketing sites + editorial console |
| Complexity | L (10 channels x 2 locales x 7 page types + console) |
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
3b. `apps/web/public/skins/<slug>/scene.svg` - 7 original illustrations in two placements: `band` on channel home (tagline) and `strip` on article pages (quiet back-link), both via `SkinScene`
4. `apps/web/src/app/skins.css` - `[data-skin]` / `[data-hero]` surface grammar: hero composition, app bar, eyebrow, section rule, story cards, CTA panel, footer, motif placement
5. Wiring: `[locale]/[industry]/layout.tsx` sets `data-skin` + `data-hero`; hooks in `Hero`, `CtaCard`, `StoryCard`; `skins.css` imported in the root layout; middleware now exempts `skins/`
**Evidence:** screenshots of all 7 homes (desktop) + 2 mobile; `pnpm lint`, `pnpm typecheck`, `pnpm check` green; 7/7 channels 200 with distinct `data-skin`
**Deferred:** photography/illustration beyond generated line-art - no image-generation pipeline exists; a channel that needs licensed imagery needs a SPEC + performance budget
**Next recommended:** `@ui-screen-spec create - channel-home` for per-channel copy and hero composition; then `@ui-visual-verify`


---

## Latest build (@ui-screen-spec)

**Date:** 2026-11-05
**Request:** "implement awesome webdesign an art customized for each channel/industry/subject"
**Executed:**
1. Seven channel-home SPECs: `.work.ui/screens/channel-home-<slug>/20261105-SCREEN-SPEC.md` (13 sections each, per-channel art direction, palette, tone, acceptance)
2. `apps/web/src/components/SkinEmblem.tsx` - seven inline line-art masthead marks (scales, trend bars, open arcs, book, routed nodes, shield, cell), inheriting `currentColor`
3. `Header` + `Footer` now render the channel emblem instead of a letter tile; brandmark shape/radius stays skin-specific
**Checks:** `pnpm lint`, `pnpm typecheck`, `pnpm check` green; masthead sheet captured for all 7 channels
**Next recommended:** `@ui-screen-spec review - channel-home-legal`, then `@ui-visual-verify milestone`


---

## Latest build (@x-director) — realistic imagery

**Date:** 2026-11-05
**Request:** replace line-art with realistic colour imagery; keep line art strategic; professional layout
**Executed:**
1. `apps/web/public/photos/<slug>/band.jpg` + 800w crops — one licensed photo per channel, cropped 1600x640, served through `next/image` (fill + sizes)
2. `apps/web/public/photos/credits.json` — title, creator, licence, source per photo; CC BY-SA channels render an in-caption credit link
3. `SkinScene` now renders photography for band and article strip; `scene.svg` retained as fallback; motifs + `SkinEmblem` stay line-art as the brand layer
4. `apps/web/src/middleware.ts` — `photos/` exempted from the locale rewrite (same class of bug as `skins/`)
**Known gap:** the image cache must be cleared when a photo file is replaced in place (`rm -rf .next/cache/images`); filenames are not content-hashed.
**Next recommended:** `@ui-visual-verify milestone`, then per-channel SPEC review.


---

## Latest build (@x-director) — distinct palettes and layouts

**Date:** 2026-11-05
**Request:** different colour schemes and layouts per channel
**Executed:**
1. Migration `009_distinct_channel_palettes.sql` — 7 palettes (ivory/burgundy, cool-white/navy, blush/plum, parchment/forest, mist/graphite, **dark** midnight/cyan, white/teal); profiles synced
2. `skins.ts` gains `list` (grid3 / grid2 / stack / magazine) and `bar` (split / centered); layout exposes `data-list` / `data-bar`
3. `skins.css` — coverage rhythms, centered app bar for three channels, dark-scheme handling for cybersecurity
4. SPECs updated with each channel's palette
**Checks:** migration applied and idempotent; `pnpm check` = 7 channels pass contrast; `pnpm lint` / `typecheck` green
**Note:** the web container lost Playwright's system libraries mid-session; reinstalled `libglib` etc. to keep screenshot verification working (container-only, not a repo change).

---

## Latest build (@x-director) — editorial conversion v2

**Date:** 2026-11-05
**Request:** "the current web UI design is pretty lame and dull... too many boxes, too many rounded corners... the forms are confusing... the left column is double the height from the column on the right"
**Executed:**
1. **Reference intake:** scanned `ellevest`, `hubspot`, `leadpages`; DNA docs + references registry + Draft direction `.work.ui/inputs/references/directions/editorial-conversion.md`. Audit PASS.
2. **Open editorial layout:** removed the hero card and page-section cards; full-bleed proof, photo and conversion bands; 0–2 px corners on marketing surfaces; display H1; action panel with promise row; photo scrim + credit lockup.
3. **Balanced coverage:** replaced per-column DOM with CSS multi-column `column-fill: balance`; `grid2`/`magazine` 2 columns, `stack` 1; `grid3` retired for the current seven (3 columns left a 288–408 px ragged bottom). Added `apps/web/e2e/layout.spec.ts` (21 checks: overflow, CTA containment, column spread ≤ 260 px).
4. **Per-channel placement:** Lab/Network full-bleed banner; Legal/Financial/Sentinel sidebar/banner; Sanctuary inset; Campus 2-column hero so the corner CTA is balanced. Search page uses a process sidebar instead of a duplicate compact CTA.
5. **Form clarity:** filled, bordered fields (not underline-only), 600-weight labels, `*` + "Fields marked * are required", optional block as a bordered control, message visible and marked optional, 3 px focus ring, filled textarea/select.
**Checks:** production build green; Playwright 29 passed / 1 skipped (public, accessibility, admin, layout); 56 channel pages × desktop/mobile = 200 + zero horizontal overflow; `pnpm lint`, `typecheck`, `check` green (268 keys, 7 themes); token-lint 48 files / 0 raw literals.
**Follow-up:** direction Approved; aliases applied; all seven SPECs bound. Remaining: SPEC review + milestone visual/a11y audit.
**Next recommended:** `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`; then `@ui-screen-spec review` the seven bound SPECs.

---

## Bind (@ui-reference-intake) — editorial-conversion

**Date:** 2026-11-05
**Request:** operator approved "1." ratify the direction and "2." bind the seven SPECs + apply the composition aliases.
**Executed:**
1. Direction `editorial-conversion` marked **Approved (2026-11-05)**.
2. Applied composition tokens to `.work.ui/design-system/tokens.json`: `component.action.*`, `component.band`, `component.lift`, `component.field.*`, `color.shade`; schema-valid **84 tokens**.
3. Bound all seven channel-home SPECs — §13 `exampleIds: N/A` waiver, `referenceIds`/`direction`/`doNotCopy`/`originalityCheck`/`accessibility` rows, `### Reference DNA (binding)` block, §11 acceptance bullet, de-exampled `regionMap`.
4. Created `.work.ui/inputs/references/SCREEN_REFERENCE_MAP.md` with seven Approved rows.
**Checks:** `reference-scan.py audit` PASS (0 problems); `token-schema-verify.sh` 84 tokens valid; `token-lint` 0 raw literals; build/e2e unchanged (29 passed / 1 skipped; layout 21/21).
**N/A waiver:** the screens are driven by live-site references, not an `examples/` manifest; `exampleIds: N/A` in all seven SPECs is deliberate and recorded here.
**Impact read:** `.work.ui/reports/20261105-editorial-conversion-impact.md` — what the change means for readers, the business, the codebase and what remains unproven.
**Next recommended:** `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`, then `@ui-screen-spec review` the seven bound SPECs.

---

## Amendment (@ui-screen-spec) — channel-home-legal

**Date:** 2026-11-05
**Request:** amend after the review failed on SPEC-vs-build mismatches.
**Fixed:**
1. §3 — added success + permission-denied (N/A) states; loading copy now matches the open layout.
2. §4 — coverage is balanced 2-column, not 3-up; proof/photo/conversion are full-bleed; open blocks and skin placement documented.
3. §5 — form fields updated (name/email/matter type/consent, Add details, Additional details; brief fields).
4. §8 — component statuses match the v2 build; explicit `native allowed` waivers for native select and the P1 Skeleton/Notice; CATALOG-init waiver recorded.
5. §11 — replaced the stale Portico/hero-card bullet with v2 acceptance (open hero, proof/photo bands, balanced columns, filled fields, no duplicate task-page CTA, layout gate).
6. §12 — UIS-10 corrected to **yes / pending** (marketing shell with photography), not “no photography”.
7. §13 — added the standard `### extractedRules (binding)` heading; Reference DNA block retained.
**Review:** re-checked — required sections 1–13, §12 registry, §13 shape, §11 extractedRules, N/A waiver, catalog waiver, one Next action: **PASS**.
**Status:** `Draft` → `Review`; approval is still the operator’s.
**Next recommended:** approve `channel-home-legal`, then `@ui-screen-spec review` the other six bound SPECs; run the milestone visual/a11y audit.

---

## Review all channels (@ui-screen-spec)

**Date:** 2026-11-05
**Request:** run `@ui-screen-spec review` for all channels.
**Result:** **7/7 PASS**; all statuses `Review`.
**Amended in the six remaining SPECs (same seven classes as legal):**
1. §3 — success + permission-denied (N/A) states; loading copy matches the open layout.
2. §4 — balanced 2-column coverage, full-bleed proof/photo/conversion, open blocks; per-channel CTA placement.
3. §5 — form fields (name/email/qualification/consent, Add details, Additional details; brief fields).
4. §8 — v2 component statuses; `native allowed` waivers for select + P1 skeleton/notice; CATALOG-init waiver.
5. §11 — v2 acceptance: open hero, proof/photo bands, balanced columns, filled fields, no duplicate task-page CTA, layout gate.
6. §12 — UIS-10 corrected to **yes / pending**; UIS-07 remains pending at milestone.
7. §13 — `### extractedRules (binding)` heading; Reference DNA block retained.
**Checks:** required sections 1–13, §12 registry, §13 shape, §11 extractedRules, N/A + catalog waivers, one Next action — pass on all seven. No code changed.
**Next recommended:** approve the seven `Review` SPECs; then `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone`.

---

## Channel expansion (@x-director) — manufacturing, energy, retail

**Date:** 2026-11-05
**Request:** add three additional channels (operator selected full live: manufacturing, energy & utilities, retail & e-commerce).
**Executed:**
1. Profiles `apps/api/config/deployments/manufacturing.json`, `energy.json`, `retail.json` — theme, EN/ES copy, disclaimers, CTA + qualification, 5 topics, 4–5 sources, partner.
2. Applied to the running dev stack (idempotent; re-run reports 0 created/updated). **45/45 sources pass** `verify-sources --industry all`; 10 industries, 0 failures, 0 coverage warnings.
3. New skins **Forge** (poster, gear), **Grid** (ledger, pylon), **Market** (split, tag) — `skins.ts`, motifs + original SVG scene bands, `SkinScene` unoptimized SVG support, emblems, CSS skin grammar.
4. Three channel-home SPECs copied from the bound direction, reviewed to `Review`; `SCREEN_REFERENCE_MAP` now 10 rows.
5. Verification: production build; Playwright **57 passed / 1 skipped** (layout 40/40, axe 11/11, public/admin); 80 channel pages desktop+mobile 200 + zero overflow; `pnpm check` 10/10 contrast; token-lint 0 raw.
**Known content gap:** manufacturing EN 10 / ES 41, energy EN 16 / ES 39, retail EN 10 / ES 1. The English thinness is a source/scoring issue; add EN feeds or broaden topics before launch. New channels use original SVG bands, not licensed photos.
**Next recommended:** approve the ten `Review` SPECs; run the milestone visual/a11y audit; apply the three profiles to prd when the deploy lane opens.

---

## Visual fix — Sanctuary CTA, box removal, dark-scheme links

**Date:** 2026-11-05
**Request:** "behavioral-health: fix the spacing issues and the color scheme making the text almost unreadable… remove the box borders and the corner-rounding."
**Changed:**
1. Sanctuary CTA is an **open column** (accent left rule, transparent background) — no pale-on-white contrast bug, no box, no empty stretched panel. `CtaPanel` gains `open`.
2. Removed the skin-level box overrides that re-added **22 px hero radius + shadow** and **18 px story radius + shadow**; `[data-skin]` selectors now enforce 0 radius / no shadow / no side borders.
3. Proof and conversion bands are borderless full-width tints; hero/story/proof/conversion no longer read as cards.
4. Behavioral-health coverage changed `stack` → `magazine` (two balanced columns instead of a narrow single column with a large empty side).
5. Dark-scheme contrast: story "Read more" and scene links use the accent; Sentinel eyebrows use the accent. Axe now passes on all ten channels.
**Checks:** production build; **57 e2e passed / 1 skipped** (layout 40/40, axe 11/11); 80 pages desktop+mobile 200 + zero overflow; `pnpm check` 10/10; token-lint 0; inventory check pass.
**Docs:** skin system (Sanctuary open column, magazine coverage), behavioural-health SPEC + canonical CTA list, direction wording.

---

## Visual invariant — square surfaces, no hero motif

**Date:** 2026-11-05
**Request:** "get rid of the round-corners… this drawing is weird, just remove it."
**Changed:**
1. Photo band, hero card, story items, proof band, conversion band, brief band, action panel and cards are forced to `border-radius: 0 !important` under `[data-skin]`; a skin rule can no longer re-introduce a radius.
2. The per-skin hero motif overlay (`.sn-hero-card::after`) is disabled globally; the photo/illustration band and masthead emblem remain.
3. Added regression checks in `apps/web/e2e/layout.spec.ts`: every channel's surfaces compute `0px` radius and the hero `::after` computes `display:none`.
**Checks:** production build/e2e pass after this change; 57 e2e / 1 skipped; axe 11/11; 80 pages zero overflow; inventory check pass.

---

## Visual verify — milestone (@ui-visual-verify)

**Date:** 2026-11-05
**Verdict:** **pass with gaps** (`10` channel homes).
**Report:** `.work.ui/reports/20261105-visual-verify-milestone.md`
**Concept run:** `.work.ui/reports/20261105-uis-07-10.md` — UIS-07 done / ship_with_notes; UIS-10 done / ship.
**Checks:** production build; Playwright 57 passed / 1 skipped; token-lint 0 raw; 84 DTCG tokens; no `Applies=yes` + `pending`; §13 exampleIds N/A waiver; extractedRules reflected; native-select/Skeleton waivers; reference fidelity pass; effects N/A.
**Gaps/waivers:** CATALOG init (P1), native select/Skeleton/Notice waivers, Storybook not configured (N/A), vision tier not run (opt-in), ten SPECs still `Review`.
**Next recommended:** approve the ten `Review` SPECs; `@ui-accessibility-audit milestone`; then CATALOG init.

---

## SPEC approval - 2026-11-05 (@ui-screen-spec)

**Action:** operator approved all ten channel-home SPECs in one message.
**Paths:** `.work.ui/screens/channel-home-<slug>/20261105-SCREEN-SPEC.md` - behavioral-health, cybersecurity, education, energy, financial, legal, logistics, manufacturing, retail, stem-cell.
**Header change:** `Status: Review` -> `Approved (2026-11-05)`; `Needs` -> `@ui-accessibility-audit milestone`; `## Next action` rewritten to the same command.
**Unchanged:** sections 1-13 (layout, content, acceptance criteria, UIS registry, references) - approval changed status only.
**Next recommended:** `@ui-accessibility-audit milestone` (dark cybersecurity first), then `@ui-design-system init` to clear the UIS-07 catalog gap.

---

## Accessibility audit - milestone 2026-11-05 (@ui-accessibility-audit)

**Verdict:** **pass** - 0 critical, 0 serious, 0 WCAG A/AA failures across 30 URLs; no waivers required.
**Report:** `.work.ui/reports/20261105-accessibility-audit-milestone.md`
**Tool:** axe-core 4.10.1 via `@axe-core/playwright` in the `web` container, tags wcag2a/2aa/21a/21aa/22a/22aa + best-practice; DOM, keyboard, reflow, and contrast checks in the same run.
**Findings:** F1 duplicate `nav.menu` label on header + footer nav (29 pages) - `Header.tsx:41`, `Footer.tsx:28`; F2 CTA `<aside>` nested in `<section>` (20 pages) - `CtaCard.tsx:26`; F3 SPEC §9 44px target claim vs 20px text links (AA 2.5.8 met by spacing); F4 form errors lack `aria-invalid`/`aria-describedby`; F5 admin placeholder-labels (out of scope).
**Evidence:** skip link first tab 10/10, ring = channel accent and 4.61-10.36:1 vs bg, reflow clean at 320px, reduced motion honoured, one `h1` and no heading skips on 30/30, `pnpm test:a11y` 10 passed + 1 flaky (hydration timeout, retry pass), `pnpm check` 10/10 contrast.
**Gaps:** no AT/screen-reader pass, no forced-colors or 400% zoom, keyboard walk sampled on 3 pages, audit ran on `next dev` not a production build.
**Next recommended:** `@ui-design-system init`; decide on F1/F2 before the next component-build pass.

---

## A11y fixes + CATALOG init - 2026-11-05

**A11y F1:** footer `nav` label moved from `nav.menu` to a new `nav.footer` key (`en` "Site links", `es` "Enlaces del sitio") - `apps/web/src/components/Footer.tsx:28`, `apps/web/src/messages/{en,es}.json`. Catalog parity 269 keys.
**A11y F2:** CTA panel `<aside>` -> `<section aria-label>` - `apps/web/src/components/CtaCard.tsx:26`. No CSS targeted the `aside` element; only `.sn-cta` / `.sn-action` classes.
**F3:** ten `20261105-SCREEN-SPEC-amendment-01.md` files record the target-size wording change (controls 44px, text links 24px + spacing); parent SPECs untouched per the amendment rule.
**F4/F5:** recorded as debt (form error wiring, admin placeholder labels); not fixed this pass.
**Verification (production build, `next start` on :3100):** `npx playwright test` **57 passed / 1 skipped**; axe re-scan with `best-practice` on 8 pages (EN/ES, contact, article) -> 0 violations; nav labels `["Menu","Site links"]` / `["Menú","Enlaces del sitio"]`; `pnpm lint`, `pnpm typecheck`, `pnpm check` (269 keys, 10/10 contrast), `pnpm build` pass. Running the suite against `next dev` instead produced hydration timeouts and layout flakiness - build first, always.
**CATALOG:** `.work.ui/design-system/CATALOG.md` rebuilt from foundation doc 03 - 21 rows, DTCG token names, behavior sources (native controls; Radix only with an APG justification), APG pattern per row, states, a11y notes; shipped-surface map added.

---

## S0 primitives + imagery - 2026-11-05 (@ui-component-build)

**Primitives shipped:** `apps/web/src/components/ui/` - `button`, `card`, `chip` (+`ChipLink`), `section-header`, `text-field`, `text-area`, `select-field`, `consent-field`, `field-error`, `trust-line`.
**Refactors:** `LeadForm`, `ContactForm`, `BriefSignup` now use the field set (duplicated markup retired); `TrustBlock` uses `Card` + `SectionHeader` + `Chip`; `TopicRail` uses `ChipLink`; `Notices` lost its off-token amber/blue palette and uses theme tokens; `LeadForm` success state uses `Card` + `Chip` + `TrustLine`.
**A11y F4:** `TextField`/`TextArea`/`SelectField` wire `aria-invalid` + `aria-describedby` to an optional `error`, so a field-level message is announced with the field; the forms still surface server errors through `FieldError`'s polite live region.
**Imagery:** retail, energy and manufacturing bands replaced with licensed photographs; `credits.json` has 10 entries; report `.work.ui/reports/20261105-imagery-audit.md`.
**Verification (production build, `next start` :3100):** `pnpm build` pass; `npx playwright test` **57 passed / 1 skipped**; axe on 11 URLs incl. the three new bands -> 0 violations; `pnpm lint` / `pnpm typecheck` / `pnpm check` (269 keys, 10/10 contrast) pass.
**Known gaps:** Storybook still absent (waiver recorded); `Skeleton`/`Toc` (P1) unbuilt; admin placeholder labels (F5) open.

---

## Admin Offers tab - 2026-11-06 (@x-director)

**Scope:** `.work.ui/screens/admin-console/20261106-SCREEN-SPEC-amendment-02.md`.
**Shipped:** Offers tab between Channels and Sources: issue list, row count, status, generated time, expandable detail with sourced rows and source version, and a `Build now` action. No publish or email control.
**Copy:** EN/ES added (380 catalog keys); the intro states drafts only.
**Verification:** `pnpm lint`, `pnpm typecheck`, `pnpm check` (380 keys, 11/11 contrast), `pnpm build`; Playwright `admin.spec.ts` 5/5 on the dev server, including the new Offers test.
**Gap:** the tab has no public counterpart and no publish gate.


---

## Public reference pages + publish gate - 2026-11-06 (@x-director)

**Scope:** `.work.ui/screens/reference/20261106-SCREEN-SPEC.md`; `.work.ui/screens/admin-console/20261106-SCREEN-SPEC-amendment-02.md`.
**Shipped:** reader-facing archive at `/{locale}/{industry}/references` and detail at `/{locale}/{industry}/references/{date}`; only published issues. The channel asset card switches from waitlist to "Read the latest issue" when an issue is published. Admin Offers tab gains reviewer-gated Publish and two-step Unpublish. ES shows English content with a notice and `noindex`.
**Verification:** `pnpm lint`, `pnpm typecheck`, `pnpm check` (408 keys, 11/11 contrast), `pnpm build`; Playwright admin 6/6; public 13/14 with one known navigation flake that passes in isolation; axe 23/23 public URLs, plus archive EN/ES and published detail.
**Gap:** no email delivery; no cross-issue search; ES content remains English.
