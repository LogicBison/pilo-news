# Channel inventory

**What this is:** the canonical list of live channels: name, slug, address, layout. The address of a channel is its own subdomain, never a path on the apex.
**Status:** Generated 2026-11-10 from live API (`GET /v1/industries`) · **Needs:** nothing manual — `./bin/start.sh test` and CI fail when this file is stale.
**Source:** the live API when it answers (it knows channels created from the admin console), the deployment profiles otherwise. The generated block is deliberately environment-free: no port, no scheme, no default channel. Those are deployment settings, and baking one machine into this file is what made the previous inventory impossible to check anywhere but the machine that wrote it.

## Inventory

<!-- CHANNEL_INVENTORY_BEGIN -->
**Channels:** 12 · **Channel host:** `{slug}.<channel-domain>` (`SN_CHANNEL_DOMAIN`: `localhost` in dev, `APP_DOMAIN` in prd)

| # | Channel | Slug | English | Spanish | Layout |
|---|---|---|---|---|---|
| 1 | Legal Services & Corporate Governance | `legal` | `legal.<channel-domain>/` | `legal.<channel-domain>/es` | editorial |
| 2 | Financial Services & Banking | `financial` | `financial.<channel-domain>/` | `financial.<channel-domain>/es` | professional |
| 3 | Psychiatry & Clinical Psychology | `behavioral-health` | `behavioral-health.<channel-domain>/` | `behavioral-health.<channel-domain>/es` | editorial |
| 4 | Education & Higher Academics | `education` | `education.<channel-domain>/` | `education.<channel-domain>/es` | academic |
| 5 | Logistics & Supply Chain | `logistics` | `logistics.<channel-domain>/` | `logistics.<channel-domain>/es` | professional |
| 6 | Cybersecurity & Threat Intelligence | `cybersecurity` | `cybersecurity.<channel-domain>/` | `cybersecurity.<channel-domain>/es` | professional |
| 7 | Stem Cell Treatments | `stem-cell` | `stem-cell.<channel-domain>/` | `stem-cell.<channel-domain>/es` | academic |
| 8 | Health & Medicine | `health-medicine` | `health-medicine.<channel-domain>/` | `health-medicine.<channel-domain>/es` | professional |
| 9 | Manufacturing & Industrial Operations | `manufacturing` | `manufacturing.<channel-domain>/` | `manufacturing.<channel-domain>/es` | professional |
| 10 | Energy & Utilities | `energy` | `energy.<channel-domain>/` | `energy.<channel-domain>/es` | professional |
| 11 | Retail & E-commerce | `retail` | `retail.<channel-domain>/` | `retail.<channel-domain>/es` | editorial |
| 12 | Digital Technology | `digital-technology` | `digital-technology.<channel-domain>/` | `digital-technology.<channel-domain>/es` | professional |

**Path form:** `/{about|contact|search|briefs|references}` · `/topic/{slug}` · `/article/{id}` · `/feed.xml` · `/es/...` for Spanish
**Compatibility:** `{apex}/{slug}/...` still renders and canonicalises to the channel host. `/admin` is apex-only.
**Root `/`** is the lobby (`/services`, `/privacy`, `/terms` beside it); `SN_DEFAULT_INDUSTRY` now only drives the 404 home link.
**Concrete URLs for this machine:** `./bin/channels.sh --urls`
<!-- CHANNEL_INVENTORY_END -->

## How to keep it updated

It cannot drift silently. Three gates, cheapest first:

1. `./bin/start.sh migrate` warns when the file no longer matches the channels in the database.
2. `./bin/start.sh test` runs `./bin/channels.sh --check` after the API and UI checks.
3. CI runs the same check with no server and no env file — from the deployment profiles — so a profile edit without a regenerated inventory fails the build.

Regenerate, then commit:

```bash
./bin/channels.sh --write    # live API first, profiles as fallback
./bin/channels.sh --check    # must print ok
./bin/channels.sh --urls     # concrete URLs for this machine, including the port
```

The generated block between the markers is machine-owned. Edit the prose outside them by hand.

## Next action

Nothing while the check is green. On a channel change: `./bin/channels.sh --write` and commit.
