# MOD-06 — AI change risk, M9 asset card test

**Scope of the diff:** uncommitted working tree for iteration M9 (`.work/plans/NEXT.md:83`).
Code: `apps/web/src/lib/assets.ts`, `apps/web/src/lib/api.ts`, `apps/web/src/messages/{en,es}.json`, channel home + article pages, `apps/web/e2e/public.spec.ts`, `apps/api/config/deployments/{legal,cybersecurity}.json`, `apps/api/migrations/011_seed_asset_offers.sql`, `apps/api/tests/contract/test_bundle.py`, plus `apps/web/src/app/skins.css` (coverage card clamp, repair of the energy column-balance finding).
Docs: iteration block, plan, decision ledger, touch-scope.

## AI change risk summary
- AI-assisted: yes (agent session, no `human-only` declaration)
- Boundaries crossed: 2 — (a) the web presentation layer (channel config → card → message catalogs) and one shared stylesheet rule for coverage cards, (b) the API's channel-config path (deployment profiles + one idempotent seed migration + a contract assertion). No worker, HTTP handler, or cross-context import was touched.
- New cross-boundary deps: none — the web already consumes `industry.cta` from `/v1/news/bundle`; the seed writes a key the API already serves (`channels/http/routes.py:39`).
- Test isolation: ok — `test_bundle.py` asserts `cta.asset` for the legal channel (fails only if the seed or the API passthrough breaks); `e2e/public.spec.ts` asserts render, absence, and the one-rung rule. `evidence: measured` (api 111 passed; full Playwright 59 passed / 1 skipped on a production build, including the layout suite that caught the regression).
- Human architectural review: optional — two boundaries, but the second is config-plus-seed with an idempotent guard; the product decisions were made by the operator (D-008, D-009).
- Blast radius (stylesheet rule): the clamp shortens long story excerpts to three lines at >=768px on every channel; it cannot hide a headline, and mobile keeps the full text. Measured column spreads after the rule: max 178px against a 260px gate (was 330px on energy). `evidence: measured`.
- Blast radius (asset config): if `cta.asset` names a slug the registry does not know, that channel renders no card and — because the brief rung is suppressed there — loses its only secondary ask; if the seed is wrong, the wrong channel offers an asset it cannot deliver. The failure is visible on the page, needs no data repair, and reverts by dropping the key. No writes, no lead-path change. `evidence: measured` (contract + e2e), `estimated` (reader harm from a missing rung).

## Recommendation
merge_ok

## Conditions if merge_with_conditions
- none — no conditions attached to this recommendation.
