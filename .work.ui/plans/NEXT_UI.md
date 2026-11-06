# NEXT_UI — UI planning backlog

> **Path:** `<repo-root>/.work.ui/plans/NEXT_UI.md` · **`@ui-component-build`** owns `## Current UI iteration`.

**Status:** UI v2 implemented and verified · direction **Approved** · **10/10 SPEC Review** · **visual verify pass with gaps** · **Needs:** approve the ten Review SPECs + `@ui-accessibility-audit milestone`

---

## Done (UI)

| Item | Artifact |
|------|----------|
| UI bootstrap | `.work.ui/` skeleton |
| CTA/lead-capture brief | `.work.ui/design-system/20261105-CTA-BRIEF.md` |
| UI foundation 01-04 | `.work.ui/plans/foundation/20261105-0{1..4}-*.md` |
| DTCG token source | `.work.ui/design-system/tokens.json` (74 tokens, schema-valid) |
| Lead-generation reference intake | `.work.ui/inputs/references/` — `ellevest`, `hubspot`, `leadpages` scanned; 3 DNA docs; Draft direction `editorial-conversion`; audit PASS |
| Editorial conversion v2 | Open hero, full-bleed proof/photo/conversion bands, 0–2 px corners, dark action panel, filled forms — `apps/web/src/app/skins.css` + components |
| Balanced coverage | CSS multi-column `column-fill: balance`; 2 columns (`grid2`/`magazine`); `stack` available but unused; grid3 retired |
| Layout regression check | `apps/web/e2e/layout.spec.ts` — 21 checks (overflow, CTA containment, column spread ≤ 260 px) |
| Form clarity | Filled bordered fields, 600-weight labels, required note + `*`, optional block as a control, visible textarea/select |
| Task-page cleanup | Search/about use a process sidebar instead of a duplicate compact CTA; article end uses an open lead block; all pages with a brief link render `#brief-signup` |
| Token gate | `token-lint` 48 files / 0 raw colour literals (`theme.ts` + `globals.css` exempt as token files) |
| Direction ratified | `editorial-conversion` Approved 2026-11-05; composition aliases applied to `tokens.json` (84 tokens, schema-valid) |
| Seven SPECs bound | §13/§11 + `Reference DNA (binding)` + `exampleIds: N/A` waiver; `SCREEN_REFERENCE_MAP.md` 7 rows; reference audit PASS |
| Impact read | `.work.ui/reports/20261105-editorial-conversion-impact.md` — reader/business/code meaning + unproven claims |
| All ten SPECs reviewed | 7 review findings fixed in each; §3/§4/§5/§8/§11/§12/§13 aligned to the v2 build; status `Review`; re-check PASS 10/10 |
| Three new channels | manufacturing, energy, retail full profiles + 5/4/4 sources + Forge/Grid/Market skins + 3 SPECs + 10-row reference map |
| Channel verification | 45/45 sources pass `verify-sources --industry all`; 57 e2e passed / 1 skipped; 80 pages 200 + no overflow; `pnpm check` 10/10 |
| Visual verify milestone | **pass with gaps**; 10 channels, 0 visual regressions; report + UIS-07/10 concept run |

---

## Blocked on owner (UI)

| # | Item | Notes |
|---|------|-------|
| - | (none) | |

---

## Recommended next

| Priority | Item | Notes |
|----------|------|-------|
| **0** | Approve the ten `Review` SPECs | Visual verify pass with gaps; approval is the operator's gate |
| **1** | `@ui-accessibility-audit milestone` | Dark cybersecurity first; axe is green, audit adds manual checks |
| **2** | `@ui-design-system init` | Clear the UIS-07 catalog gap; register P0 primitives |
| **3** | Content coverage for the new channels | manufacturing EN 10, retail ES 1; add EN feeds/broaden topics before launch |
| **4** | `@ui-component-build plan - S0/S1` | primitives + remaining screens (contact, about, admin) |

---

## Intake queue

> Free-text UI requests captured by `@ui-screen-spec intake - <sentence>`. Format: `- <YYYY-MM-DD> · <class> · "<sentence>" → <next command>`. Classes: local / cross-cutting / brownfield / underspecified.

- 2026-11-05 · cross-cutting · "too many boxes, too many rounded corners, forms confusing, columns unbalanced" → `editorial-conversion` v2 (done)

---

## Current UI iteration

**v2 conversion spine — complete; bind pending.** The channel-home and article conversion surfaces are rebuilt and verified. Remaining work is governance (direction ratification, token aliases, SPEC bind, milestone audit) and the non-public screens.

---

## Done this UI iteration

| ID | Description | Completed |
|----|-------------|-----------|
| U-01 | Reference intake: 3 lead-gen refs, DNA, Draft direction | 2026-11-05 |
| U-02 | Open editorial layout: no section cards, full-bleed bands, sharp corners | 2026-11-05 |
| U-03 | Balanced coverage via CSS multi-column + layout regression test | 2026-11-05 |
| U-04 | Per-channel CTA placement (banner/sidebar/inset/corner) and Campus 2-col hero | 2026-11-05 |
| U-05 | Form clarity: filled fields, required note, optional control, visible message | 2026-11-05 |
| U-06 | Production verification: build, 29/29 e2e, 56 pages no overflow, axe | 2026-11-05 |
| U-07 | Direction ratified + composition tokens applied | 2026-11-05 |
| U-08 | Seven SPECs bound + reference map + audit PASS | 2026-11-05 |
| U-09 | All ten channel SPECs reviewed, amended, re-check PASS → `Review` | 2026-11-05 |
| U-10 | Three channels added (manufacturing, energy, retail); skins + profiles + sources verified | 2026-11-05 |
| U-11 | Visual verify milestone pass with gaps + UIS-07/10 concept run | 2026-11-05 |

---

## Next action

Approve the ten `Review` SPECs, then run `@ui-accessibility-audit milestone`; initialize the CATALOG and close the new channels' content gaps before launch.
