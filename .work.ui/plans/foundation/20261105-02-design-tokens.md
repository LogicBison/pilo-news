# System News — Design tokens

**What it is:** UI foundation doc 02 — the token set every component must consume, where it lives, and the contrast evidence behind it.
**Status:** Draft (2026-11-05) · **Needs:** operator acceptance of the `border.strong` control border (D1) and of the base/elevated split (D2).

## Canonical token files

| Layer | Path | Role |
|-------|------|------|
| **Runtime tokens (CSS)** | `apps/web/src/app/globals.css` | `:root` custom properties consumed by components: `--sn-*` |
| **Design source (DTCG)** | `.work.ui/design-system/tokens.json` | canonical token definitions, `$type`/`$value`, OKLCH, aliases — validated (`token-schema-verify.sh`) |
| **Channel values (data)** | `industries.theme` JSONB (`apps/api/migrations/002_seed_industries.sql:8-40`, `apps/config/deployments/*.json`) | per-channel overrides, injected at request time by `apps/web/src/lib/theme.ts:37-51` |

**Boundary rule:** `tokens.json` holds the fallback palette (the `editorial` default) and the full UI scale. Per-channel colours are **data**, never copied into `tokens.json` — one source of truth per layer, no drift. `tokens.json` is validated by `token-schema-verify.sh` (74 tokens, ok, measured 2026-11-05).

**Projection rule:** the CSS layer still receives hex from `industries.theme` because the backend contract requires 6-digit hex (`apps/api/src/news_api/channels/domain/theme.py:70-74`). Each colour token therefore carries its hex projection under `$extensions.sn.hex`; the OKLCH value is the design source, the hex is the wire format. Moving the wire format to OKLCH is a backend change — out of scope, recorded in UU2.

## Semantic token map

Light is the only shipped scheme (`apps/web/src/app/globals.css:14`); dark is deferred (UU1). `--sn-*` is the CSS alias that exists today; `token` is the DTCG path.

| Token | `--sn-*` | Value (light) | Usage |
|-------|----------|---------------|-------|
| `color.surface.base` | `--sn-bg` (new `--sn-surface-base`) | `oklch(98.9% 0.0026 286.4)` · `#fbfbfd` | page canvas |
| `color.surface.elevated` | new `--sn-surface-elevated` | `oklch(100% 0 0)` · `#ffffff` | cards, panels |
| `color.surface.inset` | new `--sn-surface-inset` | `oklch(96.4% 0.0058 264.5)` · `#f1f3f7` | input fills, wells, chips |
| `color.surface.overlay` | new `--sn-surface-overlay` | `oklch(100% 0 0)` · `#ffffff` | sheets, sticky bar |
| `color.text.primary` | `--sn-text` | `oklch(21.0% 0.0318 264.7)` · `#111827` | body, headings |
| `color.text.secondary` | new `--sn-text-secondary` | `oklch(37.3% 0.0306 259.7)` · `#374151` | support copy |
| `color.text.muted` | `--sn-muted` | `oklch(44.6% 0.0263 256.8)` · `#4b5563` | timestamps, captions |
| `color.text.on-primary` | hardcoded `#ffffff` (retire) | `oklch(100% 0 0)` · `#ffffff` | text on primary fill |
| `color.border.subtle` | new `--sn-border-subtle` | `oklch(93.3% 0.0092 258.3)` · `#e5e9ef` | region separators |
| `color.border.default` | `--sn-border` | `oklch(89.8% 0.0127 255.5)` · `#d8dee6` | decorative borders only |
| `color.border.strong` | new `--sn-border-strong` | `oklch(59.8% 0.0252 260.7)` · `#77808f` | control boundaries (1.4.11) |
| `color.brand.primary` | `--sn-primary` | per channel (default `#1e3a5f`) | buttons, brandmark, links |
| `color.brand.accent` | `--sn-accent` | per channel (default `#8a4b08`) | eyebrow, CTA edge, focus ring |
| `color.focus.ring` | `--sn-accent` | alias → `color.brand.accent` | focus-visible outline |
| `color.state.success` | new `--sn-success` | `#15803d` | confirmations |
| `color.state.warning` | new `--sn-warning` | `#b45309` | degraded/retry notice |
| `color.state.danger` | new `--sn-danger` | `#b91c1c` | field errors |
| `color.state.info` | new `--sn-info` | `#0b4f6c` | language-fallback notice |

Non-colour tokens: `space.0-16` (4px base), `radius.sm|md|lg|xl|pill`, `elevation.1|2|3|inset`, `font.*`, `motion.*`, `z.base|sticky|overlay|toast`, `breakpoint.sm|md|lg|xl` — full values in `tokens.json`.

## Surface & control tokens (craft tier: refined)

The surface stack is mandatory at refined tier (`.ai.ui/standards/20260523-SURFACE-AND-CONTROL-CRAFT.md` §2). Today only two surface values exist and they are not a stack:

| Layer | Today | Target |
|-------|-------|--------|
| base | `--sn-bg` `#ffffff` | `#fbfbfd` |
| elevated | `--sn-surface` `#f6f7f9` used as a *tint*, cards are `--sn-bg` | `#ffffff` + `elevation.1` |
| inset | **missing** — inputs fill with `--sn-bg` (`globals.css:270-281`) | `#f1f3f7` + `elevation.inset` |
| overlay | **missing** — sticky bar reuses `--sn-bg` at 95% (`apps/web/src/components/Cta.tsx:72`) | `#ffffff` at 95% + `elevation.3` |

**Control contrast gap (measured).** Inputs are identified by a 1px `--sn-border` on a same-as-background fill: 1.26–1.48:1 across the seven channels, against the 3:1 WCAG 1.4.11 floor for non-text contrast. `color.border.strong` fixes it at 3.59–3.99:1 (measured). axe does not test 1.4.11, which is why the current "0 critical/serious" axe result did not catch it.

## Per-channel values today (measured 2026-11-05)

Read live from `/v1/industries/{slug}` on the dev stack; contrast computed with the same relative-luminance definition as `theme.py:43-60`.

| Channel | Layout | Primary | Accent | Surface | Radius | Heading | text/bg | muted/bg | text/surf | white/primary | accent/bg | border/bg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| legal | editorial | `#1e3a5f` | `#8a4b08` | `#f6f7f9` | 10px | Georgia | 17.74 | 7.56 | 16.55 | 11.50 | 6.79 | 1.35 |
| financial | professional | `#0b4f6c` | `#0f766e` | `#f1f5f9` | 6px | Arial | 17.85 | 7.58 | 16.30 | 8.94 | 5.47 | 1.48 |
| behavioral-health | editorial | `#4c1d95` | `#9a3412` | `#faf5ff` | 12px | Georgia | 14.68 | 7.56 | 13.68 | 10.95 | 7.31 | 1.39 |
| education | academic | `#1d4ed8` | `#b45309` | `#f8fafc` | 10px | Georgia | 14.43 | 7.43 | 14.03 | 6.70 | 4.94 | 1.26 |
| logistics | professional | `#14532d` | `#b45309` | `#f0fdf4` | 6px | Arial | 17.74 | 7.56 | 16.95 | 9.11 | 5.02 | 1.37 |
| cybersecurity | professional | `#1e293b` | `#0e7490` | `#f1f5f9` | 8px | Arial | 17.85 | 7.58 | 16.30 | 14.63 | 5.36 | 1.48 |
| stem-cell | academic | `#0f4c5c` | `#9a3412` | `#f8fafc` | 10px | Georgia | 14.68 | 7.56 | 14.03 | 9.51 | 7.31 | 1.28 |

Reading: every channel clears 4.5:1 on the five gated pairs, and the accent clears 4.5:1 as text (not just the 3.0 it is gated at). The only failing pair is `border/bg`, which no gate checks today. Channel personality currently lives in 7 colours + 2 font families + radius — that is the whole of "per-channel character", and the reason the skin refresh exists.

## Rules

1. Components consume semantic tokens only; no `#`, `rgb(`, `hsl(`, or Tailwind palette classes in component or layout files (`.ai.ui/standards/20260523-DESIGN_TOKENS_STANDARD.md` §4).
2. A new value needs a token; a new token needs a row in this doc.
3. Any token change re-runs `pnpm check` (contrast, 7 channels) and `token-schema-verify.sh`.
4. Channel themes stay data: two font families max, 6-digit hex, five gated contrast pairs (`theme.py:78-97`).
5. Accessibility pairs gated at 4.5:1 (text) and 3:1 (non-text controls) in every channel, not just the default.

## Evidence

| Claim | Tag |
|-------|-----|
| 7 channels loaded from the dev API, values as tabulated | measured |
| Contrast ratios in the table | measured (WCAG 2.1 relative luminance) |
| Input boundary 1.26–1.48:1 vs 3:1 floor | measured |
| `border.strong` `#77808f` = 3.99:1 on white, 3.59:1 on inset | measured |
| `tokens.json` valid DTCG, 74 tokens | measured (`token-schema-verify.sh`) |
| OKLCH values are the design source, hex the wire format | assumption — depends on a future backend change (UU2) |
| Base `#fbfbfd` vs elevated `#ffffff` reads as a stack at 1.03:1 | assumption — verify visually in `@ui-visual-verify` |

## Decisions needed

1. **`color.border.strong` on every control** — changes the look of all inputs and cards' interactive edges; the alternative is failing 1.4.11.
2. **Base/elevated split** (`#fbfbfd` page, `#ffffff` cards) — a visible change to every page; it is what makes "elevated" mean something.

## Open questions

1. Do channels need their own surface tints (health already seeds `#faf5ff`) or is hue confined to primary/accent? Data supports both; the skin refresh should decide per channel.
2. `--sn-surface` is today a tint used by chips and the footer. Retire it, or keep it as `surface.subtle`?

## Next action

`@ui-design-foundation greenfield` — continue with foundation doc 03 (pattern inventory).
