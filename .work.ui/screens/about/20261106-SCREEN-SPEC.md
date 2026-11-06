# About the desk — screen SPEC

**What it is:** screen SPEC for the about page of every channel — `/{industry}/about` and `/es/{industry}/about`. The page that answers three questions a reader asks before trusting the desk: who picks these stories, how, and what happens to my data.
**Status:** Implemented (2026-11-06) — built and verified; 78 Playwright tests pass on a production build
**Slug:** about
**Path:** `.work.ui/screens/about/20261106-SCREEN-SPEC.md`

## 1. Summary

A reader who is deciding whether to trust a headline lands here from the top nav About link, the footer, or a search result. The job is to leave with the method understood: approved feeds, language-aware scoring, AI summaries with a fail-open rule, and a desk reachable for corrections.

Today the screen is `apps/web/src/app/[locale]/[industry]/about/page.tsx` (85 lines): H1, two body paragraphs, a three-item "how the desk works" list, a contact line, `LeadForm`, `BriefSignup`, and a `TrustBlock` in a sticky aside. Three gaps show:

- **A trust page carries a number the config contradicts.** `about.how3` in both locales says "the seven-day window keeps the desk current"; every channel runs `retention_days: 30` (`apps/api/config/scoring.json:22` and all eleven deployment profiles).
- **Three asks on one page.** Lead form, brief signup and the contact link all compete. The M9 rule suppresses the brief where `cta.asset` is set on the channel home and article; about never received it.
- **No reading measure.** The body column has no max width, so the measure follows the layout column and runs past 65ch at `lg`.

This SPEC keeps the page's job narrow: explain the method, prove it with checkable statements, offer one primary action, and correct the copy.

## 2. Personas & jobs

| Persona | Job |
|---------|-----|
| Industry reader (P1) | Decide in under a minute whether this desk is worth reading |
| Publisher / source contact (P2) | Check the sourcing and correction policy before pitching a feed |
| Prospective lead (P3) | Confirm the desk is real before submitting the consultation form |

## 3. States

| State | Treatment |
|-------|-----------|
| Default | H1, mission paragraphs, how-the-desk-works list, contact line, lead form, brief (conditional), trust rail |
| Loading | none — server-rendered static copy; only the layout's degraded notice can appear |
| Empty | N/A — no list or collection on this page |
| Degraded API | layout `DegradedNotice`; the page still reads its copy and renders; never blank |
| Lead form success | in-place confirmation (`LeadForm` owns it) — this page adds no state |
| Lead form failure / 429 | `LeadForm` messages; the contact link remains the fallback |
| Brief suppressed | where `channel.cta.asset` is set, the brief block does not render at all |
| Permission denied | N/A — public screen |

## 4. Layout & hierarchy

| Region | Content | Notes |
|--------|---------|-------|
| App bar | inherited `Header` | no change to the shared header |
| Mission | H1 + two paragraphs | measure ≤65ch; serif H1; no card |
| Method | `h2` + three-item list, then the contact line | open block with a top rule; list markup, not styled paragraphs |
| Conversion | `LeadForm` (primary) + `BriefSignup` (conditional secondary) | full-width inside the main column; no side-by-side with the rail at `lg` |
| Rail | `TrustBlock` (what happens after a request) | sticky at `lg` only, `h-fit`; renders as the shipped `Card` |
| Footer | inherited | unchanged |

Breakpoints: `sm` 640, `md` 768, `lg` 1024, `xl` 1280. Single column on mobile in this order: mission → method → contact → lead form → brief → trust. The trust rail never precedes the mission on mobile.

## 5. Content

Copy lives in `apps/web/src/messages/{en,es}.json`; key sets are equal and CI-checked (`pnpm check`). Reused keys: `about.title`, `about.description`, `about.body1`, `about.body2`, `about.howTitle`, `about.how1`, `about.how2`, `about.how3`, `about.contact`, `trust.*` (via `TrustBlock`), `lead.*`, `brief.*`.

Required copy changes (both locales, no new keys):

| Key | Change |
|-----|--------|
| `about.how3` | drop the "seven-day window" claim; say the desk keeps a rolling window and can be refreshed by an operator. The real value is 30 days and is not exposed by the API, so the page does not state a number |
| `about.how1`, `about.how2`, `about.body1`, `about.body2` | keep — each is verifiable against code (language-scoped scoring, AI fail-open, no article bodies stored, no image rehosting) |

Rules: every factual claim on this page must be checkable against configuration or schema. No retention number, no story counts, no "trusted by" phrasing, no team names. One primary action; the brief is secondary and conditional.

## 6. Interactions

Focus order: skip link → emblem/home → nav → locale switch → H1 → body → method list → contact link → lead form fields → submit → brief fields → brief submit → trust rail.

- The contact line is a text link to `/{industry}/contact`; not a button, no modal.
- `LeadForm` and `BriefSignup` keep their own submit and validation behaviour; this page does not wrap them in extra chrome.
- No modals, no accordions, no tabs — the method list is short enough to read.
- Locale switch preserves the path (`/es/{industry}/about`).
- Sticky rail only from `lg`; it must not overlap the footer at any scroll position.

## 7. Data dependencies

- `GET /v1/industries/{slug}` — name, tagline, disclaimer, `cta` (drives the lead kind and the brief suppression). Shape lives in the domain SPEC; not restated here.
- `POST /v1/leads` via `LeadForm` (`placement="about"`) and `BriefSignup` (`placement="brief-about"`) — contract in `.work/features/industry-sites/20261105-SPEC.md` §R12/R17 and ADR 013.
- `retention_days` exists on the channel model (`apps/api/src/news_api/channels/domain/theme.py:114`) but is **not** in the `/v1/industries/{slug}` payload (`apps/api/src/news_api/channels/http/routes.py:28-42`). That is why §5 removes the number rather than rendering it; exposing the field is a separate API change.
- No new endpoint, no schema change, no analytics endpoint.

## 8. Tokens & components

| Component | Catalog status | Native waiver |
|-----------|----------------|---------------|
| SectionHeader | shipped | — (method `h2`, trust rail heading) |
| TrustBlock | pattern, shipped | — (renders `Card` + `Chip` + `SectionHeader`) |
| LeadForm | pattern, shipped | — (renders `Card`, `Chip`, `TextField`, `TextArea`, `SelectField`, `ConsentField`, `FieldError`, `Button`; owns its submit) |
| BriefSignup | pattern, shipped | — (renders `TextField`, `ConsentField`, `Button`; no `Card`) |
| Card | shipped | used by `LeadForm` and `TrustBlock` only; the mission and method sections add no box |
| TrustLine | shipped | inside `LeadForm`; the rail's expectation line if `TrustBlock` is ever replaced |

Tokens: `color.surface.base`, `color.surface.elevated` (rail card only), `color.border.subtle` (section rules), `color.text.primary`, `color.text.muted`, `color.focus.ring`, `font.family.serif`, `font.size.*`, `space.*`. No raw hex, no `px` literals; the measure is a `ch`-based max width.

`CATALOG.md` labels built primitives `shipped`; for the review gate that is `done`.

## 9. Accessibility

WCAG 2.2 AA.
- One `h1`; each section heading is `h2` via `SectionHeader`; the trust rail's steps are `h3` inside an ordered list (existing `TrustBlock` behaviour).
- The method block is a real `<ul>`/`<li>` list.
- Body measure ≤65ch at `lg`; line height from the type scale.
- Contact link has a visible focus ring and 44px target height.
- No motion beyond the 0.18s token transitions; `prefers-reduced-motion` honoured.
- Contrast from tokens only; the dark `cybersecurity` scheme is checked by `pnpm check`.

## 10. Analytics & observability

No page-level event. `LeadForm` and `BriefSignup` emit their existing `lead_form_start` / `lead_submit{result}` events with `placement="about"` and `placement="brief-about"`, which already reach `/v1/admin/funnel`. This SPEC adds no event and records no reader data.

## 11. Acceptance criteria

- [ ] One `h1`; the method and trust sections use `h2`; no skipped heading level.
- [ ] The body measure is 65ch or less at `lg` and above.
- [ ] Neither locale contains "seven-day"/"siete días" or any other retention number; `about.how3` reads as a rolling window.
- [ ] The mission block uses the channel's serif display for the H1 (brand typography); no hero art, no decorative band.
- [ ] Every claim in `about.body1`, `about.body2`, `about.how1`, `about.how2`, `about.how3` maps to code or configuration (feeds scored by language; summary language equals the story language — `migrations/001_init.sql:103-104`; AI summaries fail open; no article body stored — `migrations/001_init.sql:70-100`; no image rehosting).
- [ ] Exactly one primary action: the lead form's submit. The contact link is a text link.
- [ ] `BriefSignup` renders only when `channel.cta.asset` is absent, matching the channel home and article rule (`.work.ui/screens/contact/20261106-SCREEN-SPEC.md` §Decisions 2).
- [ ] `TrustBlock` renders in the rail, sticky only at `lg`, and never overlaps the footer.
- [ ] The method list uses list markup and three items — no fourth item added without a matching config fact.
- [ ] No team grid, avatars, social icons, department tabs or map on this page.
- [ ] No horizontal overflow at 1280 and 390 px for `/legal/about` and `/es/legal/about`; `e2e/layout.spec.ts` covers both paths.
- [ ] EN and ES render complete, unmixed copy; the locale switch preserves the path; `pnpm check` stays green.
- [ ] axe-core: zero critical or serious violations on both locales.
- [ ] Tone: method first, plainly stated. No superlatives, no team story, no testimonials.

## 12. Concept / UIS registry

| UIS id | Applies | Reason | Status |
|--------|---------|--------|--------|
| UIS-01 | yes | scan path: mission → method → contact → form | pending |
| UIS-02 | yes | touch targets on links and form controls | pending |
| UIS-03 | yes | no added motion; reduced-motion honoured | pending |
| UIS-04 | yes | contrast on all channel schemes, dark included | pending |
| UIS-05 | yes | keyboard order, form focus, no modal traps | pending |
| UIS-06 | yes | agent-authored UI: no slop, no invented proof | pending |
| UIS-07 | yes | craft tier refined | pending |
| UIS-08 | yes | degraded, brief-suppressed, form success/failure | pending |
| UIS-09 | no | no charts or dashboards | N/A |
| UIS-10 | no | utility page; the channel home owns the marketing surfaces | N/A |

## 13. Visual references

| Field | Value |
|-------|-------|
| **exampleIds** | `websites/W7` (about page), `websites/W9` (reading measure) |
| **manifestPaths** | `.ai.ui/examples/websites/manifest.md` |
| **referenceIds** | `websites/W7`, `websites/W9`; direction `editorial-conversion` |
| **direction** | `.work.ui/inputs/references/directions/editorial-conversion.md` (Approved 2026-11-05) |
| **doNotCopy** | logo/wordmark; reference palettes as identity; team photos and bios; testimonials; W7's social icons and department tabs |
| **originalityCheck** | own method copy, own composition, own channel palette; no reference layout reproduced |
| **accessibility** | WCAG 2.2 AA; measure and contrast verified; token-lint 0 raw literals |
| **craftTier** | refined |
| **extractedRules** | mission statement with brand typography; values section as heading + paragraph; reading measure ≤65ch; factual claims only |
| **regionMap** | mission → `W7` mission statement · method → `W7` values section · body measure → `W9` 65ch rule |

### extractedRules (binding)

- Mission statement carries brand typography (serif H1) and sits full-width inside the measure. (`W7`)
- The method reads as a values section: one heading, short paragraphs, no icon-only meaning. (`W7`)
- Reading measure ≤65ch for the body copy. (`W9`)
- State only what can be checked; no social proof that cannot be produced on request. (`W7` T7 rule, applied here)

### Deliberately not carried

- **W7's team grid, avatars and social links.** There is no team page and no public people data; rendering empty avatars would fake a team.
- **W7's icon + heading + paragraph value cards.** No icon primitive ships (`CATALOG.md` has none) and the method is three short statements; a list carries them without decorative icons.
- **W7's department tab filter.** Three method items do not need filter tabs.
- **W9's sticky table of contents and back-to-top.** The page has three sections; a TOC would be chrome with nothing to navigate.
- **The channel-home furniture** — photo band, coverage columns, action panel — stays on the home screen.

### Channel art direction

Inherited: the page renders inside the channel's `[data-skin]` wrapper, so display font, accent rule and radius follow the channel. No imagery of its own. `TrustBlock` keeps its card surface; every other region is open.

## Decisions

1. **No team section.** No people data exists; the trust comes from method, not faces.
2. **No retention number** until `/v1/industries/{slug}` exposes `retention_days`. The page says "rolling window" and stays true for every channel.
3. **One primary action.** The lead form submits; the contact link stays a text link; `BriefSignup` renders only when `cta.asset` is absent, matching the home/article rule from M9.
4. **The rail keeps `TrustBlock` as a shipped card**, and `LeadForm` keeps its own card. Both are reused patterns, not new boxes; the mission and method sections stay open.
5. **No "last updated" date.** There is no content field behind it, and a hardcoded date would age silently.

## Open questions

1. Should the method section link a public source-quality page? `docs/source-quality.md` is internal (policy, grades); publishing a reader-facing version is a content decision, not a UI one.

## Next action

None — implemented. Follow-ups live in `.work.ui/plans/NEXT_UI.md`.