# Editorial console - screen SPEC amendment 02

**Status:** Implemented (2026-11-06)
**Parent:** `20261106-SCREEN-SPEC.md` (Implemented)
**Scope:** a new Offers tab

## What changed

The console now has an **Offers** tab between Channels and Sources. It is the operator's window into the generated reference drafts.

- The list shows channel, offer slug, issue date, scope, row count, status, generated time, and actions.
- `View` expands the issue: standfirst, row table, source version, reviewer state, and any error.
- `Build now` queues a fresh draft through `POST /v1/admin/offers/build` with `force: true`.
- `Publish` opens a small inline form that requires a reviewer name. It calls `POST /v1/admin/offers/{id}/publish` and makes the issue public at `/{locale}/{industry}/references/{date}`.
- `Unpublish` is a two-step action; it returns the issue to draft and removes the public route.
- There is no email action in this amendment.

## Rules

- **B1.** Offers are read-only except for the build action.
- **B2.** A build in progress disables only that row's build button.
- **B3.** A failed issue shows its error in the expanded panel.
- **B4.** The detail table uses a caption, column headers, and links that open the source in a new tab.
- **B5.** Publish requires a reviewer name of at least two characters; the API enforces the same rule.
- **B6.** Unpublish uses the same two-step confirmation pattern as key revocation.
- **B7.** The detail panel shows the frozen reviewer and published timestamp after publish.

## Verification

- `pnpm typecheck`, `pnpm lint`, `pnpm check` clean (380 keys, 11/11 contrast).
- `pnpm build` passes.
- Playwright `admin.spec.ts` opens the tab, finds the legal draft, expands it, sees a source link, and opens the reviewer form.
- A second test publishes the legal draft with a test reviewer, reads the public reference page, and unpublishes it in `finally`.
- The tab renders the two current drafts with 12 rows each while they are drafts.
