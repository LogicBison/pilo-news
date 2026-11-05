# UI skin refresh - next session brief

**Status:** proposed · **Needs:** operator selection of 2-3 reference sites per channel; `.work.ui` foundation run.
**Next action:** run `@ui-design-foundation greenfield`, then per-channel screen specs, then component build.

## Objective

give every channel a distinct, professional, lead-generating skin. current styling is one
material-inspired system shared by all channels; the gap is per-industry character, not
base quality.

## Constraints

- `.work.ui` is still greenfield: no design tokens, screen specs, or component catalog certified.
- UI completion gate applies: `@ui-visual-verify` + `@ui-accessibility-audit` pass, UIS-06 for agent-assisted UI.
- Themes are data (`industries.theme`); anything that needs per-channel layout must extend the
  three layout variants or add a new one, never fork a page tree.
- WCAG AA on every token pair; `pnpm check` must stay green for all channels.

## Reference sites (operator supplied 2026-11-05)

lead-generation patterns to study: above-the-fold CTA hierarchy, social proof placement,
form friction, pricing/segmentation, trust blocks.

| # | Site | Pattern worth extracting |
|---|------|--------------------------|
| 1 | https://userpilot.com/ | product-led hero + demo CTA pairing |
| 2 | https://databox.com/ | dense proof metrics above the fold |
| 3 | https://www.hubspot.com/ | segmented CTAs by intent |
| 4 | https://basecamp.com/ | plain-language positioning, single primary action |
| 5 | https://calendly.com/ | one job per page, embedded scheduling |
| 6 | https://www.typeform.com/ | form-first conversion, progressive disclosure |
| 7 | https://www.ellevest.com/ | trust-first copy for a regulated audience |
| 8 | https://www.nerdwallet.com/ | comparison clarity, disclosure placement |
| 9 | https://monday.com/ | visual product framing, benefit-led cards |
| 10 | https://leadpages.com/ | landing-page CTA repetition |
| 11 | https://www.charitywater.org/ | emotional proof + donate CTA |
| 12 | https://www.semrush.com/ | data-rich social proof |
| 13 | https://mailchimp.com/ | tone-led brand voice, onboarding CTA |
| 14 | https://www.warbyparker.com/ | product clarity, low-friction entry |

## Proposed per-channel direction

| Channel | Direction | References |
|---------|-----------|------------|
| legal | authority + discretion, consultation-led | ellevest, nerdwallet |
| financial | comparison + disclosure, data-forward | nerdwallet, databox |
| behavioral-health | calm trust, privacy-first | ellevest, charitywater |
| education | outcome proof, program comparison | hubspot, databox |
| logistics | operational clarity, quote request | basecamp, calendly |
| cybersecurity | threat credibility, assessment CTA | semrush, userpilot |
| stem-cell | clinical credibility, ethics-first | ellevest, typeform |

## Work plan

1. `@ui-design-foundation greenfield`: tokens, type scale, component inventory, screen specs for one channel.
2. `@ui-style-stack`: confirm tailwind + CSS custom properties remain the delivery mechanism.
3. Per-channel: theme tokens + layout variant choice + hero/CTA composition spec.
4. Component build: one channel first (legal), verify, then reuse for the rest.
5. `@ui-visual-verify` + `@ui-accessibility-audit` per channel; `pnpm check` for contrast.

## Guardrails

- no per-channel page forks; theme + variant + copy only.
- lead forms keep consent-first behavior and DSAR support (ADR 013).
- do not regress CLS or the current axe-clean state.
- keep copy in `messages/en.json` / `messages/es.json`.

## Next action

pick the reference pairs per channel, then run the UI foundation skill.
