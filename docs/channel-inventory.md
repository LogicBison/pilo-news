# Channel inventory

**What this is:** the canonical list of live channels, slugs, localized URLs, layout and the default channel.
**Status:** Generated 2026-11-05 · **Needs:** re-generate after any channel change; a stale file fails the local test gate.
**Source:** `GET /v1/industries` + `APP_BASE_URL` + `SN_DEFAULT_INDUSTRY`. The committed file reflects the local dev base; regenerate with the production base for a production inventory.

## Inventory

<!-- CHANNEL_INVENTORY_BEGIN -->
**Base URL:** http://localhost:43991 · **Default channel:** `/stem-cell` (root `/` redirects) · **Admin:** http://localhost:43991/admin · **API health:** http://localhost:46105/v1/health
**Channels:** 11

| # | Channel | Slug | English | Spanish | Layout | Default |
|---|---|---|---|---|---|---|
| 1 | Legal Services & Corporate Governance | `legal` | http://localhost:43991/legal | http://localhost:43991/es/legal | editorial |  |
| 2 | Financial Services & Banking | `financial` | http://localhost:43991/financial | http://localhost:43991/es/financial | professional |  |
| 3 | Psychiatry & Clinical Psychology | `behavioral-health` | http://localhost:43991/behavioral-health | http://localhost:43991/es/behavioral-health | editorial |  |
| 4 | Education & Higher Academics | `education` | http://localhost:43991/education | http://localhost:43991/es/education | academic |  |
| 5 | Logistics & Supply Chain | `logistics` | http://localhost:43991/logistics | http://localhost:43991/es/logistics | professional |  |
| 6 | Cybersecurity & Threat Intelligence | `cybersecurity` | http://localhost:43991/cybersecurity | http://localhost:43991/es/cybersecurity | professional |  |
| 7 | Stem Cell Treatments | `stem-cell` | http://localhost:43991/stem-cell | http://localhost:43991/es/stem-cell | academic | root |
| 8 | Manufacturing & Industrial Operations | `manufacturing` | http://localhost:43991/manufacturing | http://localhost:43991/es/manufacturing | professional |  |
| 9 | Energy & Utilities | `energy` | http://localhost:43991/energy | http://localhost:43991/es/energy | professional |  |
| 10 | Retail & E-commerce | `retail` | http://localhost:43991/retail | http://localhost:43991/es/retail | editorial |  |
| 11 | Digital Technology | `digital-technology` | http://localhost:43991/digital-technology | http://localhost:43991/es/digital-technology | professional |  |

**Patterns:** `/{slug}/search` · `/{slug}/about` · `/{slug}/contact` · `/{slug}/article/{id}` · `/es/{slug}/...`
<!-- CHANNEL_INVENTORY_END -->

## How to keep it updated

1. Add or remove a channel (profile import or admin console).
2. Run `./bin/channels.sh --write` with the stack up.
3. Run `./bin/channels.sh --check` (or `./bin/start.sh test`); it fails when this file is stale.
4. Commit the regenerated file with the channel change.

The generated block is the only machine-owned part — edit the prose outside the markers by hand.

## Next action

`./bin/channels.sh --write` after any channel change.
