# Cybersecurity channel home — screen SPEC amendment 01

**What it is:** amendment to `20261105-SCREEN-SPEC.md` §9 for the `cybersecurity` channel home.
**Status:** Approved (2026-11-05) — operator approved the audit findings in full; amendment recorded, parent SPEC left untouched.
**Needs:** nothing.

## 1. Change

§9 previously read "Touch targets ≥44px" as a blanket rule.

Replaced with: "Touch targets: interactive controls (buttons, inputs, selects, textareas, chips) ≥44px high; text links ≥24px high and spaced so a 24px circle centred on the target does not intersect a neighbour."

## 2. Why

The a11y milestone audit (`.work.ui/reports/20261105-accessibility-audit-milestone.md`, finding F3) measured controls at 44–48px but header/footer and card text links at 20–24px. WCAG 2.2 AA 2.5.8 (target size, 24px minimum) is met — footer links carry 28px vertical gaps — while 2.5.5 (AAA, 44px) was never a realistic target for inline links on this screen.

## 3. Effect

No layout change and no code change; the SPEC now states what the build actually delivers. AA conformance is unchanged.

## Next action

None — parent SPEC §9 stands corrected by this amendment.
