# Editorial console - screen SPEC amendment 03

**Status:** Implemented (2026-11-06)
**Parent:** `20261106-SCREEN-SPEC.md`
**Scope:** a new Contacts tab

## What changed

- Contacts sits after Leads.
- Table: channel, name/email, country, source page + campaign, status, created,
  and actions.
- `View` expands the message, phone, campaign, and session hash.
- Status is `new`, `read`, or `closed`.
- Delete is a two-step action and calls a DSAR erase.
- The table does not expose the IP or user-agent hash.

## Rules

- **C1.** List, filter by channel/status, update status, erase.
- **C2.** The message body is shown only in the expanded row.
- **C3.** Delete keeps the existing two-step confirmation pattern.
- **C4.** No raw IP or user-agent is displayed.

## Verification

- `pnpm typecheck`, `pnpm lint`, `pnpm check` (415 keys, 11/11 contrast).
- `pnpm build` passes.
- Playwright admin e2e opens the Contacts tab.
- API tests cover list, status update, and erase.
