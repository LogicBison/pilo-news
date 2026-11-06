# Accessibility audit — milestone (ten channel homes + channel flows)

**What it is:** WCAG 2.2 AA audit of the live channel surfaces, run before `@ui-component-build` continues past the approved SPECs.
**Status:** Done (2026-11-05) — **pass**, no critical or serious findings, no waivers needed; F1/F2 fixed and re-verified, F3 resolved by SPEC amendment, F4/F5 deferred as debt.
**Needs:** nothing.

## 1. Scope

| Axis | Value |
|------|-------|
| Screens | 10 channel homes (`/legal` … `/retail`), each in EN and ES = 20 URLs |
| Channel flows | `/legal/contact`, `/es/legal/contact`, `/legal/about`, `/legal/privacy`, `/legal/terms`, `/legal/search` |
| Articles | `/legal/article/…`, `/cybersecurity/article/…`, `/retail/article/…`, `/es/legal/article/…` (ES article id) |
| Total URLs scanned | 30, zero load errors |
| Standard | WCAG 2.2 AA (`ACCESSIBILITY_STANDARD`), project SPEC §9 per channel |
| Tool | `axe-core 4.10.1` via `@axe-core/playwright`, inside the `web` compose service |
| axe tags | `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22a`, `wcag22aa`, `best-practice` |
| Environment | `web` service, `next dev` (dev server), Chromium headless 1280×900 · 390×844 · 320×720 |

Not run: screen-reader testing (no AT in the session), `@axe-core/playwright` vision tier, forced-colors mode, 400% zoom, production-build rerun (the committed suite last ran on a production build).

## 2. Verdict

**Pass.** 0 critical, 0 serious, 0 WCAG A/AA failures across 30 URLs. The only axe hits are two `best-practice` rules (moderate). Nothing blocks the approved SPECs.

## 3. Findings

| # | Severity | Finding | Evidence | Pages |
|---|----------|---------|----------|-------|
| F1 | moderate (best-practice) | Two `<nav>` landmarks share one accessible name (`nav.menu`), so axe `landmark-unique` cannot tell them apart | `apps/web/src/components/Header.tsx:41`, `apps/web/src/components/Footer.tsx:28` | 29 of 30 |
| F2 | moderate (best-practice) | The CTA panel is `<aside>` nested inside `<section>` inside `<main>`; `complementary` should be top-level | `apps/web/src/components/CtaCard.tsx:26` | 20 of 30 |
| F3 | minor (SPEC claim) | SPEC §9 says "touch targets ≥44px"; measured header/footer text links are 20–24px tall. AA 2.5.8 is still met by spacing (28px gaps in the footer); 2.5.5 (AAA, 44px) is not | measured: footer links 20px high / 28px apart; form controls 44–48px, buttons 48px | 10 of 10 |
| F4 | minor (standard §4) | Lead/contact errors surface in an `aria-live` region but fields carry no `aria-invalid`/`aria-describedby`; the message is not tied to the failing field | `apps/web/src/components/LeadForm.tsx:291`, `apps/web/src/components/ContactForm.tsx:88` | channel homes + contact |
| F5 | minor (out of scope) | Admin console inputs use `placeholder` as the only label (axe passes; 3.3.2 weak) | `apps/web/src/app/[locale]/admin/AdminConsole.tsx:389`, `:437`, `:492`, `:609` | admin only |

Non-findings (checked, not defects):
- Honeypot input `name="website"` sits in an `aria-hidden`, `display:none` wrapper (`apps/web/src/components/ContactForm.tsx:82`) — not exposed, not focusable.
- An English article id under `/es/...` returns the localized 404 ("Página no encontrada") — correct data scoping, not a routing bug; the matching ES id renders with `lang="es"`, skip link, and one `h1`.

## 4. Evidence

| Check | Result |
|-------|--------|
| axe, 30 URLs | 0 critical · 0 serious · 2 moderate rules (`landmark-unique` 29 pages, `landmark-complementary-is-top-level` 20 pages) · 0 of the WCAG-2.2-only rules fire |
| Committed suite `pnpm test:a11y` | 10 passed, 1 flaky (`/stem-cell` hydration timeout, retry passed); single re-run passed in 1.3s |
| Skip link is the first tab stop | 10/10 channels, visible on focus, ring `solid 3px` |
| Focus ring colour | equals the channel accent 10/10 (e.g. `#22d3ee` cybersecurity, `#a16207` retail); ring:bg contrast **4.61–10.36:1** |
| Focus not obscured by the sticky header | 0 obscured stops across 3 channels × 8 tabs |
| Keyboard traps | none (26 tabs per page on `/legal`, `/cybersecurity`, `/legal/contact`) |
| Reflow at 320 CSS px | `scrollWidth == innerWidth` on 10/10 channels |
| `prefers-reduced-motion: reduce` | transitions collapse to `1e-05s` |
| Heading structure | exactly one `h1` and no skipped levels on 30/30 URLs |
| Language | `lang="en"` / `lang="es"` matches the route on 30/30 URLs |
| Landmarks | 1 `main#main`, 2 `nav`, skip link on 30/30 |
| Images | 1 `img` per channel page, `alt=""` + `aria-hidden` (decorative band); credit text stays in the DOM |
| Forms | native `required` on all mandatory fields, visible labels, required note, `role="search"` with sr-only label |
| Theme contrast (`pnpm check`) | 10/10 channels pass; catalogue 268 keys in EN and ES |
| Computed contrast from themes | text:bg 14.05–17.85, muted:bg 6.72–8.61, accent:bg 4.61–10.36 (`measured`, WCAG 2.x formula) |

## 5. Coverage gaps (unverified)

- No screen reader (NVDA/VoiceOver) pass; axe + DOM checks only.
- Vision tier and forced-colors not exercised.
- Keyboard walk sampled on 3 pages, not all 30.
- Audit ran against `next dev`, not a production build; dev-server compile stalls caused the one flaky suite run.

## 6. Resolution (2026-11-05, same session)

| Finding | Resolution | Evidence |
|---------|------------|----------|
| F1 | Footer `nav` now uses a new `nav.footer` key ("Site links" / "Enlaces del sitio"); header keeps `nav.menu` | `apps/web/src/components/Footer.tsx:28`, `apps/web/src/messages/{en,es}.json`; labels render `["Menu","Site links"]` / `["Menú","Enlaces del sitio"]` |
| F2 | CTA panel is `<section aria-label>`; no CSS targeted the `aside` element | `apps/web/src/components/CtaCard.tsx:26` |
| F3 | Ten `20261105-SCREEN-SPEC-amendment-01.md` files replace the blanket ≥44px line with "controls 44px, text links 24px + spacing"; parent SPECs untouched | `.work.ui/screens/channel-home-*/20261105-SCREEN-SPEC-amendment-01.md` |
| F4 | Deferred — lands with the `TextField`/`FieldError` extraction in S0 | `NEXT_UI.md` priority 2 |
| F5 | Deferred — admin label pass | `NEXT_UI.md` priority 3 |

Re-verification after the fixes, against a production build in the `web` container (`next build` + `next start` on port 3100, `PLAYWRIGHT_BASE_URL=http://localhost:3100`):

| Check | Result |
|-------|--------|
| `npx playwright test` (a11y + layout + public + admin) | **57 passed, 1 skipped** |
| axe re-scan, 8 pages, WCAG 2.2 + `best-practice` | 0 violations (both moderate rules gone) |
| `pnpm lint` / `pnpm typecheck` / `pnpm check` | pass · pass · 269 keys, 10/10 contrast |
| `pnpm build` | pass |

Dev-server caveat worth recording: running the same suite against `next dev` produced hydration timeouts and layout flakiness (`browserType` contention, 503 prefetches). The project convention — build first, test the production server — reproduces the baseline exactly.

## Decisions needed

None — F1/F2 and the F3 wording were approved and applied.

## Open questions

1. Does `@ui-component-build` S0 pay the F4 field-error wiring at the same time as the `TextField` extraction? (Recommended: yes — one diff, one re-audit.)

## Next action

`@ui-component-build plan - S0` — build the P0 primitives in `.work.ui/design-system/CATALOG.md`, wiring F4 while extracting the fields.
