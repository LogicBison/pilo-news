# Cybersecurity & Threat Intelligence — channel home screen SPEC

**What it is:** screen SPEC for the `cybersecurity` channel home (`/{industry}` → `/cybersecurity`, `/es/cybersecurity`), the page that carries this channel's skin and lead CTA.
**Status:** Draft (2026-11-05) — built ahead of review per operator instruction · **Needs:** `@ui-screen-spec review - cybersecurity` then approval.

## 1. Summary

A professional lands on `/cybersecurity`, recognises the channel within one screen, reads what changed in their field, and — if it matters — asks for a specialist. Entry points: search, social, direct, the language switch, and the article back-link strip.

## 2. Personas & jobs

Primary: P1 industry reader. Job: judge whether an advisory applies to my stack; get a responder fast.

## 3. States

| State | Treatment |
|-------|-----------|
| Loading | route `loading.tsx` skeleton (cards + hero block) |
| Empty | `EmptyState` with channel context; CTA stays visible |
| Partial / fallback | `FallbackNotice` when the bundle language differs |
| Error / degraded | `DegradedNotice` with retry; shell renders, never blank |
| No leads configured | CTA panel renders copy but no form; form hidden behind a config check |

## 4. Layout & hierarchy

| Region | Content | Notes |
|--------|---------|-------|
| App bar | emblem, channel name, nav, locale switch | sticky; skin-specific border |
| Hero (ledger) | lead story, favourite rail, CTA panel | one H1, one primary CTA |
| Illustration band | `SkinScene` (Sentinel) | decorative, captioned with the tagline |
| Proof strip | stories live, languages, updated, independence | verifiable numbers only |
| Desk brief + topic rail | AI summary, topics | 2:1 grid at `lg` |
| Coverage columns | story cards | 3-up at `lg`, 1-up mobile |
| Sources | publisher list | links open in a new tab |
| CTA stack | trust block, lead form, brief capture | one primary action |

Breakpoints: `sm` 640, `md` 768, `lg` 1024, `xl` 1280. Mobile first; hero stacks before the CTA.

## 5. Content

Copy lives in `apps/web/src/messages/{en,es}.json`; channel strings come from `industries` (name, tagline, disclaimers, cta). Primary CTA: "Talk to a vetted security partner". Form asks: need type.

## 6. Interactions

Focus order: skip link → emblem/home → nav → locale switch → hero H1 → hero CTA → band → coverage → CTA form. Locale switch preserves path. Sticky mobile CTA appears after 60% scroll and is dismissible. No modals on this screen.

## 7. Data dependencies

`GET /v1/industries/{slug}`, `GET /v1/news/bundle?industry=cybersecurity&locale=…`, `POST /v1/leads`, `POST /v1/cta-events`. Domain contract: `.work/features/industry-sites/20261105-SPEC.md` §6 (link only — do not duplicate shapes).

## 8. Tokens & components

Surface stack from foundation doc 02. Components in use: `Header` (done, emblem), `Hero` (done), `SkinScene` (done), `ProofStrip` (done), `StoryCard` (done), `CtaCard` (done), `TrustBlock` (done), `LeadForm` (done, native `<select>` — `Select` primitive planned), `BriefSignup` (done), `StickyCta` (done). `Skeleton` and `Notice` primitives: planned (P1) — current treats via `loading.tsx` and `Notices.tsx`.

## 9. Accessibility

WCAG 2.2 AA. Decorative art is `aria-hidden`; the emblem is decorative (channel name is adjacent text). Focus ring 3px accent. Touch targets ≥44px. Live region for form status. Illustration never carries meaning available only visually. Reduced motion respected.

## 10. Analytics & observability

Events: `cta_impression`, `cta_click`, `lead_form_start`, `lead_submit{result}` with channel, placement, locale — no PII. Page render and API fetch metrics exist server-side (`web_api_fetch_total`).

## 11. Acceptance criteria

- [ ] Channel renders its own skin attributes (`data-skin="Sentinel"`, `data-hero="ledger"`) — no two channels share the tuple
- [ ] Hero contains exactly one H1 and one primary CTA
- [ ] Circuit-trace band with a shield and check; hex lattice motif; shield emblem in the masthead.
- [ ] Proof strip shows only values derivable from the bundle response
- [ ] Locale switch preserves the current path; ES page never mixes EN copy
- [ ] Contrast stays green for this channel (`pnpm check`)
- [ ] Tone: credible, specific, no fear-mongering. Mono labels, square corners.
- [ ] extractedRules — W2 split hero / single CTA; W3 tiered CTA in a card grid; W6 content grid with filter chips; W9 ≤65ch reading measure on articles

## 12. Concept / UIS registry

| UIS id | Applies | Reason | Status |
|--------|---------|--------|--------|
| UIS-01 | yes | scan path: hero → proof → coverage → CTA | done |
| UIS-02 | yes | touch targets on mobile CTA and chips | done |
| UIS-03 | yes | motion minimal, reduced-motion honoured | done |
| UIS-04 | yes | channel contrast pairs gated | done |
| UIS-05 | yes | keyboard order through nav, hero, form | done |
| UIS-06 | yes | agent-authored UI: no slop, no stock gradients | done |
| UIS-07 | yes | craft tier refined | pending at milestone close |
| UIS-08 | yes | empty/error/degraded states | done |
| UIS-09 | no | no analytical charts on this screen | N/A |
| UIS-10 | no | no photography; original line-art only | N/A |

## 13. Visual references

| Field | Value |
|-------|-------|
| **exampleIds** | W2, W6, W9 |
| **manifestPaths** | `.ai.ui/examples/websites/manifest.md` |
| **craftTier** | refined |
| **beforeScreenshot** | n/a — greenfield skin, no before state kept |
| **extractedRules** | hero single CTA; tiered CTAs; content grid with chips; ≤65ch measure |
| **regionMap** | hero → W2 · coverage → W6 · CTA panel → W3 · article body → W9 |

### Channel art direction

Circuit-trace band with a shield and check; hex lattice motif; shield emblem in the masthead.

Imagery: a licensed photograph carries the band (source and licence in `apps/web/public/photos/credits.json`); motifs and the masthead emblem stay line-art as the brand layer.

Palette from `industries.theme`: **dark scheme** — midnight `#0b1220` base, light `#e5edf7` text, cyan `#22d3ee` accent, 2px corners. Reference basis: semrush (data density), userpilot (product-led proof).

## Next action

`@ui-screen-spec review - channel-home-cybersecurity`, then `@ui-visual-verify milestone` for this channel.
