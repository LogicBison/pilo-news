# Industry Sites SPEC — amendment 01 (2026-11-06)

**Amends:** `20261105-SPEC.md` R16 (CTA placement) · **Origin:** M9 / D-008, D-009 · **Status:** applied in code, awaiting owner review with the base SPEC
**Needs:** nothing to build; owner review of R16 wording when the base SPEC is next ratified.

## R16 — what changed and why

Base rule: "One primary CTA per page; secondary (brief signup) never competes visually. Placement and offer come from channel config (JSONB), not hardcoded JSX."

Two gaps in the base wording surfaced during M9:

1. **"secondary (brief signup)" named only one secondary rung.** With a gated asset card shipped, a page could carry two list-capture asks (asset waitlist + brief signup) and both count as secondary. The reader sees two email fields for the same relationship.
2. **"placement and offer come from channel config" was not implementable as written** while the asset was a hardcoded slug in a page component.

## Amended R16 (supersedes the base sentence)

Every channel home shows one primary CTA above the fold: a hero card plus a sticky mobile bar that appears after 60% scroll and is dismissible. Articles show the CTA after the summary and at end of article, never mid-paragraph. Search/about show a compact block; the footer carries a quiet link.

- **One primary CTA per page.** Secondary rungs never compete visually with it.
- **One secondary rung per page.** Where a channel configures `cta.asset` (a gated reference asset), the asset card is that channel's single secondary rung and the brief signup does not render. Where `cta.asset` is absent, the brief signup is the secondary rung.
- **Placement and offer come from channel config (JSONB), not hardcoded JSX.** `cta.asset` names an asset slug; `apps/web/src/lib/assets.ts` resolves the slug; the copy lives in `messages/{locale}.json` under `asset.<slug>.title|body`.

## Consequences

| Surface | Effect |
|---------|--------|
| `industries.cta.asset` | new optional key, seeded by `apps/api/migrations/011_seed_asset_offers.sql` for legal and cybersecurity |
| Channel home / article | asset card resolved from config; `#brief-signup` suppressed where an asset exists |
| Tests | `tests/contract/test_bundle.py` asserts `cta.asset`; `e2e/public.spec.ts` asserts render, absence, and the one-rung rule |
| Copy | no page promises a send date before delivery exists |

## Next action

Owner ratifies the amended R16 with the base SPEC; no further code change is implied.
