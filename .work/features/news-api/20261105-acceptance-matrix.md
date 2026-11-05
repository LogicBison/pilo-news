# Reference acceptance matrix - news API and sites

**What it is:** the LogicBison multilingual news scenarios adapted to System News' contracts; the executable acceptance checklist for M1-M3.
**Status:** Draft (2026-11-05) · **Needs:** nothing (executed during implementation).
**Source:** `/mnt/work/Projects/LogicBison/docs/news-multilingual-replication.md` §13 (28 scenarios), adapted to ADR 007/010 and the `/v1` contract.

| # | Scenario | Action | Expected | Rule |
|---|----------|--------|----------|------|
| 1 | English bundle | `GET /v1/news/bundle?industry=legal&locale=en` | `language:"en"`, items all `en`, `fallback:false` | news-api R16, R13 |
| 2 | Spanish bundle | `...&locale=es` after ES sources seeded | `language:"es"`, items all `es` | R16, R13 |
| 3 | Unknown locale | `...&locale=fr` | `400 invalid-locale` (divergence: explicit API error, site never emits it) | R13 |
| 4 | Case-insensitive locale | `...&locale=ES` | Spanish bundle (normalized to lowercase) | R13 |
| 5 | Missing locale | `GET /v1/news/bundle?industry=legal` | English bundle, `language:"en"` | R13 |
| 6 | Explicit ES page | `/es/legal` | 200, Spanish UI + ES items, `<html lang="es">` | industry-sites R1-R3 |
| 7 | Cookie redirect | `sn_locale=es`, request `/legal` | `302` to `/es/legal`, query preserved | industry-sites R2 |
| 8 | Accept-Language | No cookie, `es-MX,es;q=0.9,en;q=0.5`, `/legal` | `302` to `/es/legal` | R2 |
| 9 | English rewrite | No cookie, `en-US`, `/legal` | 200 at `/legal` (no `/en` in URL) | R1 |
| 10 | Switcher | Click ES on `/legal/article/{id}` | Cookie set, navigates to `/es/legal/article/{id}`; later `/` lands on `/es/legal` | R2 |
| 11 | Date locale | `/es/legal` | Dates rendered `es-ES` month abbreviations, UTC | R2, R11 |
| 12 | API down | Stop API or unset internal URL | Distinct unavailable state, page still 200 | R10 |
| 13 | Refresh auth | `POST /v1/admin/refresh` without token | `401` (or `503` if admin auth unconfigured) | news-api R17, R11 |
| 14 | Refresh success | With token, `force:true` | `202` + `run_id`; status reaches `ok`; bundles rebuilt | R17 |
| 15 | Reset | `full_reset:true` with confirmation | All summaries regenerated; audited | ingestion R15, R17 |
| 16 | Schedule | Advance clock 12 h | Exactly one scheduled run per channel; staggered | ingestion R1 |
| 17 | No schedule on read | Public GETs for 1 h | Zero refresh runs (no request-driven TTL) | ingestion R1 |
| 18 | Missing AI key | Unset keys, force refresh | Headlines/layout intact; no summaries; run `ok`/`partial` | ingestion R11, R13 |
| 19 | Provider failure | Invalid key, force refresh | Same as 18; refresh still returns a terminal status | ingestion R13 |
| 20 | Feed failure | Disable one ES feed | Other ES items still rank; warning logged; run `partial` | ingestion R16 |
| 21 | Empty language | All ES feeds produce nothing | `bundles.es` exists empty; `GET ?locale=es` returns empty `es`, not English | news-api R13 |
| 22 | Missing language bundle | Delete the ES bundle cache | `GET ?locale=es` returns EN bundle with `language:"en"`, `fallback:true` | R13 |
| 23 | No cross-language dedupe | Same story in EN and ES feeds | Appears in both bundles | ingestion R6/R8 |
| 24 | Summary language gate | Add ES source, force refresh | ES item gets Spanish summary; never reuses an EN summary | ingestion R12/R15 |
| 25 | `prompt_version` | Bump version, force refresh | Old summaries reused; after `full_reset`, regenerated | ingestion R15 |
| 26 | SEO | Fetch `/es/legal` HTML | `hreflang` en/es/x-default; canonical `/es/legal`; og:locale `es_ES` | industry-sites R7 |
| 27 | Sitemap | `GET /sitemap.xml` | English and `/es` entries with alternates; admin/API excluded | R7 |
| 28 | Channel isolation | Same story in `legal` and `financial` feeds | Each bundle contains only its channel | news-api R4, I1 |

**Divergences from the reference (deliberate):** unknown locale returns `400` instead of an English bundle; schema is Postgres/Redis instead of a JSON cache; admin auth is JWT+Argon2 instead of a shared token; scheduling is worker-driven instead of request-TTL.

## Next action

Run this matrix during M1 (API) and M3 (web); record pass/fail in the milestone verification block.
