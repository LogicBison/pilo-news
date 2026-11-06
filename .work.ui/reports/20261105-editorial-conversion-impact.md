# Editorial conversion v2 — what this change means

**What it is:** a plain-language read of the UI/UX change approved on 2026-11-05 — what moved, what it is designed to do, and what is still unproven.
**Status:** Implemented + verified 2026-11-05 (ten channels) · **Needs:** approve the ten `Review` SPECs + milestone visual/a11y audit; conversion effect is unmeasured.
**Scope:** channel home, article end, search, about; ten channels; EN/ES.

## 1. For the reader

- **Less furniture, more news.** Section cards, 10–18 px corners and repeated rounded containers are gone from the marketing surfaces. The lead story, proof, photo and action panel now read as one editorial page instead of a stack of widgets.
- **One obvious next step.** Each page has one saturated action panel ("request a consultation") plus a quieter brief path. The reader no longer has to choose between several competing buttons.
- **Proof before the ask.** Live bundle facts (stories, languages, updated, independence) sit above the CTA, not buried at the bottom.
- **Forms are recognisable as forms.** Fields are filled and bordered with a required note and a visible optional block; a field can no longer be mistaken for a section separator.
- **Balanced reading.** Coverage uses CSS multi-column balance, so one column no longer runs hundreds of pixels past the other.

## 2. For the business

- **Two-path funnel, one primary.** Consultation stays the primary conversion; the weekly brief is the low-friction secondary. Both write to the same lead API and keep the existing consent, qualification, partner-routing and funnel events.
- **Per-channel intent is preserved.** Legal/Sentinel keep a sidebar, Financial a banner, Sanctuary an inset, Campus a corner block in a 2-column hero, Network/Lab a full-bleed banner. The change is not one template painted seven times.
- **What it does *not* mean:** no claim of a conversion lift. No A/B test, no traffic data, and no analytics/consent decision (U9) exist yet. Treat the effect as **designed for** clarity and trust, not proven.
- **Monetisation is unchanged.** Lead pricing/partner model (U18) and the two-path offer ladder are untouched.

## 3. For the product and codebase

- **One conversion grammar, not seven forks.** `skins.css` owns the shared action/proof/photo/conversion/form rules; each skin only overrides placement and shape. Adding a channel still means a skin tuple + motif, not a page fork.
- **Balance is a gate, not a taste call.** `apps/web/e2e/layout.spec.ts` fails if a coverage column spread exceeds 260 px, if a compact CTA escapes its column, if the hero action panel leaves the viewport, or if any page overflows horizontally. This is the regression check the operator asked for.
- **Tokens are the contract.** The action surface, band, field fill/border/radius and danger colour are semantic tokens (`tokens.json` 84 tokens, schema-valid) injected by `theme.ts`; `token-lint` reports 0 raw colour literals in component source.
- **Task pages stay task pages.** Search/about use a process sidebar + the real form instead of a duplicate CTA; article end uses an open lead block. Admin/contact keep their compact density.

## 4. Tradeoffs and residual risk

- **Three-column coverage was retired for the current seven.** With nine uneven stories it left a 288–408 px ragged bottom; two balanced columns are the consistent choice. The `grid3` type remains for future feeds with enough uniform content.
- **Filled fields reintroduce a visible box.** That is deliberate: underline-only fields were the confusing part. The box is a field, not a section card.
- **Full-bleed bands require `overflow-x: clip`.** The page is audited at 1280 and 390 px; a future layout that adds a wider element must respect the same rule.
- **Photography licensing is unchanged.** CC BY-SA channels still depend on the in-caption credit; no new assets were added.
- **The direction is Approved, the SPECs are bound, but not yet reviewed.** The formal `@ui-visual-verify milestone` / `@ui-accessibility-audit milestone` run is still pending even though axe and the production e2e suite are green.

## 5. Evidence (2026-11-05)

| Claim | Result |
|---|---|
| Production build | pass |
| Playwright public + accessibility + admin + layout | 57 passed, 1 skipped |
| Layout balance / CTA containment / overflow | 40/40 checks pass |
| Channel pages desktop + mobile | 80/80 HTTP 200, zero horizontal overflow, no orphan `#brief-signup` links |
| Contrast | 7/7 channels pass the five gated pairs |
| Token contract | 84 DTCG tokens valid; 0 raw colour literals in 48 component files |
| Reference provenance | `reference-scan.py audit` PASS (0 problems, 0 warnings) |
| Sources | `verify-sources --industry all`: 10 industries / 45 sources, 45 pass, 0 fail, 0 warnings |

## 6. What is still open

- Milestone visual + accessibility audit across all ten skins (dark cybersecurity first).
- Approval of the ten `Review` channel-home SPECs; per-channel copy pass.
- Analytics/consent posture (U9) and traffic sizing (U10) before any conversion claim can be measured.
- Formal conversion measurement: impressions, CTA clicks, form starts, submits, qualified leads by channel/placement.
- New-channel content coverage: manufacturing EN 10 / ES 41, energy EN 16 / ES 39, retail EN 10 / ES 1; add EN feeds/broaden topics before launch.

## Next action

Run `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone` on the production build, then `@ui-screen-spec review` the seven bound SPECs.
