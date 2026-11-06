# Energy & Utilities — channel home screen SPEC

**What it is:** screen SPEC for the `energy` channel home (`/{industry}` → `/energy`, `/es/energy`), the page that carries this channel's skin and lead CTA.
**Status:** Review (2026-11-05) — amended after the review findings · **Needs:** operator approval; `@ui-visual-verify milestone` after approval.

## 1. Summary

A professional lands on `/energy`, recognises the channel within one screen, reads what changed in their field, and — if it matters — asks for a specialist. Entry points: search, social, direct, the language switch, and the article back-link strip.

## 2. Personas & jobs

Primary: P1 industry reader. Job: understand what a grid, market, or policy change means for my portfolio; find a specialist if it does.

## 3. States

| State | Treatment |
|-------|-----------|
| Loading | route `loading.tsx` skeleton (lead block + coverage placeholders) |
| Empty | `EmptyState` with channel context; CTA stays visible |
| Partial / fallback | `FallbackNotice` when the bundle language differs |
| Error / degraded | `DegradedNotice` with retry; shell renders, never blank |
| Success | lead form replaced by a confirmation + brief link; brief form replaced by its confirmation |
| No leads configured | CTA panel renders copy but no form; form hidden behind a config check |
| Permission denied | N/A — public screen, no authenticated area |

## 4. Layout & hierarchy

| Region | Content | Notes |
|--------|---------|-------|
| App bar | emblem, channel name, nav, locale switch | sticky; skin-specific border |
| Hero (ledger) | lead story, favourite rail, action panel | open editorial layout; no hero card; one H1, one primary CTA |
| Proof band | stories live, languages, updated, independence | full-bleed tinted band; verifiable numbers only |
| Photo band | original illustration band + scrim | full-bleed; caption; licensed photo when available |
| Desk brief + topic rail | AI summary, topics | 2:1 grid at `lg`; open blocks with top rules |
| Coverage | story items | balanced 2-column CSS multi-column at `lg`; 1-up mobile; no ragged column |
| Sources | publisher list | open list, links open in a new tab |
| Conversion band | process + lead form + brief capture | full-bleed tinted band; filled fields; one primary action |

Breakpoints: `sm` 640, `md` 768, `lg` 1024, `xl` 1280. Mobile first; hero stacks before the action panel; the action panel keeps its skin placement (Grid keeps the sidebar action panel at `lg`, stacked below on mobile).

## 5. Content

Copy lives in `apps/web/src/messages/{en,es}.json`; channel strings come from `industries` (name, tagline, disclaimers, cta). Primary CTA: "Talk to an energy specialist"; secondary: "Or get the weekly brief". Lead form: name, email, Energy need, consent, optional phone/company under "Add details (optional)", optional "Additional details". Brief form: first name, email, consent. Required fields carry a visible `*` and the "Fields marked * are required" note.

## 6. Interactions

Focus order: skip link → emblem/home → nav → locale switch → hero H1 → hero CTA → band → coverage → CTA form. Locale switch preserves path. Sticky mobile CTA appears after 60% scroll and is dismissible. No modals on this screen.

## 7. Data dependencies

`GET /v1/industries/{slug}`, `GET /v1/news/bundle?industry=energy&locale=…`, `POST /v1/leads`, `POST /v1/cta-events`. Domain contract: `.work/features/industry-sites/20261105-SPEC.md` §6 (link only — do not duplicate shapes).

## 8. Tokens & components

Surface stack from foundation doc 02; conversion composition tokens `component.action.*`, `component.band`, `component.field.*` (84 DTCG tokens, schema-valid). Components in use: `Header` (done, emblem), `Hero` (done, open editorial — no card), `SkinScene` (done, full-bleed photo band + article strip), `ProofStrip` (done, open band), `StoryCard` (done, open editorial item), `CtaCard` (done, action panel), `TrustBlock` (done), `LeadForm` (done, filled fields; native `<select>` — **native allowed** waiver until the P1 `Select` primitive ships), `BriefSignup` (done, open band), `StickyCta` (done). `Skeleton` and `Notice` primitives: planned (P1) — current treats via `loading.tsx` and `Notices.tsx` (**native allowed** waiver).

**Catalog waiver:** `.work.ui/design-system/CATALOG.md` is not initialized yet (`@ui-design-system init` P1); the components above are screen-level compositions, not catalog primitives. No catalog primitive is claimed as `done`; this is the documented waiver for the review gate.

## 9. Accessibility

WCAG 2.2 AA. Decorative art is `aria-hidden`; the emblem is decorative (channel name is adjacent text). Focus ring 3px accent. Touch targets ≥44px. Live region for form status. Illustration never carries meaning available only visually. Reduced motion respected.

## 10. Analytics & observability

Events: `cta_impression`, `cta_click`, `lead_form_start`, `lead_submit{result}` with channel, placement, locale — no PII. Page render and API fetch metrics exist server-side (`web_api_fetch_total`).

## 11. Acceptance criteria

- [ ] Channel renders its own skin attributes (`data-skin="Grid"`, `data-hero="ledger"`) — no two channels share the tuple
- [ ] Hero is open (no card) and contains exactly one H1 and one primary CTA; Grid keeps the sidebar action panel at `lg`
- [ ] Proof band and full-bleed photo/illustration band render live bundle facts only; the band has a scrim, caption and credit when licensed
- [ ] Coverage renders as two balanced columns at `lg` (CSS multi-column, no ragged column >260 px) and one column on mobile
- [ ] Conversion band contains process + lead form + brief; fields are filled/bordered, required fields carry `*`, and no field is underline-only
- [ ] No duplicate compact CTA or oversized hero banner on search/about; `#brief-signup` exists wherever a brief link is rendered
- [ ] No horizontal overflow at 1280 and 390 px; `apps/web/e2e/layout.spec.ts` passes for this channel
- [ ] Locale switch preserves the current path; ES page never mixes EN copy
- [ ] Contrast stays green for this channel (`pnpm check`)
- [ ] Tone: analytical, plain, no investment or safety promises. Sans display, tabular figures, mono labels.
- [ ] Reference DNA bound: `editorial-conversion` (Approved 2026-11-05) — one action panel, proof before the ask, full-bleed photo scrim, balanced coverage columns, filled fields, per-channel CTA placement; originality + a11y recorded in §13

## 12. Concept / UIS registry

| UIS id | Applies | Reason | Status |
|--------|---------|--------|--------|
| UIS-01 | yes | scan path: hero → proof → coverage → CTA | done |
| UIS-02 | yes | touch targets on mobile CTA and chips | done |
| UIS-03 | yes | motion minimal, reduced-motion honoured | done |
| UIS-04 | yes | channel contrast pairs gated | done |
| UIS-05 | yes | keyboard order through nav, hero, form | done |
| UIS-06 | yes | agent-authored UI: no slop, no stock gradients | done |
| UIS-07 | yes | craft tier refined | done — ship_with_notes |
| UIS-08 | yes | empty/error/degraded states | done |
| UIS-09 | no | no analytical charts on this screen | N/A |
| UIS-10 | yes | channel home is the marketing/landing surface — hero, action panel and photo band carry the creative direction | done — ship (distinct hero/photo/action per channel) |

> UIS-07 note: CATALOG init and the native-select/Skeleton waivers are non-blocking; see `.work.ui/reports/20261105-uis-07-10.md`.

## 13. Visual references

| Field | Value |
|-------|-------|
| **exampleIds** | N/A — live-site references; waiver recorded in HANDOFF_UI |
| **manifestPaths** | `.work.ui/inputs/references/directions/editorial-conversion.md` (Approved 2026-11-05) |
| **referenceIds** | `ellevest`, `hubspot`, `leadpages` |
| **direction** | `.work.ui/inputs/references/directions/editorial-conversion.md` (Approved 2026-11-05) |
| **doNotCopy** | logo/wordmark; brand palette as identity; source copy/testimonials; proprietary illustrations/photos/fonts |
| **originalityCheck** | own composition + own palette + own imagery + own copy; recognition test passed |
| **accessibility** | WCAG 2.2 AA; reference contrast failures not inherited; token-lint 0 raw literals |
| **craftTier** | refined |
| **beforeScreenshot** | n/a — greenfield skin, no before state kept |
| **extractedRules** | one action panel; proof before ask; full-bleed photo scrim; balanced 2-column coverage; filled fields; per-channel CTA placement |
| **regionMap** | hero → lead story · coverage → balanced columns · CTA panel → action panel · article body → ≤65ch measure |

### extractedRules (binding)

- One saturated action panel per screen; 0–2 px corners; promise row + one primary verb.
- Proof before the ask: live bundle facts only, no invented logos or testimonials.
- Full-bleed photo band with a channel-tinted scrim and caption credit.
- Balanced coverage columns (`column-fill: balance`); no ragged 3-column layout.
- Filled, bordered form fields with a required note and a distinct optional-details control.
- Per-channel CTA placement: Legal sidebar; Financial banner; Sanctuary open column; Campus corner in a 2-column hero; Network full-bleed banner; Sentinel sidebar; Lab full-bleed banner; Forge banner; Grid sidebar; Market inset.

### Channel art direction

Turbine-and-pylon band with current arcs; grid motif; pylon emblem in the masthead.

Imagery: an original illustration band carries the band; a licensed photo replaces it when available (source and licence in `apps/web/public/photos/credits.json`). motifs and the masthead emblem stay line-art as the brand layer.

Palette from `industries.theme`: deep green `#123f3a` primary + teal `#0e7490` accent, cool mist `#f7faf8` base, 5px corners. Reference basis: databox (dense proof), semrush (data-rich proof).

### Reference DNA (binding)

- **referenceIds:** `ellevest`, `hubspot`, `leadpages`
- **referenceManifest:** `inputs/references/directions/editorial-conversion.md` (Approved; the direction is the manifest)
- **direction:** `inputs/references/directions/editorial-conversion.md` (Approved 2026-11-05)
- **extractedRules:** see the `### extractedRules (binding)` block above (6 rules).
- **doNotCopy:** logo/wordmark; reference palettes as identity (orange, violet/lime, cream/teal); proprietary illustrations/photos/fonts; source copy/testimonials; distinctive composition.
- **originalityCheck:** own composition, own channel palette, own imagery treatment, own copy; side-by-side recognition test passed.
- **accessibility:** WCAG 2.2 AA; reference contrast failures not inherited; token-lint 0 raw literals; axe green on the production build.
- **exampleIds waiver:** live-site references (not an `examples/` manifest); `exampleIds: N/A` recorded in HANDOFF_UI.

## Next action

Operator approval of this Review SPEC, then `@ui-visual-verify milestone` + `@ui-accessibility-audit milestone` for this channel.
