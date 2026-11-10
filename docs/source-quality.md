# Source quality policy

Every enabled feed is graded against a small, testable policy. The same rules
gate the seeded portfolio, the deployment-profile importer, and the operator
review. Nothing here is a substitute for the publisher's terms — licensing stays
an owner decision (U5).

## 1. Gates

A feed passes when it clears all of these:

| Gate | Rule | Why |
|------|------|-----|
| Reachable | HTTP 200 and a parseable RSS/Atom document | Dead feeds silently starve a channel |
| Structure | at least 3 items, each with a title and link | Guards against placeholder or broken documents |
| Fresh | newest item younger than 45 days (warn at 14) | A stale feed is worse than no feed: it makes the channel look abandoned |
| Language | declared language agrees with the feed's titles (stopword vote, 75% confidence) | A mislabelled Spanish feed in an English column corrupts the site |
| Size | at most 200 items; warn above | Unbounded feeds are usually not curated |
| Trust | trust at or above 0.75 | Editorial floor; below it the source cannot lead a story |
| Duplicates | fewer than 40% repeated titles | Detects broken or looping feeds |

Failures are hard stops except thin-but-valid feeds (3–9 items), low trust,
aging (14–45 days), future-dated items, and duplicate ratio; those lower the
score and appear as warnings.

## 2. Score and grade

Score starts at 1.0 and is penalised per issue; grade maps to
`A ≥ 0.90`, `B ≥ 0.80`, `C ≥ 0.70`, `D < 0.70`. A feed passes when it has no
hard failure and scores at least 0.70.

Trust bands used for the launch portfolio:

| Band | Meaning | Examples |
|------|---------|----------|
| 0.90–0.95 | Reference outlet; wire-grade reliability | WSJ (disabled, stale), FreightWaves, ABA Journal |
| 0.85–0.89 | Established trade publication | Finextra, BleepingComputer, Supply Chain Dive |
| 0.78–0.84 | Niche or regional outlet, strong domain coverage | Confilegal, Infocop, Educación Futura |

## 3. Coverage policy

Each channel must end with at least four enabled sources and at least one per
supported language (EN, ES). The importer reports violations as warnings, and
`verify-sources` lists them under `coverage`.

## 4. Run the verification

```bash
# every channel
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli verify-sources --industry all

# one channel
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api \
  python -m news_api.cli verify-sources --industry financial
```

The command prints JSON: per source `score`, `grade`, `passed`, `metrics`
(items, newest item age, detected language), and `issues`; per channel
`coverage`. Exit code is `1` when any source fails, so CI can gate on it.

## 5. What to do with a failure

- **Stale or empty feed**: disable it (`PATCH /v1/admin/sources/{id}`
  `{"enabled": false}`) and add a replacement that passes. Do not delete: the
  row keeps provenance for articles already published.
- **Language mismatch**: fix the declared language or drop the feed.
- **Low trust**: raise trust only with an editorial reason recorded in the
  channel's deployment profile.
- **Duplicate-heavy**: usually a broken publisher feed; replace it.
- **`robots_disallowed`**: the publisher's `robots.txt` refuses our crawler.
  There is nothing to fix from our side — a feed path under a `Disallow` is not
  ours to read. Disable the source in its deployment profile (never by hand in
  the database, so the profile stays the source of truth) and add a replacement.
  Re-enable it only if the publisher changes the file or grants a licence; the
  crawler page at `/bot` is what our user agent points at.

### Retired 2026-11-10 (robots, not breakage)

| Source | Channel | Why |
|--------|---------|-----|
| Finextra | financial | `User-agent: *` carries `Disallow: /rss/` (specific bots get `Allow: /rss/`) |
| The Register | digital-technology | default-deny policy: `User-agent: *` → `Disallow: /`, licence sold separately |

Both were disabled through their profiles (`apply-profile`) and are excluded
from `verify-sources`. Financial dropped to 3 enabled sources against the policy
minimum of 4, so `Federal Reserve Board` press releases
(`https://www.federalreserve.gov/feeds/press_all.xml`, EN, trust 0.95) were
added and the profile re-applied. `verify-sources --industry all` is 50/50 with
no coverage warnings.

`verify-sources` exits 1 on any failed source and on any channel below the
availability floor; read `summary.failed` and `availability` when it does.

## 6. Availability and permission

Coverage counts configured sources; **availability** counts the ones a publisher
still lets us read. They are reported separately and only the second one gates.

- **Permission ledger.** `verify-sources` writes `permission_state`
  (`allowed` / `denied` / `licensed`), `robots_checked_at`, `robots_hash` and
  `robots_crawl_delay` per source. The hash names the exact robots text the
  verdict came from, so a publisher editing their file is visible as a changed
  record rather than a mystery regression.
- **A refusal is a state.** `401`/`403` → outcome `denied`, seven-day host
  cooldown, no fail-streak escalation (it is not a host outage). A `403` whose
  body is a WAF challenge is classified `challenge` instead.
- **Licensed feeds.** `auth_type` (`header`/`basic`) with `auth_secret_ref`
  naming an environment variable. The database stores the variable name, never
  the secret. A publisher-requested `User-Agent` is `auth_type: header` +
  `auth_header_name: User-Agent` — the supported alternative to browser
  impersonation.
- **Availability floor.** A channel needs four healthy sources; below that the
  CLI exits 1 with `availability.healthy` in the report.
- **Primary sources first.** Government, regulator and exchange feeds are the
  preferred replacement when a desk loses a source: explicit terms, stable
  URLs, no WAF. Added 2026-11-10: CISA News (cybersecurity), SEC Press Releases
  (financial), alongside the Federal Reserve Board (financial).

## 7. Editorial judgment that stays human

Automation covers liveness, freshness, structure, and language. It cannot judge
licensing, editorial balance, or whether an outlet is appropriate for a
regulated channel. Those remain owner decisions, recorded in the deployment
profile and `.work/plans/UNKNOWNS.md`.

## Next action

Re-run `verify-sources` after any portfolio change; it must exit 0 and report
`unavailable: 0`.
