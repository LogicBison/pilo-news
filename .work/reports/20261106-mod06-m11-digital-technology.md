# MOD-06 — AI change risk, M11 digital-technology channel

**Scope of the diff:** M11 working tree — new deployment profile, new skin + two SVGs + a licensed photo, e2e loops extended, channel docs, inventory regenerated.

## AI change risk summary
- AI-assisted: yes (agent session, no `human-only` declaration)
- Boundaries crossed: 2 — (a) the channel-config path (a new profile applied through the existing importer), (b) the web presentation layer (one skin entry, two SVG assets, one photo with credit, e2e loops). No API, schema, worker, or cross-context import changed.
- New cross-boundary deps: none — the profile uses the existing `IndustryProfile` schema; the skin uses the existing `Skin` interface and `resolveSkin`.
- Test isolation: ok — the new channel appears in the layout loop (`e2e/layout.spec.ts`), a public-spec test asserts its skin, brief rung and credit line, and `pnpm check` reads its theme from the live API. `evidence: measured` (64 passed, 1 skipped on a production build; 11/11 contrast).
- Human architectural review: optional — the risky part is content and licensing, not architecture.
- Blast radius: if the profile is wrong, one channel renders with the wrong theme or empty feeds; if the skin assets are missing, `resolveSkin` falls back to the layout skin and the page still renders. If the CC BY-SA credit were dropped from the skin, the licence would be breached on a public page — the highest-consequence failure here, and it is asserted by the e2e test. `evidence: measured` (tests) / `assumption` (defects in the SVG art are cosmetic and only a human notices).

## Recommendation
merge_ok

## Conditions if merge_with_conditions
- none — the licence credit is asserted in the test suite.
