# Contact desk — screen SPEC

**What it is:** screen SPEC for the contact page of every channel — `/{industry}/contact` and `/es/{industry}/contact`. The page where a reader reaches a human: a correction, a source suggestion, or a question. It is not a lead form and does not route to a partner.
**Status:** Implemented (2026-11-06) — built and verified; 78 Playwright tests pass on a production build
**Slug:** contact
**Path:** `.work.ui/screens/contact/20261106-SCREEN-SPEC.md`

## 1. Summary

A reader who found an error, knows a better source, or wants to ask the desk something lands here from the footer Contact link, the top nav, or the error state's contact link (R10). The job is to send the message and leave knowing a person will read it — or to skip the form and write to the desk email directly.

Today the screen is `apps/web/src/app/[locale]/[industry]/contact/page.tsx` (60 lines): H1, intro, desk email, `ContactForm`, and a boxed `sn-card` aside holding only the disclaimer. It works, but it is the thinnest public screen — `about` and `search` reuse `LeadForm`/`TrustBlock`, this one has no conversion composition — and three gaps show:
- the form renders `*` with no required note (LeadForm and BriefSignup both render one);
- failure and rate-limit states give no desk email, which R12 requires;
- the desk email falls back to `news@example.com` when `CONTACT_TO` is unset (`contact/page.tsx:31`); the real address is `news@heraldfox.com` and belongs in configuration.

This SPEC composes the screen from shipped primitives: one H1, one primary action, open surfaces, filled fields, a stated next step, and the desk email as a peer alternative that is hidden rather than faked when unconfigured.

## 2. Personas & jobs

| Persona | Job |
|---------|-----|
| Industry reader (P1) | Report a correction or ask a question without hunting for an address |
| Publisher / source contact (P2) | Suggest a feed or flag a licensing question for the desk |
| Desk operator (internal) | Receive a message with enough context to answer: channel, locale, what changed |

## 3. States

| State | Treatment |
|-------|-----------|
| Default | H1, intro, desk email (when configured), form, rail: next step + privacy note + channel disclaimer |
| Loading | none — the screen renders server-side; only the layout's degraded notice can appear |
| Sending | submit disabled, label `contact.sending`; fields stay editable; no spinner overlay |
| Success | form replaced in place by a `role="status"` confirmation: what happened, the desk email, `contact.sendAnother`; focus moves to the confirmation; URL unchanged |
| Validation | per-field `error` on the field that failed (required, email shape, message length); focus moves to the first invalid field; entered values preserved |
| Rate limited (429) | `contact.rateLimited` as the form-level message, the desk email shown as the alternative, retry allowed after the `Retry-After` window; no internals (R12) |
| Failure (400 / 422 / 5xx / network) | form-level message: the problem `detail` for a 400 domain problem, else `contact.failure`; desk email shown; values preserved; submit stays enabled |
| Degraded API | layout `DegradedNotice` renders; the form still posts to the proxy; never a blank page |
| Desk email unconfigured | the email line and its `mailto` do not render at all — no placeholder address |
| Permission denied | N/A — public screen, no authenticated area |

## 4. Layout & hierarchy

| Region | Content | Notes |
|--------|---------|-------|
| App bar | inherited `Header` | skin-specific border; no change to the shared header in this SPEC |
| Intro | H1 + one-paragraph description + desk email | open; no card, no photo band; H1 uses the channel's serif |
| Form | name, email, phone (optional), message, required note, submit | main column, `2fr` at `lg` |
| Rail | next step (a person reads it, reply when needed), privacy link, channel disclaimer | `1fr` at `lg`; open list with a top rule, **no card** |
| Footer | inherited | unchanged |

Breakpoints: `sm` 640, `md` 768, `lg` 1024, `xl` 1280. Mobile first, single column: intro → email → form → rail. The rail never precedes the form on mobile; the form is the page's job. No sticky CTA on this page — the page is the conversion, and a second ask would compete with the submit.

## 5. Content

Copy lives in `apps/web/src/messages/{en,es}.json`; EN/ES key sets are equal and CI-checked (`pnpm check`). Reused keys: `contact.title`, `contact.description`, `contact.emailLabel`, `contact.formTitle`, `contact.formIntro`, `contact.name`, `contact.email`, `contact.phone`, `contact.message`, `contact.submit`, `contact.sending`, `contact.success`, `contact.failure`, `contact.rateLimited`, `contact.honeypot`, `common.optional`, `common.requiredNote`, `footer.disclaimer`, `footer.privacy`.

New keys this SPEC requires (names indicative, both locales):

| Key | Intent |
|-----|--------|
| `contact.nextTitle` | rail heading: what happens after sending |
| `contact.nextBody` | "A person reads every message. We reply when a reply is needed." — no SLA, no response-time promise |
| `contact.privacyNote` | one line: the message is used to reply, linked to `/{industry}/privacy` |
| `contact.successTitle` | confirmation heading; the existing `contact.success` becomes the body |
| `contact.sendAnother` | restores an empty form without a reload |

Rules: no invented response time, no "we usually reply within…", no testimonial or proof band on this page. The channel name is interpolated into the title (`contact.title` takes `{industry}`).

Desk address: `news@heraldfox.com` for every channel, carried by `CONTACT_TO`; the page renders configuration, never a literal string.

## 6. Interactions

Focus order: skip link → emblem/home → nav → locale switch → H1 → desk email → name → email → phone → message → submit → rail links → footer.

- Enter in a single-line field submits; Enter in the textarea inserts a newline.
- `noValidate` on the form; validation runs on submit and per field as the user leaves it; an error clears on input.
- Success moves focus to the confirmation container (`tabIndex={-1}`); `contact.sendAnother` returns focus to the name field.
- The honeypot stays `aria-hidden`, `tabIndex={-1}`, and outside the accessibility tree.
- No modals, no autofocus on load, no route change on any submit outcome.
- The locale switch preserves the current path (`/es/{industry}/contact`).
- The desk email is a plain `mailto:` link — no copy-to-clipboard widget.

## 7. Data dependencies

- `POST /v1/contact` via `/api/proxy/v1/contact` — fields `name`, `email`, `phone?`, `message`, `locale`, `industry`, `website` (honeypot), `utm`. Contract: `.work/features/industry-sites/20261105-SPEC.md` §R12 and `apps/api/src/news_api/publishing/http/contact.py` (link only — shapes are not restated here).
- `GET /v1/industries/{slug}` — channel name and disclaimer, already read by the page and the layout.
- Status mapping: `200` → success (includes the API's 10-minute duplicate suppression, so the copy must stay true when nothing new was stored); `400` → the problem `detail` when present (localized domain messages, e.g. "Unknown industry."); `422` → `contact.failure`, never the raw `detail`, because that one is the fixed English string "Request validation failed."; `429` → `contact.rateLimited`; `5xx`/network → `contact.failure`.
- The 422 problem body carries no field list, although the handler builds one and drops it (`apps/api/src/news_api/platform/errors.py:158-171`). Field-level errors are therefore client-side only; the API message is always form-level. Surfacing per-field server errors would be a backend change outside this screen's scope.
- No new endpoint, no schema change, no analytics endpoint.

## 8. Tokens & components

| Component | Catalog status | Native waiver |
|-----------|----------------|---------------|
| TextField | shipped | — (native `<input>` under the primitive) |
| TextArea | shipped | — |
| Button | shipped | — (native `<button>` under the primitive) |
| FieldError | shipped (compound) | — |
| TrustLine | shipped | — (rail next-step + privacy lines) |
| SectionHeader | shipped | — (rail `h2`) |
| Card | shipped | **not used** — the rail is open, per §13 |
| SelectField / ConsentField | shipped | **not used** — contact is not a lead; no consent checkbox, no qualification select |

Tokens: `component.field.fill`, `component.field.border`, `component.field.radius`, `component.action.*` (submit only), `color.surface.base`, `color.border.subtle`, `color.text.primary`, `color.text.muted`, `color.focus.ring`, `font.family.serif`, `font.size.*`, `space.*`. No raw hex, no `px` literals in the page or the form; the one hairline rule uses `color.border.subtle`.

`CATALOG.md` labels built primitives `shipped`; for the review gate that is `done`. Every row above exists in `apps/web/src/components/ui/` and is covered by the token gate.

## 9. Accessibility

WCAG 2.2 AA.
- One `h1`; the rail heading is `h2` via `SectionHeader` — no skipped levels.
- Every control has a visible label; required fields carry the visible `*` and the form renders `common.requiredNote` once, after the last field and before the submit.
- Errors: `aria-invalid` + `aria-describedby` on the failing field (audit F4), focus moved to the first invalid field; the form-level message is a polite live region.
- Success and error containers use `role="status"`; the existing e2e test reads that role — keep it.
- Touch targets ≥44 px; focus ring 3 px accent; contrast from tokens only (`pnpm check` stays green for every channel, including the dark `cybersecurity` scheme).
- No motion beyond the 0.18 s token transitions; `prefers-reduced-motion` honoured by the existing stylesheet.
- No PII in the URL, no autocomplete on the message field, `autocomplete` set for name/email/tel.

## 10. Analytics & observability

Today this screen emits nothing; the UTM set is attached to the payload (`captureUtm`). Proposed, not yet wired: `contact_submit{result}` with `result ∈ ok | validation | rate_limited | error`, plus channel and locale — no message text, no name, no email. It needs the funnel endpoint to accept a `contact` placement (§Decisions 4); until then no client event ships and the API's `contact_submissions_total` counter remains the only signal.

## 11. Acceptance criteria

- [ ] Exactly one `h1` and exactly one primary button (the submit); the desk email is a text link, not a second action.
- [ ] The desk email comes from configuration; when `CONTACT_TO` is empty the line and its `mailto` are absent — `news@example.com` never renders.
- [ ] `/legal/contact` and `/es/legal/contact` render `news@heraldfox.com` as the desk address.
- [ ] The HTML default `news@example.com` fallback at `contact/page.tsx:31` is removed.
- [ ] Every field has a visible label; no placeholder-only input.
- [ ] Form and rail share the split at `lg` and stack with the form first below `lg`.
- [ ] No visible CAPTCHA anywhere on the screen.
- [ ] `common.requiredNote` renders once on the form; the optional phone field carries `common.optional`.
- [ ] Invalid submit produces a per-field error with `aria-invalid` + `aria-describedby`, focuses the first invalid field, and preserves the typed values.
- [ ] 429 shows `contact.rateLimited` and the desk email; 400 shows the problem `detail`; 422 shows localized `contact.failure` — never the raw English "Request validation failed."; 5xx/network shows `contact.failure` with the desk email. No outcome navigates away.
- [ ] Success replaces the form with a `role="status"` confirmation, focuses it, and `contact.sendAnother` restores an empty form focused on name.
- [ ] The rail renders as an open block with a top rule — no `.sn-card` wrapper, no border box around the disclaimer.
- [ ] Honeypot is not focusable, not announced, and the form has `noValidate`.
- [ ] No horizontal overflow at 1280 and 390 px for `/legal/contact` and `/es/legal/contact`; `e2e/layout.spec.ts` covers both paths.
- [ ] EN and ES render complete, unmixed copy; the locale switch preserves the path; `pnpm check` stays green (key parity included).
- [ ] axe-core: zero critical or serious violations on `/legal/contact` and `/es/legal/contact` (`e2e/accessibility.spec.ts` already lists `/legal/contact`).
- [ ] No headline card, photo band, or CTA panel is added to this screen — the channel home owns those.
- [ ] Tone: a quiet desk, not a funnel. No urgency, no scarcity, no response-time promise.

## 12. Concept / UIS registry

| UIS id | Applies | Reason | Status |
|--------|---------|--------|--------|
| UIS-01 | yes | scan path: H1 → form → rail; form before rail on mobile | pending |
| UIS-02 | yes | touch targets on fields, submit and rail links | pending |
| UIS-03 | yes | no added motion; reduced-motion honoured | pending |
| UIS-04 | yes | contrast from tokens on all 11 channel schemes, dark included | pending |
| UIS-05 | yes | keyboard order, validation focus, confirmation focus | pending |
| UIS-06 | yes | agent-authored UI: no slop, no stock gradients, no second CTA | pending |
| UIS-07 | yes | craft tier refined | pending |
| UIS-08 | yes | success, validation, rate-limit, failure, degraded, unconfigured-email | pending |
| UIS-09 | no | no charts or analytics on this screen | N/A |
| UIS-10 | no | utility screen inside the marketing site; no signature moment is added | N/A |

## 13. Visual references

| Field | Value |
|-------|-------|
| **exampleIds** | `websites/W8` |
| **manifestPaths** | `.ai.ui/examples/websites/manifest.md` |
| **referenceIds** | `websites/W8` (contact layout); `ellevest`, `hubspot`, `leadpages` (direction) |
| **direction** | `.work.ui/inputs/references/directions/editorial-conversion.md` (Approved 2026-11-05) |
| **doNotCopy** | logo/wordmark; brand palette as identity; source copy/testimonials; proprietary illustrations/photos/fonts; W8's map and office cards |
| **originalityCheck** | own composition, own channel palette, own copy; no reference layout reproduced |
| **accessibility** | WCAG 2.2 AA; reference contrast failures not inherited; token-lint 0 raw literals; no visible CAPTCHA |
| **craftTier** | refined |
| **extractedRules** | visible labels; success replaces the form; split form + info; honeypot with no visible CAPTCHA; one primary action |
| **regionMap** | form → `W8` form · rail → `W8` info column · intro → channel type scale |

### extractedRules (binding)

- Visible labels above every field; no placeholder-only inputs. (`W8`)
- Success replaces the form in place; no toast, no redirect, no modal. (`W8`)
- Form and info share one split layout at `lg`; single column on mobile, form first. (`W8`)
- Honeypot plus rate limit; no visible CAPTCHA unless the honeypot fails. (`W8`)
- One primary action; the submit is the only filled button, the desk email is a text link. (`W8`, direction)
- Filled, bordered fields with a visible required note; no underline-only inputs. (direction)
- Open surfaces: one hairline rule and spacing tokens instead of a card per region. (direction)
- Say what actually happens next; promise no response time the desk cannot keep. (direction)
- Same content in both locales; no partial translation, no mixed-language page. (channel SPECs)

### Deliberately not carried over

- **W8's subject dropdown.** The contact payload has no subject field (`apps/api/src/news_api/publishing/http/contact.py`) and this SPEC changes no API, so a select would be decorative. It lands with the payload change (§Open questions 1).
- **W8's office cards and map embed.** The desk has no public office; the rail carries the next step, the privacy note and the channel disclaimer.
- **The channel-home furniture** — full-bleed photo band, balanced coverage columns, action panel — belongs to the home screen, not here.

### Channel art direction

Inherited: the page renders inside the channel's `[data-skin]` wrapper, so display font, accent rule and radius follow the channel. The screen adds no imagery of its own. On the dark `cybersecurity` scheme the form fill and borders must be checked against `component.field.*` before ship (the matrix is not yet in `check-themes.mjs`).

## Decisions

1. **One desk address for all channels: `news@heraldfox.com`** (operator, 2026-11-06). `CONTACT_TO` carries it in every environment; the page reads configuration, never a literal. No per-channel addresses.
2. **Contact stays a message, not a lead.** No qualification select, no consent checkbox, no partner routing — the lead rung owns those (ADR 013). The subject dropdown waits for a field that can carry it.
3. **The rail is open, not a card.** The disclaimer keeps rendering, as an open block with a top rule.
4. **`noValidate` + client-side field errors.** Localized inline errors instead of browser bubbles in the OS language.
5. **The email sits under the intro**, where mobile readers meet it before the form.
6. **No before-screenshot.** The §13 example plus the recorded `editorial-conversion` direction is the visual contract; the standard makes the screenshot optional, so nothing is waived.
7. **`contact_submit` stays out** until the funnel accepts a `contact` placement.

## Open questions

1. When the contact payload gains a `subject`, should it be free text, a fixed list (correction / source / other), or the desk's own routing list? This gates the W8 dropdown only.

## Next action

None — implemented. Follow-ups live in `.work.ui/plans/NEXT_UI.md`.