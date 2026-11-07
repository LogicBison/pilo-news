# Reference issue archive and detail - screen SPEC

**Status:** Implemented (2026-11-06)
**Slug:** reference
**Paths:** `/{locale}/{industry}/references`, `/{locale}/{industry}/references/{date}`

## 1. Summary

A reader-facing archive for dated reference issues and the issue page itself. A draft is never visible here; only a published, reviewer-signed issue appears. The page is the public counterpart of the admin Offers tab.

## 2. States

| State | Treatment |
|-------|-----------|
| Archive, no issues | honest empty state: the first issue is in review |
| Archive, published issues | newest first, date, title, scope, row count |
| Detail, published | title, standfirst, issue date, scope, reviewer, row count, table, sources, source version |
| Detail, draft/unpublished/missing | 404 |
| API unavailable | degraded notice |
| Spanish locale | English issue content with a visible English-only notice; `noindex` |
| Long rows | table scrolls inside the page; the page never scrolls horizontally |

## 3. Layout

- Archive: max-width 3xl, back link to channel, h1, one-line intro, list.
- Detail: max-width 4xl, back link, eyebrow, h1, standfirst, metadata chips, optional ES notice, table, sources, provenance footer.
- Table columns: date, what changed (headline + change + jurisdiction), action, source link.
- One action only: the source link in each row; no lead form on the issue page.

## 4. Content

All strings live in `messages/{en,es}.json` under `reference.*`. The issue title, rows, sources, scope, reviewer, and source version come from the published issue, not from copy.

## 5. Interactions

- Every row opens the primary source in a new tab with `rel="noopener noreferrer"`.
- Archive rows link to the detail page.
- The back link returns to the channel home.
- No forms, no popups, no client state.

## 6. Data

- `GET /v1/industries/{slug}/references` and `.../references/{issue_date}`.
- Only `status='published'` rows; drafts return 404.
- `meta.fallback=true` for Spanish; the page shows the English-only notice.

## 7. Accessibility

- One h1, table caption, `scope="col"` headers.
- Source links have accessible names; external-link behavior is standard.
- Contrast from channel tokens; `pnpm check` remains green.
- Axe: 0 critical/serious on the archive EN/ES and on a published detail page during the admin publish e2e.

## 8. Verification

- `pnpm lint`, `pnpm typecheck`, `pnpm check` (408 keys, 11/11 contrast).
- `pnpm build` includes both reference routes.
- Playwright: archive empty state, published detail, ES notice, channel asset link, admin publish/unpublish.
- Axe: 23 public URLs + reference archive; published detail checked in the admin e2e.

## 9. Out of scope

- Email delivery or subscription to an issue.
- Correction notes, issue comments, or a search across issues.
- ES translation of issued rows; the page states English.
