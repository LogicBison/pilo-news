# SCREEN REFERENCE MAP

**What this is:** Which references and direction are bound to each screen SPEC.
**Status:** Approved · **Updated:** 2026-11-05
**Needs:** keep in sync with each SPEC §13 and the direction status.

| Screen slug | SPEC | Reference IDs | Direction | Bound | Date |
|---|---|---|---|---|---|
| `channel-home-legal` | `screens/channel-home-legal/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-financial` | `screens/channel-home-financial/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-behavioral-health` | `screens/channel-home-behavioral-health/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-education` | `screens/channel-home-education/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-logistics` | `screens/channel-home-logistics/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-cybersecurity` | `screens/channel-home-cybersecurity/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-stem-cell` | `screens/channel-home-stem-cell/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |

| `channel-home-manufacturing` | `screens/channel-home-manufacturing/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-energy` | `screens/channel-home-energy/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |
| `channel-home-retail` | `screens/channel-home-retail/20261105-SCREEN-SPEC.md` | `ellevest`, `hubspot`, `leadpages` | `directions/editorial-conversion.md` | Approved | 2026-11-05 |

## Rules

- A row is valid only when the direction is `Approved` and its token proposal has been applied.
- SPEC §13 must contain the same `referenceIds`, `extractedRules`, `doNotCopy`, and `originalityCheck`.
- Remove a reference from the row when its DNA is superseded — do not silently keep stale bindings.

## Next action

`@ui-visual-verify milestone` + `@ui-accessibility-audit milestone` on the production build; then review the seven SPECs.
