# Editorial console - screen SPEC amendment 02

**Status:** Implemented (2026-11-06)
**Parent:** `20261106-SCREEN-SPEC.md` (Implemented)
**Scope:** a new Offers tab

## What changed

The console now has an **Offers** tab between Channels and Sources. It is the operator's window into the generated reference drafts.

- The list shows channel, offer slug, issue date, scope, row count, status, generated time, and actions.
- `View` expands the issue: standfirst, row table, source version, reviewer state, and any error.
- `Build now` queues a fresh draft through `POST /v1/admin/offers/build` with `force: true`.
- The tab states: "Generated drafts from public sources. Build queues a new draft; nothing is published or emailed."
- There is no publish button and no email action in this amendment.

## Rules

- **B1.** Offers are read-only except for the build action.
- **B2.** A build in progress disables only that row's build button.
- **B3.** A failed issue shows its error in the expanded panel.
- **B4.** The detail table uses a caption, column headers, and links that open the source in a new tab.
- **B5.** The tab does not expose a public URL or a publish control.

## Verification

- `pnpm typecheck`, `pnpm lint`, `pnpm check` clean (380 keys, 11/11 contrast).
- `pnpm build` passes.
- Playwright `admin.spec.ts` opens the tab, finds the legal draft, expands it, and sees a source link.
- The tab renders the two current drafts with 12 rows each.
