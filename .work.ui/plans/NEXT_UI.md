# NEXT_UI — UI planning backlog

> **Path:** `<repo-root>/.work.ui/plans/NEXT_UI.md` · **`@ui-component-build`** owns `## Current UI iteration`.

**Status:** UI v2 implemented and verified · direction **Approved** · **11 channel SPECs Approved** · **visual verify pass with gaps** · **a11y milestone pass** · **S0 primitives shipped** · **S1 screens shipped** (contact, about, admin-console; 78 Playwright tests green on a production build) · **Needs:** P1 primitives, S4 SPECs

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
| Ten SPECs approved | operator approved all ten channel-home SPECs 2026-11-05; `Status: Approved` in each |
| Accessibility audit | `@ui-accessibility-audit milestone`: **pass**, 30 URLs, 0 critical/serious, 2 moderate best-practice findings; report `.work.ui/reports/20261105-accessibility-audit-milestone.md` |

---

## Blocked on owner (UI)

| # | Item | Notes |
|---|------|-------|
| - | (none) | |

---

## Recommended next

**New 2026-11-09:** `.work.ui/plans/20261109-brand-assets.md` — the Herald Fox logo on the apex
masthead/footer plus favicons on every host. Needs decision 1 (emblem + live text vs baked lockup).

| Priority | Item | Notes |
|----------|------|-------|
| **0** | P1 primitives | `Skeleton` (article/search blank states) and `Toc`; both are `planned` in the catalog and block nothing today |
| **1** | S4 screen SPECs | `search`, `privacy`, `terms`; `search` needs the pagination question answered first (screen-map open question 1) |
| **2** | S2 per-channel review pass | no new components; theme and copy check on the three S1 screens across all 11 channels |

---

## Intake queue

> Free-text UI requests captured by `@ui-screen-spec intake - <sentence>`. Format: `- <YYYY-MM-DD> · <class> · "<sentence>" → <next command>`. Classes: local / cross-cutting / brownfield / underspecified.

- 2026-11-05 · cross-cutting · "too many boxes, too many rounded corners, forms confusing, columns unbalanced" → `editorial-conversion` v2 (done)

---

## Current UI iteration

**S1 — contact, about, admin-console: complete (2026-11-06).** Three SPECs authored, reviewed, approved, implemented, and verified. The milestone closed with a production build and 78 Playwright tests passing, including the new layout, contact, about and admin cases.

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
| U-12 | Ten channel-home SPECs operator-approved (`Review` -> `Approved`) | 2026-11-05 |
| U-13 | Accessibility milestone audit: pass on 30 URLs; F1-F5 recorded | 2026-11-05 |
| U-14 | A11y F1/F2 fixed: footer `nav.footer` label, CTA `<aside>` -> `<section>`; re-scan 0 violations | 2026-11-05 |
| U-15 | F3 resolved: ten `20261105-SCREEN-SPEC-amendment-01.md` files (target-size wording) | 2026-11-05 |
| U-16 | CATALOG rebuilt from foundation doc 03: 21 rows, tokens, behavior sources, APG, states | 2026-11-05 |
| U-17 | S0 primitives shipped (10 files under `components/ui/`); forms/trust/topic surfaces refactored onto them; field errors wired via `aria-invalid` + `aria-describedby` | 2026-11-05 |
| U-18 | Imagery audit: all ten bands verified; retail, energy, manufacturing moved from SVG line-art to licensed photographs (credits recorded) | 2026-11-05 |
| U-19 | Admin console inputs gained `aria-label`s (a11y F5) | 2026-11-05 |
| S1-1 | `contact` screen: config-driven desk address, client validation, per-field errors, failure/429 states with the desk email, success panel with send-another, open rail | 2026-11-06 |
| S1-2 | `about` screen: 65ch measure, "rolling window" copy fix (the seven-day claim contradicted 30-day retention), brief suppressed wherever `cta.asset` is set | 2026-11-06 |
| S1-3 | `admin-console`: empty sign-in, session-check state, 401 return, APG tabs, no browser dialogs, two-step confirms, inline hide/pin, audit action filter, `SN_DEFAULT_INDUSTRY` workspace, labelled forms, scoped tables | 2026-11-06 |
| S1-4 | Verification: production build, 78 Playwright tests pass (0 skipped with credentials), axe 0 critical/serious | 2026-11-06 |

---

## Next action

`@ui-design-system plan` for the P1 primitives (`Skeleton`, `Toc`), or `@ui-screen-spec create - search` to open S4. Content coverage is now a refresh question, not a gap: every channel serves content in both locales (lowest: digital-technology ES 16).
