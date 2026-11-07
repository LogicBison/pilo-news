# Plan — the Herald Fox lobby (`heraldfox.com`)

**What it is:** the apex site. A professional lobby that lists every live desk, carries the same free reader offers, and sells two services: news services and content generation. This document is the business plan, the data/routing contract, the design direction, and the build handoff for `@x-director` / `@ui-director`.
**Status:** **Implemented 2026-11-07.** H1-H10 shipped and verified; see §15 for the as-built record and the three deviations. Copy deck: `.work.biz/strategy/20261107-lobby-copy.md`.
**Needs:** U1 (brand name ratification — this plan says "Herald Fox"), D-005 (named reviewers, gates the content-generation claim), D-002 (email delivery, gates any email promise), and one new decision on service pricing (D-016, proposed at the end).

---

## 1. The job of the page

The apex currently redirects to one desk (`app/page.tsx` → `/{SN_DEFAULT_INDUSTRY}`). That wastes the only surface where a visitor arrives without having chosen a topic, and it hides the two things nobody can find today: that there are eleven desks, and that the same machinery is for sale.

The lobby does three things in this order:

1. **Route a reader** to a desk in under ten seconds, without asking for an email.
2. **Prove the machinery** — the sources, the review gate, the two languages — because that proof is also the sales argument.
3. **Convert a buyer** into one scoping call, for either a news service or a content-generation engagement.

One page. Two audiences. The sequence matters: the buyer reads the proof only if the reader experience is real, so the desk directory comes before the services band.

## 2. Two audiences, one page

| | Reader | Buyer |
|---|---|---|
| Who | a professional in one of the eleven fields | an association, firm, fund, or agency that needs industry news under its own name |
| Arrives with | "what happened in my field" | "we cannot staff a newsroom" or "we need a document we can hand a client" |
| Wants | the desk, the brief, the reference issue | scope, cadence, who signs it, what it costs |
| Conversion | enters a desk, or takes a free offer there | one scope call |
| Copy register | desk editor, plain, specific | procurement, plain, specific |

The failure mode to avoid: a services brochure with news links in the corner. The desks are the product demo. If a visitor sees one desk do real work, the services band reads as "the same thing, for us", not as an agency pitch.

## 3. What the lobby is not

- **Not a second capture surface.** Every free reader offer lives on its desk. The lobby links to it. One capture point per offer means one consent record, one rate limit, one form to maintain, and attribution that says which desk earned the lead. A parallel lobby form would split the funnel and double the surface for no extra leads.
- **Not a channel.** It has no industry, no partners, no consultation routing. Free reader offers are inherited from the desks, not re-listed as separate products.
- **Not a price list.** No public prices. Services are scoped in a call and bought as a fixed pilot (see §11).
- **Not an email trap.** No interstitial, no modal on entry, no scroll-hijack.

## 4. Offer architecture

Two families, both visible, kept visually separate so nobody mistakes the free desk for the paid service.

### 4.1 Family A — free, per desk (inherited, not duplicated)

Sourced from `GET /v1/industries/{slug}` → `offers` (`brief`, `asset`, `question`, `consultation`), which is already live per channel (measured 2026-11-07: `stem-cell` = brief + question + consultation, no asset).

| Offer | Where the lobby sends the reader | Lobby label |
|---|---|---|
| Weekly brief | the desk that offers it (`offers.brief === true`) | "Get the weekly brief" |
| Reference issue | the desk's `/references` archive, filtered to desks with `offers.asset` | "Read a reference issue" |
| Ask one question | the desk's article/home rung (`offers.question`) | "Ask one question" |
| Specialist routing | the desk's consultation form (`offers.consultation`) | "Talk to a specialist" |

A desk that does not offer one of these is not shown for that offer. The card CTA becomes a desk picker when more than one desk qualifies — no form on the lobby.

**Resolved 2026-11-07:** the brief is capture-only and delivery is still open (D-002), so the lobby ships **three** offer cards — reference issue, ask one question, specialist routing — and the brief card is held in the copy deck until delivery works. The desk plates keep their "Brief" chip wherever `offers.brief` is true, because the offer is real at the desk; only the lobby's own card is withheld. With D-017 (no lobby capture) this also removes the only reason to put an email field on the apex.

### 4.2 Family B — paid, for organizations

Two services, one pipeline, one review gate.

| Service | What the buyer gets | Who it replaces |
|---|---|---|
| **News service** — a desk under their name | one or more desks run for them: sourced daily or weekly, summarized, reviewed, published under their brand in EN/ES, delivered as a page, RSS, email, or JSON | an in-house editor nobody has budget for |
| **Content generation** — commissioned reference documents | dated, cited documents built from primary records: regulatory calendars, rule-change logs, recall trackers, queue and trial digests. Signed by a named reviewer | a research analyst rewriting the same document every month |

Both reuse: the ingestion pipeline (52 feeds, measured), the DeepSeek summary stage, the reviewer gate on reference issues, the EN/ES catalogs, and the public API. The marginal cost of a new desk is a deployment profile (`docs/adding-an-industry.md`), which is the honest sales story: we are not inventing a product, we are renting capacity that already runs.

**Content-generation constraint (blocking):** the copy claims a named reviewer signs each document. D-005 (reviewer names) is still open. Until a name exists, the page must say "reviewed before publication" and the reviewer field stays "to be assigned" — or the service is not offered.

## 5. Page architecture

Eleven sections. Section numbers are visible (the wayfinding spine), so an operator can point at "section 03" in a review.

| # | Section | Purpose | Data | Primary CTA |
|---|---|---|---|---|
| 00 | Masthead | brand, "11 desks", language switch, services link | static | Services |
| 01 | Hero | the promise + two doors | desk count, locales | "Follow a desk" / "Commission a desk" |
| 02 | Live board | arrival-board card: desk, cadence, locales | 11 desks | — (proof, not a link) |
| 03 | Directory | all desks as plates | desk list + offers + taglines | "Enter the desk" |
| 04 | Free offers | three reader offers, one card each (the brief card is held until D-002) | offer availability | "Choose a desk" |
| 05 | How a desk is built | source → summarize → route, three steps | static | — |
| 06 | Services | the two paid services | static | "Request a scope call" |
| 07 | Engagement | scope → pilot → review gate → publish | static | "Request a scope call" |
| 08 | Questions | 8 FAQ items | static | — |
| 08b | Contact | one message form, same fields and endpoint as every channel contact page, no industry attached (D-020) | `/v1/contact` | Send message |
| 09 | Two doors | final split CTA | static | both |
| 10 | Footer | desk list (SEO), legal, RSS, language | desk list | — |

Sections 01–03 are above the fold on desktop only in the sense that the hero *is* the directory entrance — the plates start within the first viewport on a 900px-tall screen.

## 6. Dynamic data contract

### 6.1 What exists today (measured 2026-11-07)

- `GET /v1/industries` → 11 rows: `slug`, `name`, `locales`, `theme_summary {primary, accent, layout}`, `code`. No tagline.
- `GET /v1/industries/{slug}` → adds `tagline`, `theme` (colors + fonts + layout), `offers {asset, brief, consultation, question}`, `cta` (localized headline/body/label), `disclaimer`, `timezone`.

The lobby needs `tagline` + `offers` per desk, which only exist per desk. That is 11 requests.

### 6.2 What to add (one endpoint, one round trip)

`GET /v1/desks?locale=en` — a read-only projection of the same rows, one call:

```json
{"data":[{"slug":"legal","name":"...","tagline":"...","locales":["en","es"],
          "accent":"#5b2333","layout":"editorial",
          "offers":{"brief":true,"asset":true,"question":true,"consultation":true},
          "fetch_interval_minutes":720,
          "latest_published_at":"2026-11-05T09:30:00Z"}],"meta":{"generated_at":"..."}}
```

`latest_published_at` comes from one indexed `max(published_at)` per industry — cheap, and it gives the live board an honest "last filed" per desk instead of a fabricated activity number. `fetch_interval_minutes` already exists on `industries` (migration 013) but is not in any public payload; the board's "Updates" column needs it, otherwise the column reads the deployment default and lies about a desk with a custom cadence. Field name `desks` rather than `industries` because this is the lobby's shape, not the channel API's.

Until it exists, the lobby fetches the 11 detail endpoints in parallel behind a 300-second revalidate. Acceptable for launch; the endpoint is a 40-line addition and removes 10 round trips.

### 6.3 Not needed

No live item counts (`meta.total` does not exist), no cross-desk feed, no ranking. The lobby stays honest: cadence and last-published are facts; a "trending" sort would be invented.

## 7. Routing and platform changes

| # | Change | Where | Why |
|---|---|---|---|
| R1 | apex `/` renders the lobby instead of redirecting | `apps/web/src/middleware.ts` (drop the apex `/` → `/{slug}.domain` redirect) + `app/page.tsx`, `app/[locale]/page.tsx` | it is the only top-of-funnel surface |
| R2 | `/services`, `/es/services`, `/privacy`, `/terms` at the apex | `app/[locale]/services/page.tsx` etc. | services need a page that can be linked and indexed alone |
| R3 | reserve `services`, `pricing`, `login` as channel slugs | `RESERVED_SUBDOMAINS` in `lib/hosts.ts` + the slug validator in `channels` | a static segment must never collide with a desk |
| R4 | apex sitemap lists the lobby, not nothing | `app/sitemap.ts` | today the apex returns `[]` when subdomains are on (ADR 015); the lobby makes it a real site |
| R5 | robots on the apex: allow `/`, keep `/admin` out | `app/robots.ts` | same reason |
| R6 | `GET /v1/desks` | `channels/http/routes.py` | §6.2 |
| R7 | funnel surface for cross-desk events | migration `016_cta_surface.sql`: `cta_events.industry_id` nullable + `surface text`, endpoint accepts `industry: str \| None` and `surface` | the lobby's service CTA has no industry; today `CtaEventRequest.industry` is required (min 2 chars) so the services funnel cannot be measured at all |
| R8 | `desk_enter` event | `CtaEventRequest.event` literal + `apps/web/src/lib/analytics.ts` | which desks the lobby actually moves, per desk |
| R9 | shared header/footer for the apex | `components/lobby/*` | `Header`/`Footer` are channel-scoped (`Industry` prop) |

R7 is the only schema change and it is small. Without it the lobby launches with a blind services funnel — the one funnel that has a sales quota attached.

## 8. Design direction

Concept: **the building, not the publication.** The eleven channels are editorial publications with photographic skins. The lobby is the ground floor: wayfinding signage, a directory board, a brass number by each section. Ink and paper, one signal color, no photography. It should feel like the front desk of a serious organization that happens to publish.

### 8.1 Palette (measured)

| Token | Hex | oklch | Use | Measured |
|---|---|---|---|---|
| `paper.base` | `#F3EEE4` | `oklch(94.5% 0.017 85)` | page canvas | — |
| `paper.inset` | `#E8E1D3` | `oklch(90.7% 0.021 85)` | wells, plate footer, board rows | ink 13.95:1 |
| `paper.raised` | `#FBF8F2` | `oklch(97.7% 0.010 85)` | plates, cards | ink 17.12:1 |
| `ink.primary` | `#12161C` | `oklch(21.0% 0.014 258)` | text, services band background | on paper 15.69:1 |
| `ink.muted` | `#4A4438` | `oklch(36.6% 0.018 80)` | supporting copy on paper | on paper 8.35:1 |
| `ink.inverse` | `#F3EEE4` | — | text on ink | on ink 15.69:1 |
| `ink.inverse-muted` | `#B7AE9E` | `oklch(74.0% 0.022 80)` | supporting copy on ink | on ink 8.26:1 |
| `signal` | `#B33A22` | `oklch(48.4% 0.150 32)` | primary button fill, focus ring, active section | on paper 5.12:1 · paper on signal 5.12:1 |
| `brass` | `#C9A227` | `oklch(73.2% 0.130 88)` | section numerals, hairlines on ink | on ink 7.50:1 |
| `live` | `#256B4F` | `oklch(46.0% 0.080 158)` | "updated" dot + label | on paper 5.51:1 |

Rules: `signal` is a fill and a focus ring, never body text. `brass` never appears on paper as text. No hue from any channel skin is reused here — the lobby must not read as one of the desks.

### 8.2 Type

- Display: **Fraunces** (variable, OFL), optical size 72–96, weight 600, tight tracking (−0.02em) for the hero only.
- Text: **IBM Plex Sans** (OFL), 400/600, 17px base, 1.6 line-height.
- Numerals: Plex Sans tabular for the board and the section spine.
- Self-host both as WOFF2 subsets in `apps/web/public/fonts/` (latin + latin-ext for Spanish), loaded with `next/font/local`, `font-display: swap`, display face preloaded only. `font-src 'self'` already allows this; no third-party font call.
- Fallback stack with metric-compatible overrides so the hero does not shift: `Georgia, 'Times New Roman', serif` for display, `system-ui, -apple-system, 'Segoe UI', sans-serif` for text.
- Scale: 76/52/34/26/19/17/15/13 px (display-xl, display, h2, h3, lead, body, small, micro).

### 8.3 Layout

- 12 columns, `max-width: 1240px`, 24px gutters, 96px section rhythm.
- **Wayfinding spine** (desktop ≥1024px): a fixed 88px left rail with section numerals `01…06`, a 2px brass progress line, current section in `signal`. On mobile it collapses to a sticky chip row under the masthead.
- **Hero**: 12 columns as 7/5. Left = eyebrow, H1 (3 lines max), lead, two doors. Right = the live board card.
- **Live board card** styled as a departures board: 4 visible rows, `paper.inset` background, tabular numerals, brass hairlines, rows `DESK · CADENCE · LANGS · UPDATED`, a `live` dot with the text label "updated on a schedule" beside it (never color alone).
- **Directory**: 3 columns × 4 rows (last row 2), 16px gaps. Each **desk plate** is a full-width link: 6px left bar in the desk's own `theme_summary.primary`, name in 600/19px caps-tracked 0.04em, tagline 15px muted clamped to 2 lines, footer row of chips (offer kinds + `EN`/`ES`) on `paper.inset`, arrow bottom-right. Hover: bar 6→10px, plate lifts 2px, arrow translates 4px. Focus: 2px `signal` ring with 2px offset.
- **Services band**: full-bleed `ink.primary`, `ink.inverse` text, brass hairlines, big numerals `01/02` for the two services. Two cards side by side on desktop, stacked on mobile. One form entry point below the cards (contact endpoint, §7).
- **Section headers**: brass numeral + hairline rule with tick marks every 24px (CSS `repeating-linear-gradient`, no image).
- **Final doors**: two equal panels, one paper one ink, each a whole-card link.

No imagery, no stock photos, no illustration. One CSS-drawn motif: the wayfinding spine. That keeps the lobby fast (target: no image bytes above the fold) and visually distinct from the eleven photographic desks.

### 8.4 Motion

150ms `ease-out` on plate hover and section reveal; the spine progress uses `scroll-driven` where supported, otherwise a throttled scroll listener. `prefers-reduced-motion: reduce` disables all transforms and keeps opacity only. Nothing autoplays.

### 8.5 Accessibility

- Contrast: every pair above is ≥4.5:1 for text (measured, §8.1). `signal` at 5.12:1 is text-safe but used as a fill only.
- The full desk plate is one link with an accessible name of the desk name + tagline.
- Board rows are a `<table>` with `<caption class="sr-only">` — they are tabular data, not decoration.
- Focus order: masthead → hero doors → board (non-interactive) → plates → offers → services → FAQ → final doors.
- Target size ≥44px for every control; plates are ≥120px tall.
- Language switch preserves the current path, same as `LocaleSwitch`.
- Every section heading is an `<h2>` under the single `<h1>`; the spine numerals are `aria-hidden`.

## 9. Measurement

Existing events take a free-form `placement` and a required `industry`; the lobby is cross-desk, so §7 R7/R8 are prerequisites for a complete read.

| Event | placement | industry | Meaning |
|---|---|---|---|
| `cta_impression` | `lobby-desk` | the desk | plate entered the viewport |
| `cta_click` | `lobby-desk` | the desk | plate clicked |
| `desk_enter` | `lobby-desk` | the desk | landing on the desk from the lobby (Referer check) |
| `cta_click` | `lobby-services` | null, `surface=lobby` | service CTA clicked |
| `lead_submit` | `lobby-services` | null, `surface=lobby` | contact form submitted |

Primary KPI: **qualified service inquiries per 100 lobby visits** — target ≥2 (assumption; no baseline exists, U10 open). Secondary: desk click-through by desk (which desks earn a lobby visitor), brief signups referred from the lobby, and bounce by section depth.

Read-out day 14 and day 28. Keep/kill rule written before launch: if service inquiries are <1 per 100 visits at day 28 with ≥500 visits, the services band moves to `/services` only and the lobby reverts to a pure directory.

## 10. SEO and structured data

- `<title>` EN: "Herald Fox — eleven industry desks for professionals"; ES mirrored.
- One `<h1>`, section `<h2>`s, descriptive anchors (`/services` not `/s`).
- `hreflang` en/es/x-default on every apex page, same pattern as `lib/seo.ts`.
- JSON-LD: `Organization` (Herald Fox, `news@heraldfox.com`), `WebSite` with `potentialAction: SearchAction` → `/{desk}?q=` is not a single target, so use `WebSite` + `ItemList` of desks only, `Service` × 2 on `/services`.
- Desk list in the footer as real links — the lobby becomes the internal-link hub that pushes authority into eleven young subdomains.
- No `FAQPage` schema on the lobby until the answers are stable (they will change with D-002/D-005); add it when the copy freezes.

## 11. Pricing (proposal — not on the page)

No public prices. Anchors for the sales conversation, all `assumption` until a pilot closes:

| Package | Shape | Anchor |
|---|---|---|
| Pilot desk | 4 weeks, one desk, 3 issues/week, EN only | USD 1,500–2,500 fixed |
| News service retainer | 1–3 desks, daily or weekly, EN+ES, branded page + RSS + email | USD 2,500–6,000/month |
| Commissioned document | one dated, cited reference issue | USD 1,200–3,500 per issue |
| White-label desk launch | new vertical, profile + sources + skins + 30 days of content | USD 6,000–9,000 one-off |

The page says "scope call, then a fixed pilot" and nothing else. Publishing a price before a single pilot has closed would anchor the wrong number and invite comparison to content mills.

**What may not be sold:** only document types the feasibility work supports. `strategy/20261105-product-feasibility-verification.md` §4 rules the logistics rate index out — it cannot be built from a stable public source. The services band lists document types generically for that reason; a scope call that names a rate index would be selling something the review gate would have to refuse.

## 12. Launch gates

Ship the lobby only when all six are true. Each is a hard gate, not a preference.

| # | Gate | Current state |
|---|---|---|
| G1 | a reader offer can actually be fulfilled — either D-002 delivery is live, or the brief card is held | **resolved 2026-11-07**: brief card held; three fulfilable offers ship |
| G2 | content-generation copy names a reviewer, or drops the signature claim | not ready (D-005 open) |
| G3 | `GET /v1/desks` exists, or the 11-request fallback is behind a 300s revalidate and measured under 300ms p95 | not built |
| G6 (soft) | at least one published reference issue, or the asset card ships as a waitlist link | 0 issues on 2026-11-07 — see the copy deck's variant |
| G4 | the services funnel is measurable (R7) | not built |
| G5 | apex `/` no longer redirects, and `/`, `/es`, `/services`, `/es/services` are in the sitemap and pass axe with 0 critical/serious | not built |

G1 and G2 are business gates; G3–G5 are engineering gates. G1 is the one that decides whether this page ships this month.

## 13. Handoff to `@x-director` / `@ui-director`

Ordered so each step is verifiable alone.

| # | Task | Owner | Files | Acceptance |
|---|---|---|---|---|
| H1 | `GET /v1/desks` + OpenAPI snapshot + contract test | x (api) | `channels/http/routes.py`, `tests/contract/`, `docs/api/openapi.v1.json` | 11 rows, `tagline` + `offers` + `latest_published_at`, p95 < 50ms |
| H2 | migration 016: nullable `industry_id`, `surface`; `desk_enter` event | x (api) | `migrations/016_*.sql`, `publishing/http/cta.py`, `publishing/http/funnel.py` | funnel read-out groups by `surface`; existing channel rows unchanged |
| H3 | apex routing: lobby at `/`, `/services`, `/privacy`, `/terms`; reserve slugs | x (web) | `middleware.ts`, `lib/hosts.ts`, `app/[locale]/…` | `/` renders the lobby in both locales; `stem-cell.heraldfox.com/` still a desk; no slug collision |
| H4 | design tokens + `lobby` surface skin | ui | `.work.ui/design-system/tokens.json`, `app/lobby.css` | palette in §8.1 as tokens; contrast re-measured in the report |
| H5 | components: `Masthead`, `WayfindingSpine`, `DirectoryBoard`/`DeskPlate`, `LiveBoard`, `OfferCards`, `ServiceBand`, `ProcessSteps`, `LobbyFaq`, `FinalDoors`, `LobbyFooter` | ui | `components/lobby/*` | axe 0 critical/serious; 3 real widths; no CLS from fonts |
| H6 | copy into `messages/en.json` + `es.json`, no hardcoded strings | ui + biz | `apps/web/src/messages/*.json` | `pnpm check` passes (key parity) |
| H7 | service inquiry form → `POST /v1/contact` with `source_page=/` and no industry | x (web) | `components/lobby/ServiceForm.tsx` | row lands in admin contact tab with `source_page=/` |
| H8 | analytics: `desk_enter`, `surface`, placements | x (web) | `lib/analytics.ts` | funnel shows `surface=lobby` rows |
| H9 | e2e: lobby spec (both locales, every plate links to a live desk, form validation) + axe on 4 apex URLs | ui + x | `e2e/lobby.spec.ts` | green on a production build |
| H10 | sitemap/robots/hreflang for apex | x (web) | `app/sitemap.ts`, `app/robots.ts` | apex sitemap lists `/`, `/es`, `/services`, `/es/services` |

## 14. Risks and open decisions

| Risk | Severity | Mitigation |
|---|---|---|
| The lobby promises the weekly brief while delivery is missing | high | G1; the brief card is conditional on D-002 |
| Content-generation copy overclaims a reviewer | high | G2; copy has a "no named reviewer yet" variant |
| Services funnel unmeasurable → no way to kill the band | medium | R7 before launch, else launch without the band and with `/services` only |
| Apex competes with the desk subdomains for the same query | medium | the lobby targets the *network* query ("industry news, eleven desks"), desks keep the vertical queries; no desk copy duplicated on the apex |
| Eleven outer-plate calls on a cold cache | low | 300s revalidate + H1 |
| New fonts regress LCP | low | two subsets, preload display only, system fallback metrics |

**Decisions — approved by the owner 2026-11-07** (rows appended to `.work.biz/decisions/DECISIONS.md`):

- **D-016** — no public prices on the lobby; services sold as a fixed pilot after a scope call. Reversible, review 2027-01-15.
- **D-017** — the lobby does not capture reader emails; every free offer is served on its desk. Reversible, review 2027-01-15.
- **D-018** — brand at the apex is "Herald Fox" (ratifies U1 for the lobby surface only; channel names stay as they are).
- **D-019** — services are sold under the same review gate as the desks: no document publishes unattributed.

Consequence of D-017 now in force: the lobby has no email field, no modal, and no capture of its own. Every reader conversion happens on a desk.

## 15. As built (2026-11-07)

All ten handoff tasks shipped in one pass.

| Task | Landed |
|---|---|
| H1 | `GET /v1/desks` (`channels/http/routes.py`, `latest_published_by_industry` in the repo), contract tests, OpenAPI snapshot regenerated |
| H2 | migration `016_cta_surface.sql` (nullable `industry_id`, `surface`, `desk_enter`), funnel read-out groups by surface, admin console labels lobby rows `lobby:all` |
| H3 | apex `/` renders the lobby, `/services`, `/privacy`, `/terms` (+ `/es` twins); `services`/`pricing`/`privacy`/`terms` reserved in both the API validator and the edge list; ADR 016 |
| H4 | `components/lobby/lobby.css`: the measured palette from §8.1, scoped to `.lb-root` |
| H5 | masthead, wayfinding spine, live board, directory + desk plates, offer cards, method steps, services band, process, FAQ, two doors, footer |
| H6 | 140 `lobby.*` keys in EN and ES, parity enforced by `pnpm check` |
| H7 | `ServiceForm` posts to `/v1/contact` with no industry; the row lands in the admin contact tab with `source_page` |
| H8 | `desk_enter` + `surface` in `lib/analytics.ts`; plates fire `cta_click` and `desk_enter` before leaving the apex |
| H9 | `e2e/lobby.spec.ts` (9 tests) and six apex URLs added to the accessibility suite |
| H10 | apex sitemap lists `/`, `/es`, `/services`, `/services` ES, `/privacy`, `/terms`; robots allows the apex |

Gates: G1 resolved by holding the brief card, G2 by withholding the reviewer
signature line, G6 by shipping the asset card as a link to the desk that owns it,
G3 by the endpoint, G4 by migration 016, G5 by the routing work.

**Deviations from the plan, and why**

1. **No webfonts.** §8.2 called for self-hosted Fraunces + IBM Plex Sans. This
   environment cannot fetch them, and committing binaries I cannot verify is
   worse than a systems stack. The display face is Georgia with a metric-safe
   fallback; swapping `--lb-font-display` and `--lb-font-body` is the whole
   change when the files land.
2. **The inquiry form is on `/services` only.** The plan allowed it in the band.
   One form, one anchor (`#scope`), one consent surface — the lobby stays a
   router (D-017).
3. **`/privacy` and `/terms` carry lobby-specific copy**, not the channel pages'
   text, because the channel copy still says "System News" and D-018 has not
   renamed the network yet. When it does, merge the two.

**Review round (owner screenshot, 2026-11-07).** Four defects found after the
first pass and fixed, each with a regression test:

1. `.lb-root a { color: inherit }` beat `.lb-btn` and `.lb-skip` on specificity,
   so the primary CTA and the skip link were ink on ink. Replaced with a
   zero-specificity `:where(.lb-root) a`.
2. The masthead, spine and footer section links were page-relative (`#directory`),
   so on `/services` and the legal pages they pointed at sections that do not
   exist there. They now resolve against the lobby root (`/#directory`).
3. `lobby.final.readerBody` was rendered without its values, printing the literal
   `{desks}`. A test now fails on any leaked placeholder on any apex page.
4. Form fields shared the card's fill and a 16% hairline. Fields now sit on a
   brighter fill with a 45% edge and a subtle inset shadow.

**Second review round (2026-11-07, owner screenshot of the services band).**

- The band rendered unstyled and the CTA had no label in that capture; the
  current build measures `background: rgb(18,22,28)`, `padding: 56px 44px`, and
  the label is the inverse ink — the capture predates the anchor-specificity fix.
  A colour audit now walks **every text node** on the six apex pages: 256 / 256 /
  84 / 84 / 42 / 42 nodes, **0 failures below 4.5:1**, and the band's own 20
  nodes pass, on dev and on the production image.
- **Real defect found in the same capture:** the intro read "the 0 desks" because
  `ServicesPage` printed `desks.length` after a failed API call. The count is now
  `null` when the list did not load and the copy drops the number
  (`lobby.services.introFallback`, `lobby.footer.blurbFallback`).
- **Disabled channels:** verified end to end — with `retail` disabled,
  `/v1/desks` returns 10 slugs, the lobby renders 10 plates, the sitemap is silent,
  and re-enabling restores 11. Locked by
  `tests/contract/test_desks.py::test_a_disabled_channel_leaves_the_lobby`.

**Contact form (owner instruction, 2026-11-07).** D-020 supersedes the
no-capture clause of D-017: the lobby now carries the same contact form every
channel page has — name, work email, phone, message, consent, honeypot — posting
to `/v1/contact` with no industry and `source_page=/`. Section 07, reachable from
the masthead, the spine and the footer. It is the only form on the apex outside
`/services`.

**Verified:** API 152 tests, ruff/mypy clean, OpenAPI snapshot current; web
typecheck + lint + 560-key catalog parity; production image built and served;
Playwright 111 passed on the production build (lobby, all 29 accessibility URLs,
public, layout) and 115 on dev with the admin specs (3 flaky, all retried green,
0 failed); `./bin/start.sh dev hosts` 14/14; a contrast sweep over every text node
on the six apex pages reports 0 failures below 4.5:1; all 26 internal links on
those pages return 200.

## Next action

Nothing in this plan. When a reviewer is named (D-005) publish the signature
line, and when delivery lands (D-002) restore the brief card.
