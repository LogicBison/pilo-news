# RISK_REGISTRY — UI planning registry

**Status:** Draft · **Updated:** 2026-11-05 · **Needs:** nothing - reviewed at each UI milestone close.

Risk status: **Open** | **Mitigated** | **Accepted** | **Closed**

| ID | Risk | Category | Likelihood | Impact | Mitigation | Status | Owner |
|----|------|----------|------------|--------|------------|--------|-------|
| UR1 | Control borders fail WCAG 1.4.11: measured 1.26-1.48:1 vs a 3:1 floor, and axe does not catch it | accessibility | H | H | `color.border.strong` token (`#77808f`, 3.59-3.99:1) + control rows in every screen SPEC; add a 1.4.11 check to `pnpm check` | Open | ui |
| UR2 | Token drift between `.work.ui/design-system/tokens.json` and the DB JSONB channel themes | design-system | M | M | boundary rule in foundation doc 02; `pnpm check` gates channel contrast; no channel colours in `tokens.json` | Open | ui |
| UR3 | Seven channels, one component set: per-channel QA cost balloons at S3 | delivery | M | H | S1 pilot first; later channels change tokens/copy/variant only; no per-channel page forks | Open | ui |
| UR4 | Off-token colour in `Notices.tsx` and `globals.css:201,250` cannot follow a channel theme | design | H | M | S0 replaces them with `color.state.*` tokens | Open | ui |
| UR5 | Refined tier adds a UIS-07 concept gate to every milestone close | process | H | M | planned into S0-S5; accepted cost of the tier | Accepted | ui |
| UR6 | Base/elevated split (`#fbfbfd` vs `#ffffff`, 1.03:1) may be invisible on low-contrast displays | design | M | L | borders carry separation; confirm in `@ui-visual-verify` before S1 closes | Open | ui |

## Next action

`@ui-design-foundation certify screen-spec-ready` — UR1 and UR4 land in S0, not in the gate.
