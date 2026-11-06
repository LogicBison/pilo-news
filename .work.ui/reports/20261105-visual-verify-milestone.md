# Visual verify — milestone (ten channels)

**What it is:** milestone visual/design-token verification for the ten channel homes and the editorial-conversion build.
**Status:** **Pass with gaps** — 2026-11-05 · **Needs:** operator approval of the ten `Review` SPECs; `@ui-accessibility-audit milestone`; CATALOG init.
**Craft standard:** `standards/20260523-SURFACE-AND-CONTROL-CRAFT.md` §7 · **Craft tier:** refined · **Archetype:** hybrid marketing shell.

## Checks

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | UI visual test | **pass** | production `pnpm build`; Playwright 57 passed / 1 skipped (public, layout, axe, admin) |
| 2 | Token contract | **pass** | `token-lint --tokens globals.css --tokens theme.ts apps/web/src` → 48 files, 0 raw literals |
| 3 | Token file + visual diff | **pass** | `tokens.json` 84 DTCG tokens, schema-valid; direction Approved; screenshots reviewed |
| 4 | Build / Storybook | **pass with gap** | Next build passes; Storybook is not configured in this repo (N/A) |
| 5 | UIS registry | **pass** | no `Applies=yes` + `pending`; UIS-07/10 moved to `done` |
| 6 | Craft / §13 compliance | **pass** | exampleIds N/A waiver; extractedRules reflected; native select waiver; flat grammar by SPEC; no BEFORE cite |
| 7 | UIS-07 | **done — ship_with_notes** | `.work.ui/reports/20261105-uis-07-10.md` |
| 7b | Reference fidelity | **pass** | direction Approved; token roles present; 3 rules spot-checked; no copied assets/copy; originality test; a11y inherited check |
| 7c | Effects / widgets | **N/A** | no Tier 2–3 motion or hand-rolled complex widget added |
| 8 | Vision tier | **not run** | opt-in; production e2e + operator-requested screenshots used for this pass |

## Craft compliance

- **SPECs checked:** 10 (`channel-home-legal`, `financial`, `behavioral-health`, `education`, `logistics`, `cybersecurity`, `stem-cell`, `manufacturing`, `energy`, `retail`)
- **§13 exampleIds:** ok — N/A waiver recorded in `HANDOFF_UI` (live-site references, not an `examples/` manifest)
- **Native control violations:** none — native `<select>` and P1 Skeleton/Notice have explicit `native allowed` waivers in §8
- **UIS-07:** done — ship_with_notes
- **Reference fidelity:** pass (`ellevest`, `hubspot`, `leadpages`; Approved direction)
- **Effects/widgets:** N/A

## Gaps and waivers

1. **CATALOG not initialized** — no catalog primitive is claimed `done`; §8 records the waiver; `@ui-design-system init` is P1.
2. **Native select + Skeleton/Notice** — explicit `native allowed` waivers until the P1 primitives ship.
3. **Storybook** — not configured; the build and Playwright/axe gates stand in for this repo.
4. **SPEC approval** — all ten SPECs are in `Review`; visual verify can run, but `@ui-component-build plan` still requires approval.
5. **Vision tier** — not run; browser/vision capture is opt-in. Existing production e2e + screenshots are the rendered evidence.

## Verdict

**Pass with gaps.** The visual grammar is consistent across all ten channels: square surfaces, no hero motif overlay, open action panels, balanced two-column coverage, readable filled forms, dark-scheme contrast fixed. The gaps are governance/CATALOG/Storybook, not visual regressions.

## Next action

Approve the ten `Review` SPECs, then `@ui-accessibility-audit milestone`; initialize the CATALOG before the design-system primitive work.
