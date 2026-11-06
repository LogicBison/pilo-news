# DESIGN DIRECTION — editorial-conversion

**What this is:** A synthesized, brand-coherent direction derived from 2–4 website references — the bridge from reference DNA to tokens, SPECs, and implementation.
**Status:** **Approved** (2026-11-05) · **Date:** 2026-11-05 · **Build:** v2 applied and verified
**Needs:** none for the build; bind the seven SPECs + run the milestone visual/a11y audit. Operator approved both the direction and the token/bind package on 2026-11-05.

> This is not a clone. A user must not be able to name a reference brand from the resulting screen. Reference IDs in backticks must match `.work.ui/inputs/references/<slug>/`.

## 1. Product & job

- **Product / screen:** the channel-home conversion spine (`/{industry}`, all 7 channels) plus the article CTA — the moment a reader decides to ask for a specialist or join the brief.
- **Audience:** P1 industry reader: a professional scanning what changed in their field, skeptical of hype, deciding whether to act.
- **Primary action:** request a consultation. Secondary: join the weekly brief.
- **Constraints:** Next.js 15 + Tailwind 4 + CSS custom properties; no new webfont; WCAG 2.2 AA; all 7 channel palettes must pass contrast; no protected files; no third-party assets.
- **Current state (before):** the 2026-11-05 stem-cell screenshot shows a flat text hero, a pale CTA card with one dark pill, four equal proof tiles, a photo band with a small caption chip, and pale card-on-card sections. The page reads as a template, not a newsroom with a point of view. `estimated` from the operator screenshot.

## 2. Reference set & weights

| Reference ID | Role | Weight | Why selected | DNA confidence |
|---|---|---|---|---|
| `hubspot` | primary | 45% | warm canvas, one accent, proof-before-features, two-field first step, segmented intent | medium |
| `leadpages` | secondary | 35% | conversion-block rhythm, outlined cards with hard offset shadow, one repeated verb, visible capture→qualify→respond loop | high |
| `ellevest` | accent | 20% | audience-specific trust, question-led entry, low-friction capture, calm warm surfaces | medium |

**Rejected references:** `databox` (dashboard product, wrong job); `nerdwallet` (comparison marketplace, wrong job); `basecamp`/`mailchimp` (trial pages, weak lead-gen signal); `warbyparker` (blocked 403).

## 3. Synthesis thesis

> A newsroom with a conversion spine: editorial authority on a warm, high-contrast canvas, proof placed before the ask, and one unmistakable action surface — so a skeptical professional can act without feeling sold to.

## 4. Design principles

1. **One action surface.** Exactly one saturated, dark action block per screen. Everything else is quiet editorial surface. The eye should find the CTA in one second.
2. **Proof before the ask.** Verifiable numbers, process, and response expectation come before the form. No invented logos, counts, or testimonials.
3. **Editorial contrast, not decoration.** Oversized serif display against compact sans; one accent rule; generous whitespace. Remove gradient mush and same-size cards.
4. **Low friction by default.** Two required fields; the qualification is a chip/select; phone, company, and message live under “Add details (optional)”. The brief is one inline field.
5. **The skin survives.** This direction adds a shared conversion grammar; it does not replace any channel's hero, motif, radius, or palette. Every rule composes with `[data-skin]`.

## 5. Token proposal

**Status:** proposal only — apply through the token owner at `bind`; do not hardcode. No new palette colours; the semantic **composition** aliases derive from existing channel tokens, so every channel keeps passing `pnpm check`. `--sn-on-primary`, `--sn-shade` and `--sn-danger` are now injected by `themeStyle`; `--sn-danger` is contrast-aware (`#b91c1c`, switching to `#fca5a5` when the canvas is dark).

| Role | Proposed value | Fallback / note | Source |
|---|---|---|---|
| `--sn-action-bg` | `color-mix(in srgb, var(--sn-primary) 94%, var(--sn-shade))` | deeper than primary; white text already gated | synthesis |
| `--sn-action-ink` | `var(--sn-on-primary)` | white on primary, gated by `check-themes` | existing |
| `--sn-action-muted` | `color-mix(in srgb, var(--sn-on-primary) 76%, var(--sn-action-bg))` | ≥4.5:1 on action bg (verified 5.83–9.21:1) | synthesis |
| `--sn-action-line` | `color-mix(in srgb, var(--sn-accent) 82%, var(--sn-on-primary))` | 2 px top rule + chips, non-text only | synthesis |
| `--sn-band` | `color-mix(in srgb, var(--sn-surface) 62%, var(--sn-bg))` | proof band / brief band canvas | synthesis |
| `--sn-lift` | `0 6px 0 -3px color-mix(in srgb, var(--sn-primary) 20%, transparent)` | hard offset shadow for the action panel only | synthesis |
| `--sn-on-primary` | `#ffffff` | semantic ink on primary | existing |
| `--sn-shade` | `#000000` | mix base for deepening | synthesis |
| `--sn-danger` | `#b91c1c` / `#fca5a5` | contrast-aware error text (`themeStyle`) | existing |

- **Token-lint:** `bash $AI_UI_SOURCE/scripts/token-lint.sh --tokens apps/web/src/app/globals.css --tokens apps/web/src/lib/theme.ts apps/web/src` → 0 raw colour literals in component source.
- **Type:** keep `Georgia` display + `system-ui` body (no webfont). Add one display step: hero H1 `clamp(2.35rem, 4.6vw, 3.9rem)` / `1.03`; section headings `clamp(1.55rem, 2.4vw, 2.05rem)`. Proof figures use tabular numerals.
- **Space:** keep the 4 px base; section rhythm 64 px mobile / 96 px desktop; action panel padding 28–36 px.
- **Radius:** marketing surfaces 0–2 px; form fields 2 px; chips and buttons 2 px. The skin's `--sn-radius` still governs task pages.
- **Surface/elevation:** marketing surfaces are flat or full-bleed; the action panel is a flat colour block; no soft card shadow on the conversion spine.
- **Motion:** 180–220 ms `--sn-ease` on hover colour/shadow/translate; no scroll-triggered reveals; `prefers-reduced-motion` removes transforms.

## 6. Layout & composition

- **Hero:** no card around the lead story. The skin's hero grid (split/ledger/poster/ribbon) stays, but the hero is an open editorial composition with a kicker, display H1, topics, and a favourites rail; the lead story sits on the canvas with a bottom rule. Campus (education) uses a 2-column hero so its corner CTA is balanced beside the lead story, not stranded beneath it.
- **Action panel:** one dark action panel per screen; 0–2 px corners; accent top rule; 3-item promise row ("No obligation · One partner · Reply in one business day"); primary button; quiet "or get the weekly brief" link; disclaimer at 12 px. Lab (stem-cell) and Network (logistics) break it out as a full-bleed banner; Legal/Financial/Sentinel keep a sidebar/banner; Sanctuary keeps an open accent-rule column; Campus keeps a corner block.
- **Section order:** hero + action panel → proof band → photo band → desk brief + topics → coverage → sources → conversion band (process + form) → brief band → footer.
- **Proof band:** full-bleed `--sn-band` strip with a 1 px top rule and bottom rule; four facts in one row at `lg` with vertical hairlines, figures at 1.6 rem tabular, labels at 12 px; 2×2 on mobile. No outer card.
- **Photo band:** full-bleed, 360 px desktop / 240 px mobile, no frame; `linear-gradient` scrim from the channel primary; caption is an overlay lockup (channel name + tagline + credit), not a floating chip.
- **Coverage:** CSS multi-column with `column-fill: balance`, not fixed column DOM. 2 balanced columns for `grid2`/`grid3`/`magazine`; 1 column for `stack`. The regression test asserts the last-item bottom spread ≤ 260 px.
- **Conversion band:** full-bleed tinted band, open 2-column layout at `lg` (process left, form right, vertical rule between); no outer card.
- **Brief band:** open band with a top rule; serif headline, value list, inline name/email row; secondary weight.
- **Forms:** fields are filled surfaces with a visible 1 px boundary and 2 px corner — never underline-only, because a rule under a label reads as a section separator. Labels are 600 weight, required fields carry an aria-hidden `*`, and a "Fields marked * are required" note sits above the first field. The optional block is a bordered control, not a divider. Textareas keep a visible boundary and `min-height`; selects are full-height. Focus is a 3 px primary ring.
- **Grid/container:** 1200 px max, 72 ch reading measure; 12-column mental model implemented with existing Tailwind grids.
- **Density:** comfortable; 64–96 px between major sections; marketing surfaces use 0–2 px radii; task pages keep their own compact density.
- **Responsive:** action panel drops below the hero at `md` (except full-bleed banners, which stay full-width); proof 2×2 at `sm`; photo 16:6 → 4:3; conversion stacks at `lg`; coverage columns collapse to 1 at `md` down.

## 7. Component rules

| Component | Rule | Reference principle (not surface) |
|---|---|---|
| Nav | keep thin nav; active channel gets a 2 px accent underline | goal-first entry (ellevest) |
| Primary CTA | solid action surface, white label, arrow affordance, one per screen; same verb at hero and module | repeated single verb (leadpages/hubspot) |
| Cards | marketing surfaces are open rules, not cards; action panel only | outlined + offset shadow (leadpages) |
| Forms | filled, bordered fields (not underline-only); 2 required fields + qualification; optional phone/company under a bordered "Add details" control; message visible and optional; required note + `*`; inline errors; success = next-step card | two-field first step (hubspot), progressive capture (ellevest) |
| Proof | verifiable bundle data only; tabular figures; caption states the source ("from this channel's live bundle") | proof before features (hubspot) |
| Brief | open band with top rule; name/email inline; one-sentence value; privacy line | low-friction capture (ellevest/typeform) |
| Story cards | open editorial item with top hairline; featured item gets an accent top rule and larger title; no border/radius/shadow; no image requirement | editorial hierarchy (ellevest) |

## 8. Content voice

- **Voice:** plain, specific, second person; no urgency, no hype, no exclamation marks (inherits `.work/voice/README.md`).
- **Headline shape:** outcome + audience (“Talk to a vetted {channel} specialist”); brief: “One email a week. The stories that moved this field.”
- **CTA verbs:** request, send, get, join. One verb per action. No “unlock”, “act now”, “limited”.
- **Proof strategy:** numbers from the live bundle + process facts; never invented logos or testimonials.
- **Do not reuse:** source copy, taglines, testimonials, customer names.

## 9. Originality guardrails

- **Do not copy:** logos/wordmarks; reference palettes as identity (orange, violet/lime, cream/teal); proprietary illustrations/photos/icons/fonts; source copy; distinctive composition.
- **Differentiating moves (≥3):** (1) channel-owned dark action panel with a 2 px accent rule and a promise row; (2) proof band built from live bundle facts, not logos; (3) an editorial photo band with a channel-tinted scrim and a credit lockup; (4) two-path conversion (consultation vs brief) with different visual weight.
- **Recognition test:** show the draft beside each reference; if a viewer names the reference brand, revise.
- **Similarity budget:** family resemblance in principles only; no shared brand assets or copy.
- **Legal note:** design guidance, not legal advice.

## 10. Accessibility constraints

- WCAG 2.2 AA: body 4.5:1, large/UI 3:1; visible focus; 44 px targets; no motion-only meaning; reduced-motion honored.
- `--sn-action-muted` must be re-checked on all 7 channel action surfaces (add the pair to `apps/web/scripts/check-themes.mjs` if it is used for text).
- **Reference failures not inherited:** Ellevest's 46/50 missing alt text, HubSpot's white-on-orange small text, Leadpages' lime-on-light body text. Our photos carry alt + credit; accent is non-text or large.
- **Checks:** `pnpm check` (7 channels × 5 pairs) + `@ui-accessibility-audit milestone` + `token-lint` + Playwright axe.

## 11. Screen application

| Screen | Reference IDs | Rules to bind | Status |
|---|---|---|---|
| `channel-home-legal` | `hubspot`, `leadpages`, `ellevest` | action panel, proof band, photo scrim, conversion module, brief band | Review |
| `channel-home-financial` | same | same, Terminal density: tabular figures first | Bound |
| `channel-home-behavioral-health` | same | same, soft surface: no hard rule on action panel, keep inset | Bound |
| `channel-home-education` | same | same, numbered process steps | Bound |
| `channel-home-logistics` | same | same, banner-style action panel | Bound |
| `channel-home-cybersecurity` | same | same, dark-scheme action panel variant | Bound |
| `channel-home-stem-cell` | same | same, Lab form-first emphasis | Bound |

**Build record (2026-11-05):**

1. **Visual lift — done:** `skins.css` conversion grammar (open hero, full-bleed proof/photo/conversion, sharp corners, 0–2 px radii), `Hero.tsx` kicker/display H1, `CtaCard.tsx` action panel, `ProofStrip.tsx` band, `SkinScene` full-bleed scrim. The hero card wrapper and page-section cards were removed.
2. **Lead-gen flow — done:** `LeadForm.tsx` filled fields, required-note/asterisks, optional block as a control, message visible; `TrustBlock.tsx` merged into the conversion band; `BriefSignup.tsx` open band; copy keys in `messages/en.json`/`es.json`.
3. **Balance + task pages — done:** CSS multi-column coverage (`column-count` + `balance`), Campus 2-column hero, search page uses process sidebar instead of a duplicate CTA, compact CTA scoped to its column.
4. **Verification — pass:** `pnpm lint`, `pnpm typecheck`, `pnpm check` (267 keys, 7 themes); production `pnpm build`; Playwright 29 passed / 1 skipped, including `e2e/layout.spec.ts` (21 checks) and accessibility; 56 channel pages × desktop/mobile audited for 200 + zero horizontal overflow.
5. **Pending:** apply the four composition aliases to `tokens.json` (bind step) and bind §13/§11 in the seven SPECs; operator ratification of this Draft direction.

**Token apply step (done 2026-11-05):** the composition aliases are in `.work.ui/design-system/tokens.json` (84 tokens, schema-valid) and referenced from `apps/web/src/app/skins.css`; `--sn-on-primary`, `--sn-shade`, `--sn-danger` are injected by `theme.ts`. Re-run token schema + token-lint after any token change. `bind` is applied to all seven SPECs.

## Next action

Operator ratification of this direction, then apply the composition aliases + `bind` to the seven SPECs; the build and layout checks are already green.