# Editorial console - screen SPEC amendment 01

**Status:** Implemented (2026-11-06)
**Parent:** `20261106-SCREEN-SPEC.md` (Implemented)
**Scope:** the Channels tab only

## What changed

The Channels tab is now the operator's channel-management surface, not just a
create form plus an enable toggle. Each row shows the channel name and slug, its
effective fetch cadence, and its active free offers. `Manage` expands one inline
editor; `Close` collapses it.

The editor has four groups:

1. **Automation** - automatic fetching on/off. Manual refresh stays available.
2. **Fetch frequency** - use the deployment default, or a custom cadence in
   hours (5 minutes to 24 hours). A custom value overrides the default.
3. **Free offers** - consultation request and ask-one-question switches.
4. **Secondary offer** - none, weekly brief, or gated asset. The gated asset
   option is disabled when the channel has no `cta.asset`.

The deployment default is shown once at the top of the tab and again in the
frequency options, so the operator never has to guess what "default" means.
The editor states that public pages pick up changes within five minutes.

## Rules

- **A1.** The tab MUST show the deployment default and each channel's effective
  cadence.
- **A2.** A custom cadence MUST be validated in the browser (5-1440 minutes) and
  again by the API.
- **A3.** The weekly brief and the gated asset MUST be mutually exclusive in the
  editor; the asset option is disabled without a configured asset.
- **A4.** Save keeps the editor open on failure and shows the API detail; it
  collapses on success.
- **A5.** The `New channel` form is collapsed by default so the managed list is
  the primary surface.
- **A6.** All labels and hints live in both catalogs; the tab remains keyboard
  usable and keeps the existing tab semantics.

## Verification

- `pnpm typecheck`, `pnpm lint`, `pnpm check` clean (365 keys, 11/11 contrast).
- Playwright `admin.spec.ts` opens the editor and asserts the cadence and offer
  controls.
- A browser save check toggled the legal question offer off (`offers.question=false`
  in the public payload) and restored it.
