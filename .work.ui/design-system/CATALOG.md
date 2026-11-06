# Design system catalog

**What it is:** the primitive/compound/pattern registry for the ten channel websites — what ships today, what S0 must build, and the token + behavior + a11y binding for each.
**Status:** In review (2026-11-05) — S0 built: every P0 primitive is `shipped`; the ten channel homes are already consuming them. Refreshed by `@ui-design-system init`, updated by `@ui-component-build`.
**Needs:** operator acceptance of the P1 work (Skeleton, Toc) before S1 screens; Storybook stays uninstalled, so no row claims a story.

## 1. Catalog

Paths are `apps/web/`-relative. `shipped` means the surface exists and is in use; `planned` means S0 build scope from doc 03. Every token cell is a DTCG name from `.work.ui/design-system/tokens.json` — no literals.

| Component | Tier | Status | Path | Variants | Behavior source | APG pattern | States | Tokens | a11y notes |
|-----------|------|--------|------|----------|-----------------|-------------|--------|--------|------------|
| Button | primitive | **shipped** | `src/components/ui/button.tsx` | primary · ghost · quiet × sm · md · lg | native `<button>` (no library) | button | default · hover · focus-visible · active · disabled · sending | `color.brand.primary`, `color.text.on-primary`, `color.focus.ring`, `radius.sm`, `space.3`, `space.4`, `font.weight.semibold` | 3px accent focus ring (measured 4.61–10.36:1 vs bg); 48px min height measured |
| Card | primitive | **shipped** | `src/components/ui/card.tsx` | flat · elevated · inset | native `<article>` / `<div>` | — | default · hover (interactive only) | `color.surface.elevated`, `color.surface.inset`, `color.border.subtle`, `elevation.1` | Radius 0 under `[data-skin]`; no shadow in v2 |
| Chip | primitive | **shipped** | `src/components/ui/chip.tsx` | filter · label · topic | native `<a>` / `<button>` | button (when toggleable) | default · hover · current · focus-visible | `color.surface.inset`, `color.border.default`, `radius.pill`, `space.1`, `space.3` | Measured height 30px; keep ≥24px spacing |
| SectionHeader | primitive | **shipped** | `src/components/ui/section-header.tsx` | with description · bare | native heading | — | default | `font.family.serif`, `font.size.2xl`, `color.text.primary`, `color.text.muted` | Renders the `h2`; never skips a level |
| TextField | primitive | **shipped** | `src/components/ui/text-field.tsx` | text · email · tel · search | native `<input>` | text-input | default · focus-visible · invalid · disabled · readonly | `component.field.fill`, `component.field.border`, `component.field.radius`, `color.focus.ring`, `font.size.sm` | Label wraps the control; `required` native; error text needs `aria-invalid` + `aria-describedby` (audit F4) |
| TextArea | primitive | **shipped** | `src/components/ui/text-area.tsx` | default · tall | native `<textarea>` | text-input (multiline) | default · focus-visible · invalid · disabled | `component.field.fill`, `component.field.border`, `component.field.radius`, `font.size.sm` | Measured 120px height; same error wiring as TextField |
| SelectField | primitive | **shipped** | `src/components/ui/select-field.tsx` | default | native `<select>` — accepted waiver, no custom listbox | — (native) | default · focus-visible · disabled | `component.field.fill`, `component.field.border`, `color.text.primary` | Native keeps type-ahead + AT support; a Radix `Select` swap needs an APG combobox justification |
| ConsentField | primitive | **shipped** | `src/components/ui/consent-field.tsx` | lead consent · brief consent | native `<input type="checkbox">` in a label | checkbox | unchecked · checked · focus-visible · invalid | `component.field.border`, `color.focus.ring`, `font.size.xs` | 16px box inside a clickable label; the label supplies the 24px+ target |
| FieldError | compound | **shipped** | `src/components/ui/field-error.tsx` | inline · summary | `role="alert"` / `aria-live="polite"` | alert | hidden · visible | `color.text.danger`, `font.size.sm` | Must set `aria-invalid` on the field and join it via `aria-describedby` (audit F4) |
| TrustLine | primitive | **shipped** | `src/components/ui/trust-line.tsx` | response-time · disclosure | static text | — | default | `color.text.muted`, `font.size.sm` | Plain text; no icon-only meaning |
| CtaCard | pattern | shipped (refactor) | `src/components/CtaCard.tsx` | hero · inline · compact (`compact` boolean today) | native `<section>` + heading | — | default · hover · focus-visible | `component.action.surface`, `component.action.ink`, `component.action.muted`, `component.action.line` | Landmark fixed 2026-11-05: `<section aria-label>` (was a nested `<aside>`) |
| StickyCta | pattern | shipped (refactor) | `src/components/Cta.tsx` | bar · inline | native `<a>` | — | hidden · visible · dismissed | `color.surface.overlay`, `color.border.default`, `elevation.2` | One primary CTA per page; dismiss is a labelled button |
| StoryGrid | pattern | shipped (refactor) | `src/components/StoryCard.tsx` + `.sn-grid` | 1 · 2 · 3 column | native list | — | default · hover | `space.4`, `space.6`, `radius.sm` | Heading level per SPEC §4; the card link wraps a heading for a single tab stop |
| AppBar | pattern | shipped (refactor) | `src/components/Header.tsx` | sticky · static | native `<header>` + `<nav>` | navigation | default · scrolled · open (mobile) | `color.surface.base`, `color.border.subtle`, `z.*` | Header `nav` is `nav.menu`, footer `nav` is `nav.footer` (audit F1 fix) |
| SearchField | compound | shipped (refactor) | `src/components/SearchBox.tsx` | page · inline | native `<form role="search">` | search | default · focus-visible · invalid | `component.field.fill`, `component.field.border`, `radius.pill` | sr-only label, `role="search"`, minLength 3 |
| Skeleton | compound | planned (P1) | `src/components/ui/skeleton.tsx` | home · article · search | static CSS | — | loading | `color.surface.inset`, `motion.duration.base` | `aria-busy` + polite live region (today: `loading.tsx`) |
| Notice | pattern | shipped (refactor) | `src/components/Notices.tsx` | degraded · empty · fallback · error | static text + `role` | alert | default | `color.text.primary`, `color.surface.inset`, `color.border.default` | Off-token amber/blue/red classes are the known debt; `role="alert"` only on errors |
| Toc | compound | planned (P1) | `src/components/ui/toc.tsx` | sticky · inline | anchor list | — | current · default | `color.text.muted`, `font.size.sm` | Needs `aria-current="true"` on the active anchor |
| ArticleBody | pattern | shipped | `src/app/[locale]/[industry]/article/[id]/page.tsx` | lede · body | native prose | — | default | `font.family.serif`, `font.size.lg`, `space.6` | ≤65ch measure; one `h1`, no skipped levels |
| Pagination | compound | planned (P2) | `src/components/ui/pagination.tsx` | numeric · prev-next | native `<nav>` | — | current · disabled | `color.border.default`, `space.2` | A second `nav` needs its own label |

## 2. Shipped surfaces not promoted to the catalog

| File | Role | Disposition |
|------|------|-------------|
| `src/components/Hero.tsx` | channel hero, four skin variants | screen composition, not a primitive |
| `src/components/ProofStrip.tsx` | live bundle facts | pattern; P1 promotion candidate |
| `src/components/TrustBlock.tsx` | process + no-resale copy | pattern; absorbs `TrustLine` |
| `src/components/BriefSignup.tsx` | brief capture (`kind=brief`) | pattern; `ConsentField` extraction is S0 debt |
| `src/components/TopicRail.tsx` | topic chips | refactor onto `Chip` |
| `src/components/DeskBrief.tsx` | desk summary block | typography only; no primitive |
| `src/components/LocaleSwitch.tsx` | EN/ES switch | keep; keyboard path verified |
| `src/components/LeadForm.tsx` | lead form | refactor onto TextField / TextArea / Select / ConsentField / FieldError |
| `src/components/ContactForm.tsx` | contact form | same fields; honeypot stays `aria-hidden` + `display:none` |
| `src/app/[locale]/admin/AdminConsole.tsx` | editorial console | utilitarian tier; native controls; placeholder-only labels are known debt (audit F5) |
| `src/components/JsonLd.tsx`, `HydrationMarker.tsx` | SEO / hydration flag | no visual surface |

## 3. Binding rules

- Tokens only: every row cites DTCG names; `token-lint` fails raw colour literals (48 files, 0 raw at last run).
- Composition tokens `component.action.*`, `component.band`, `component.lift`, `component.field.*` carry the conversion spine; a screen that needs a new value extends `tokens.json`, not the component.
- Radius is `0` under `[data-skin]` (v2 direction); `component.field.radius` (2px) is the only surviving corner in forms.
- Focus ring is always `color.focus.ring` at 3px, measured 4.61–10.36:1 against every channel background.
- Storybook is not installed: documentation is this file plus `e2e/layout.spec.ts` and `e2e/accessibility.spec.ts`.

## 4. Gaps

1. `src/components/ui/` now holds the ten built primitives (`button`, `card`, `chip`, `section-header`, `text-field`, `text-area`, `select-field`, `consent-field`, `field-error`, `trust-line`). `LeadForm`, `ContactForm`, `BriefSignup`, `TrustBlock`, `TopicRail` and `Notices` consume them; doc 03 debt 1 and 3 are retired.
2. `StoryGrid` and `StickyCta` are still classes inside `StoryCard.tsx` / `Cta.tsx`, not standalone primitives — the catalog rows point at those files.
3. `Select` is native by waiver; no custom listbox exists, so no APG combobox code to justify.
4. `Skeleton` (P1) and `Toc` (P1) are unbuilt; `Pagination` (P2) is open.
5. Storybook, visual regression, and the vision tier are absent — a11y is covered by `.work.ui/reports/20261105-accessibility-audit-milestone.md`.

## Decisions needed

1. Approve the P1 pair (`Skeleton`, `Toc`) for S1 screens — the article and search routes still render blank while fetching.

## Open questions

1. Does search get `Pagination` (P2) or stay single-page?

## Next action

`@ui-component-build plan - S1` — compose the remaining screens (contact, about, admin) on the shipped primitives.
