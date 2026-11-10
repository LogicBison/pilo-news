# Next improvement session — brand, fetching, content

**Status:** Draft (2026-11-09) · **Needs:** owner decision on the fetcher's contact URL (decision 1) and the wordmark treatment (A0); the rest is executable without input.
**Scope:** four tracks from the 2026-11-09 request: (A) root-site logo, (B) favicons everywhere, (C) fetcher access + safe fetching, (D) ten content improvements.
**Evidence base:** the 2026-11-07 dev bundle (`backups/news-dev-bundle-20261107-205243.tar.gz`, 676 published articles, 52 sources, 78 refresh runs) plus the code as it stands at `cb2f1c9`.

---

## Assumption ledger

**Confirmed (file or runtime evidence)**

- the root site draws its mark as a 10 px CSS square, not the logo: `apps/web/src/components/lobby/shell.tsx:53-56`, `.lb-brand-mark` at `apps/web/src/components/lobby/lobby.css:102-108`.
- there is no favicon anywhere: no `apps/web/src/app/icon.*`, no `icons:` entry at `apps/web/src/app/layout.tsx:13-27`; `middleware.ts:188` already passes `/favicon.ico` through, so the file is simply missing.
- channel headers show the per-skin SVG emblem plus "System News": `apps/web/src/components/Header.tsx:29-38`.
- the fetcher already blocks SSRF, caps size, re-validates redirects, and sends conditional headers: `apps/api/src/news_api/articles/infrastructure/fetcher.py:19-22,44-66,94-138`.
- it does not read robots.txt, pace per host, honour `Retry-After`, or retry: same file, end to end; `ingest.py:160` is a flat `Semaphore(6)` over all sources.
- the bot identity is a placeholder domain: `fetcher.py:22` and `offers/infrastructure/fetch.py:14` both say `+https://system-news.example/bot`.
- feeds currently fetch: 51/52 sources enabled and `active`; 308 polls, 3 errors, 89 × 304 over 78 runs; two sources carry an error (WSJ Markets stale 647 days, Inside Higher Ed `ParseError` ×3).
- summaries are one shape, three sentences: 562/649 (87%); median 452 chars; 30% contain a "for professional readers…" formula; 43% carry no consequence clause at all (term scan).
- the 404 copy still promises a seven-day window in both locales (`en.json`/`es.json`, `article.notFoundBody`) while retention is 30 days.

**Inference (state it, don't bank it)**

- no publisher is blocking the current bot. Three errors in 308 polls is not a block signal; the placeholder UA is a risk, not an observed failure. Prod egress differs from this host (owner's VPS), so the prod number is unmeasured.
- the two long-tail source errors are feed-side, not fetcher-side (stale WSJ feed, one parser corner on Inside Higher Ed).

**Unknown**

- whether `heraldfox.com` DNS/TLS will be finished in the same session (O9 blocks the live check of A/B on the apex).
- whether the owner wants channel favicons differentiated per desk (plan assumes one mark for all hosts; a per-host route is a later phase).

---

## Sequencing

1. **A + B together** (one asset pipeline, one PR): logo on the root site and derived favicons. Cheap, visible, no owner input beyond the wordmark call.
2. **D1–D5, D7–D8** (content): prompt + validator + copy changes; testable offline, no infra.
3. **C** (fetching): the only track that touches runtime infrastructure; do it after the content pass so a regression in fetching cannot mask a content regression.
4. **D6** waits on the brand decision (D-018, due 2026-12-15). **D9/D10** are copy-only and can ride with step 2.

---

## Track A — the root site carries the logo

| # | Task | Files | Acceptance |
|---|------|-------|------------|
| A0 | Pick the wordmark treatment: emblem + live text (default) vs full baked lockup | decision | owner one-liner |
| A1 | Derive `emblem` (square, transparent) and `lockup` (full art, transparent) from `heraldfox-final.png` | `apps/web/public/brand/` | both trim clean at 512 px wide, no white fringe |
| A2 | Masthead: emblem at 32 px + "HeraldFox" in `--lb-font-display` 21 px, 700 | `components/lobby/shell.tsx`, `lobby.css` | renders in EN and ES, no layout shift at 360 px |
| A3 | Lobby footer: same emblem, 24 px, beside the wordmark | `shell.tsx` (`LobbyFooter`) | footer link still has one accessible name |
| A4 | Alt/aria: decorative marks `aria-hidden`, the brand link keeps `aria-label` | both | axe 0 on `/`, `/es`, `/services` |
| A5 | `og:image` for the apex (lockup on paper) — optional, same pipeline | `app/opengraph-image.tsx` | preview renders 1200×630 |

**Why not the full lockup in the masthead:** at 36–40 px tall the baked "HeraldFox" is ~7 px of serif — illegible, and the black banner fights the paper palette. The emblem reads at 32 px; the wordmark has to be live text. Measured from the source PNG: art bbox `x 140–1401, y 4–922`; the banner starts at `y ≈ 610`, so the emblem crop ends there.

---

## Track B — favicons on every host

| # | Task | Files | Acceptance |
|---|------|-------|------------|
| B1 | Build the icon tile: emblem on `#0b1220` rounded 18 %, 12 % padding (16 px legibility beats a bare transparent fox) | `apps/web/public/brand/icon-tile.png` | 16 px still shows a fox, not a smudge |
| B2 | Emit `src/app/favicon.ico` (16/32/48), `src/app/icon.png` (512), `src/app/apple-icon.png` (180, opaque) | `apps/web/src/app/` | `<link rel="icon">` emitted once per document |
| B3 | Confirm per-host behaviour: one icon for apex + 11 subdomains, `metadataBase` already per request | `app/layout.tsx` | `curl -s https://<host>/ | grep icon` on 3 hosts |
| B4 | Optional phase 2: per-desk icon via a route handler keyed on host | `app/icon/route.tsx` | only after B3 ships |

Next 15 auto-discovers `icon.*`/`apple-icon.*` in `app/`; no `metadata.icons` entry needed. Keep the middleware exclusion at `middleware.ts:188`.

---

## Track C — fetcher access and safe fetching

**Verdict first.** Access is not the current problem: 51 feeds polled, 3 errors, 0 blocks, 6,440 items over 78 runs. The problem is that nothing in the client would survive a publisher deciding to push back, and the identity it presents is not real. So yes to a safe-fetching layer — but scoped to what a feed reader needs, not a scraper's toolkit.

**Pushback on copying pizote/fun wholesale.** `fun/app/acquisition/http.py` sends a Chrome UA and browser `Sec-Ch-Ua` headers to get past bot walls; that is correct for scraping court records, and wrong here. For RSS, an honest crawler UA with a real contact URL, robots compliance and backoff is both more durable and legally cleaner. Copy the pacing, not the disguise.

What is worth porting, by source:

| Pattern | Where it exists | Take it? |
|---------|-----------------|----------|
| robots.txt check + `Crawl-delay` honoured | `fun/.../http.py:515-560` | yes |
| per-host pacing with ±20 % jitter, hourly cap | `pizote/.../politeness.py:33-46`, `fun/http.py:440-500` | yes |
| `Retry-After` as a cooldown floor | `pizote/politeness.py:71,233-258`, `fun/http.py:390-430` | yes |
| failure streak → exponential backoff → breaker | `pizote/politeness.py:44-46` | yes |
| challenge-page detection (200 + WAF body) | `fun/http.py:44-72` | yes, cheap insurance |
| browser UA spoofing | `fun/http.py:115` | **no** |
| egress-region gate / VPN | `fun/.../egress.py` | no — no jurisdiction requirement here |

| # | Task | Acceptance |
|---|------|------------|
| C0 | Real bot identity: `HeraldFoxBot/1.0 (+https://heraldfox.com/bot)` from settings, one constant, both fetchers | one string, no `example` domain left |
| C1 | robots.txt: fetch once per host/day, cache in Redis, honour `Disallow` and `Crawl-delay` | disallowed feed → `blocked` outcome, no request to the feed |
| C2 | Per-host ledger in Redis: min interval, hourly cap, jitter, failure streak, breaker | 2 feeds on one host never fire inside the interval |
| C3 | `429`/`503`: honour `Retry-After`, escalate per streak, never retry immediately | unit test with a 429 then a 200 |
| C4 | Retry budget: one retry for a dead socket only; no retry loops | test asserts one attempt on 429 |
| C5 | Response hygiene: `Content-Type` must be xml/rss/atom, reject `text/html` challenge bodies | test: 200 + HTML → `blocked` |
| C6 | Pin the validated IP: connect to the address `_resolve_is_public` approved (closes the rebinding window at `fetcher.py:51-55`) | test: host resolving twice to different IPs uses the first |
| C7 | Retire the two broken sources or fix them | `verify-sources` exit 0, 0 stale > 45 days |

Detail and test matrix: `.work/features/fetch-safety/20261109-SPEC.md`.

---

## Track D — ten content improvements

Each row: what the reader sees now (measured), what changes, how it is proven. All counts come from the 676-article dump.

| # | Finding | Change | Proof |
|---|---------|--------|-------|
| D1 | **Two shapes, no habit.** 30 % contain a "for professional readers…" clause, 43 % have no consequence clause at all (term scan). | One shape: *what happened → the detail that decides it → what changes for the reader, only if the source says so.* Encode in the prompt, enforce in `validate_summary`. | 100 % of new summaries match the shape; spot-check 20 |
| D2 | **Stock tail is readable as machine copy.** Exact 6-grams repeat: "for professional readers the takeaway is" ×5, "the move signals" ×5, ES "resulta relevante para los profesionales del" ×4. | Banned-phrase list in the validator (EN + ES), return `retry` on hit. | 0 hits across a fresh 50-summary sample |
| D3 | **Openers bury the actor.** 20 % start "A/An/The", 0 % start with a number, median first sentence 160 chars, 272 sentences ≥30 words. | First sentence: actor + action + the number/date when the source has one; ≤25 words. Cap the summary at 3 sentences / 520 chars. | median first-sentence ≤25 words; 0 "A/An/The" openers in the sample |
| D4 | **Vague verbs carry the meaning.** "signals" 16 %, "highlights" 9 %, "matters" 20 %, "readers" 11 %. | Ban `signals/highlights/underscores/matters to` as the meaning verb; require a concrete consequence (who does what, by when). | 0 banned verbs in the sample; reviewer reads 10 and cannot ask "so what" |
| D5 | **Numbers get dropped.** Only 41 % of summaries contain a digit; a 9.6 % tonnage move is the most quotable fact in its story. | If the title or excerpt carries a number, the summary must carry one. Validator: digit present when source digits exist. | 100 % compliance on items whose excerpt has a number |
| D6 | **Three brand strings in one product.** The wordmark reads "HeraldFox", the apex copy "Herald Fox" (`lobby.brand.name`), channel headers and `meta.siteName` "System News"; taglines differ too. | One brand value, driven by the asset, used by `brand.name` and `meta.siteName`. | one string in both catalogs; grep finds no "System News" in `src/` |
| D7 | **Phantom references.** The KEV digest item says "see URL in Notes"; the public page strips URLs, so the pointer goes nowhere. | Forbid "see link/URL/notes" in generation; render the source link explicitly instead. | grep the two issues: no such phrase; the source link is on the page |
| D8 | **Machine metadata as a standfirst.** `_standfirst()` emits "12 dated changes. Scope: global. Source checked 2026-11-04." | Human line ("12 federal rule changes this month, checked 4 November"); scope becomes a chip. | read the built issue: no "Scope:", no ISO date |
| D9 | **The empty-summary state says "AI" twice.** 27/676 have no summary; the page shows "From the publisher" + excerpt + "No AI summary is available" under an "AI summary" eyebrow. | One block, label "Summary" / "Resumen"; one quiet fallback line, only when used. | screenshot of a no-summary article, EN + ES |
| D10 | **The 404 promises seven days; retention is 30.** `article.notFoundBody` in both catalogs. | "may have left the 30-day archive" or drop the number. | grep both catalogs; no "seven"/"siete" |

**Two more worth doing if the list is reopened:** channel names are long in sentence position ("Back to Legal Services & Corporate Governance") → add a short display name; and 6 of 11 taglines end "— in plain language" / "en lenguaje claro" → differentiate.

**Content the ten do not touch:** the 649 existing summaries stay as they are unless re-summarised. Re-summarising 649 items costs AI budget; `refresh --full-reset --confirmation RESET` on one channel is the cheap trial (see D-trial below).

---

## Task board

| Id | Track | Depends on | Size |
|----|-------|-----------|------|
| A0 | decision | owner (decision 2) | XS |
| A1–A4 | A | A0 | S |
| B1–B3 | B | A1 | S |
| C0 | C | decision 1 (contact URL) | XS |
| C1–C7 | C | C0 | M |
| D1–D5 | D | — | M |
| D6 | D | owner (D-018) | S |
| D7–D10 | D | — | S |
| D-trial | D | D1–D5 | S: `python -m news_api.cli refresh --industry logistics --full-reset --confirmation RESET`, then read 20 |

**Verification for the whole session**

```bash
# api
docker compose --env-file .env.dev -f docker-compose.dev.yml exec api bash -c "cd /app && ruff check . && ruff format --check . && mypy src && pytest -q"
# web
docker compose --env-file .env.dev -f docker-compose.dev.yml exec web bash -c "cd /app && pnpm lint && pnpm exec tsc --noEmit && pnpm check && pnpm build"
# after build
docker compose --env-file .env.dev -f docker-compose.dev.yml exec web bash -c "cd /app && pnpm test"
```

---

## Decisions (answered 2026-11-09)

1. **Bot contact URL** (C0): `https://heraldfox.com/bot`, with a short crawler page. Ship the page in the same PR as C0.
2. **Wordmark treatment** (A0): emblem + live text, as recommended. The masthead reads the existing `lobby.brand.name` ("Herald Fox"); the spelling itself stays with D-018.
3. **Re-summarise policy** (D-trial): wait for the next natural refresh. No forced `--full-reset`; read the first natural batch after D1–D5 land.
4. **Brand string** (D6): still open, D-018 due 2026-12-15. This session does not rename anything.

## Risks

- **Re-summarising shifts the desk brief, not the rankings.** Scoring runs on title/excerpt/trust before summarisation (`articles/domain/models.py:25-45`); the brief reads summaries, so brief text changes. Low.
- **Per-host pacing slows a full refresh.** 52 feeds × 2/day is 104 requests; a 5 s floor per host costs nothing at that volume because most hosts carry one feed. Verify with the run duration before/after.
- **robots.txt on a news site can disallow the feed path.** That has to be a hard skip, not a warning — report it as a source error so the operator sees the reason.
- **Favicon on 11 subdomains** depends on the browser caching per origin; expect to hard-refresh during verification.

## Next action

Answer decisions 1–2, then start Track A+B: add an asset script under `apps/web/scripts/` that derives the emblem, lockup and icon tile from `.work.ui/references/heraldfox-final.png`, then wire the masthead.
