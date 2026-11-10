# Brand assets — logo on the root site, favicons everywhere

**Status:** Implemented (2026-11-09 → verified 2026-11-10, shipped as M15) · **Needs:** nothing — decision 1 settled (emblem + live text) and decision 2 settled (owner, 2026-11-10: keep `#0b1220`, recommendation applied, no re-derivation).
**Source art:** `.work.ui/references/heraldfox-final.png` — 1536 × 1024 RGBA, transparent background (797,734 fully transparent pixels, alpha max 254), art bbox `x 140–1401, y 4–922`. Baked palette: fur `#f87000`, banner gold `#f8a800`, banner `#000000`.
**Scope:** root site (apex lobby) gets the logo; every host gets a favicon derived from it. Channel headers keep their per-skin emblem.

---

## 1. What the site does today

| Surface | Today | Evidence |
|---------|-------|----------|
| Apex masthead | a 10 × 10 px solid square, then the text | `components/lobby/shell.tsx:53-56`, `.lb-brand-mark` `lobby.css:102-108` |
| Apex footer | same square + text | `shell.tsx` (`LobbyFooter`) |
| Channel header | per-skin SVG emblem + "System News" / desk name | `components/Header.tsx:29-38` |
| Favicon | none — no `app/icon.*`, no `metadata.icons` | `src/app/` listing; `app/layout.tsx:13-27` |
| `/favicon.ico` | 404, correctly excluded from middleware | `middleware.ts:188` |

The logo file arrived 2026-11-09 and is tracked: `.work.ui/references/heraldfox-final.png` (committed in `f71bfd3`).

## 2. Asset slate

All derivatives are generated from the one source; nothing is hand-painted.

| Asset | Path | Size | Use |
|-------|------|------|-----|
| Emblem, transparent | `apps/web/public/brand/heraldfox-emblem.png` | 700 × 700 (head square, see derivation) | masthead, footer, light surfaces |
| Emblem, flattened | on the tile, below | — | dark surfaces, favicon source |
| Lockup | `apps/web/public/brand/heraldfox-lockup.png` | 1265 × 921 trimmed (`-fuzz 2%`; art bbox ≈ 1262 × 919) | OG image, large placements only |
| Icon tile | `apps/web/public/brand/icon-tile.png` | 512 × 512 | favicon/apple source |
| Favicon | `apps/web/src/app/favicon.ico` | 16 / 32 / 48 | browser tab |
| Icon | `apps/web/src/app/icon.png` | 512 × 512 | manifest, high-DPI tab |
| Apple icon | `apps/web/src/app/apple-icon.png` | 180 × 180, opaque | iOS home screen |

### Derivation

**Tooling:** the block uses ImageMagick 6 `convert` (this host: 6.9.11 — `magick` is not installed). On ImageMagick 7 substitute `magick`; the arguments are identical. The lockup trim needs `-fuzz 2%`: without it the semi-transparent edge pixels (alpha max 254) stop the trim and leave the full 1510 × 1024 canvas.

```
# emblem: the head, square. the banner starts at y≈610, so the crop stops above it;
# the 700x610 box keeps ears, eyes and muzzle, then pads to square.
convert heraldfox-final.png -crop 700x610+410+0 +repage \
  -background none -gravity center -extent 700x700 brand/heraldfox-emblem.png

# lockup: everything, trimmed
convert heraldfox-final.png -fuzz 2% -trim +repage brand/heraldfox-lockup.png

# icon tile: dark field, emblem at 80 %, flattened (no alpha on dark = no white halo)
convert -size 512x512 xc:'#0b1220' \
  \( brand/heraldfox-emblem.png -resize 410x410 \) -gravity center -composite \
  -alpha remove -alpha off brand/icon-tile.png

# favicons
convert brand/icon-tile.png -define icon:auto-resize=48,32,16 src/app/favicon.ico
convert brand/icon-tile.png -resize 512x512 src/app/icon.png
convert -size 180x180 xc:'#0b1220' \( brand/icon-tile.png -resize 164x164 \) \
  -gravity center -composite -alpha remove src/app/apple-icon.png
```

**Why the dark tile.** At 16 px a transparent fox on white disappears into a light tab strip, and the source's semi-transparent edges leave a pale halo on dark ones. Flattening the emblem onto `#0b1220` fixes both, and matches the banner. Gold `#f8a800` stays available for an optional 2 px hairline if the tile looks flat at 32 px.

**Why not the baked lockup in the masthead.** At 32–40 px tall the baked "HeraldFox" is ~7 px of serif — unreadable, and the black banner fights the paper palette (`--lb-paper #f3eee4`). Use the emblem plus live text.

## 3. Placement

### Apex masthead (`shell.tsx` `Masthead`)

```
[emblem 32×32]  HeraldFox*           desk directory · services · questions · contact   EN/ES
                INDUSTRY NEWS, IN YOUR LANGUAGE
```

- Emblem `width=32 height=32`, `alt=""`, `aria-hidden="true"` inside the existing brand link (its `aria-label` already carries the name).
- Wordmark: `--lb-font-display` (Georgia), 21 px, weight 700, letter-spacing -0.01em. Spelling **decided (owner, 2026-11-09): "HeraldFox" is one word, never "Herald Fox"** — the logo and the lobby copy both read `HeraldFox`. The baked wordmark is a high-contrast serif; Georgia bold is the closest system face and the lobby already uses it.
- Replace `.lb-brand-mark` (the 10 px square) in both masthead and footer; delete the rule once unused.
- Mobile ≤ 480 px: emblem 28 px, wordmark 19 px, tagline hidden (it already wraps).

### Apex footer

Emblem 24 px, same link, same accessible name. No second `h1`, no duplicate landmark.

### Channel headers — unchanged by this plan

They keep `SkinEmblem`; the desk identity is the section emblem, not the corporate mark. The brand string there is the open question (D6 / D-018), not an asset question.

### OG image (optional, same pipeline)

`apps/web/src/app/opengraph-image.tsx` — 1200 × 630, paper background, lockup at ~420 px wide, desk name. Only if the session has room; the apex currently shares the channel OG.

## 4. Favicon behaviour

- Next 15 auto-discovers `icon.png`, `apple-icon.png`, `favicon.ico` in `app/` and emits the links; no `metadata.icons` entry, so the per-request `metadataBase` in `layout.tsx:18` is not involved.
- One icon serves the apex and all 11 subdomains. That is the requirement ("all sites present a favicon derived from the logo"), and browsers cache per origin, so expect to hard-refresh each host during verification.
- Phase 2 (not this session): per-desk icon via `app/icon.tsx` keyed on `Host`, so each desk carries its own emblem in the tab. Decide after the single-mark version ships.

## 5. Decisions

1. **Wordmark treatment.** (a) emblem + live Georgia text — recommended, survives any size, theme-aware; (b) baked lockup, scaled up only on the lobby hero where it is legible, emblem elsewhere. **Answered 2026-11-09: (a).** Implemented in the masthead and footer.
2. **Tile colour.** `#0b1220` (cybersecurity skin's ink) or neutral `#111111`. **Answered 2026-11-10: keep `#0b1220`** — it shipped, the derived icons are opaque on it, and the measured corner matches (`srgb(11,18,32)`); no re-derivation.
3. **Per-desk favicons.** Phase 2 or never.

## 6. Acceptance

| # | Check | Pass |
|---|-------|------|
| 1 | Masthead renders emblem + wordmark at 360 px and 1440 px | no overflow, no layout shift (CLS 0 on `/`) |
| 2 | Logo link has one accessible name | axe 0 critical/serious on `/`, `/es`, `/services` |
| 3 | One `favicon.ico` link per document (the App Router also emits `icon.png`) | `curl -s http://localhost:3000/ | grep -c 'rel="icon"'` = 2, exactly one `href="/favicon.ico"` |
| 4 | `/favicon.ico` returns 200 `image/x-icon` | curl |
| 5 | Apple icon is opaque | `identify -format "%[opaque]"` = true |
| 6 | Favicon survives the 16 px test | visual check at 16 px in light and dark tab strip; adjust the crop box ±40 px if the eyes smear |
| 7 | `pnpm lint`, `tsc --noEmit`, `pnpm check`, `pnpm build`, `pnpm test` | green |
| 8 | Both locales | masthead and footer copy unchanged, only the mark swaps |

## 7. Risks

- **Asset licence.** The logo is a supplied brand asset; keep the source in `.work.ui/references/` and commit only derivatives under `apps/web/public/brand/`. No attribution text needed — it is the house mark.
- **Baked-vs-live type mismatch.** Georgia is not the logo's face; at 21 px bold the difference is visible side by side. Accept it, or commission a webfont later (one variable to swap).
- **Cached favicons.** Verification on a subdomain may show the old (absent) icon until a hard refresh; check with a cache-busting query before declaring a failure.
- **`middleware.ts` matcher.** `/icon.png` is not in the exception list at `middleware.ts:188`; confirm the metadata route is served before the middleware rewrite, or add the paths.

## 8. Outcome (2026-11-10)

Shipped as **M15** (full plan §19, v1.7) and verified on dev: emblem 700×700 transparent, lockup 1265×921, tile 512, favicon 48/32/16, icon 512, apple 180 opaque; masthead + footer marks wired with `aria-hidden`, one accessible name; `favicon.ico` 200 `image/x-icon` on four hosts with byte-identical icons; axe 0 critical/serious; CLS 0.0000 at 360/1440 px on `/`, `/es`, `/services`.

Two corrections against this plan's assumptions:

- **`middleware.ts` did need a change.** The matcher at `src/middleware.ts:188` did not exclude `brand/`, `icon.png` or `apple-icon.png`; each was rewritten to `/en/<path>` and 404'd. The negative-lookahead now excludes all three (declared in `.work/touch-scope`).
- **Acceptance #3 was wrong as written.** The document carries two `rel="icon"` elements, not one — `favicon.ico` and `icon.png` are both auto-emitted, each exactly once. Recorded literally instead of rounding the count to a pass.

## 9. Next action

Nothing is open in this plan: decision 2 keeps `#0b1220`, per-desk favicons stay phase 2 (§5 decision 3), and the channel brand string is D6/U1 (owner, 2026-12-15).
