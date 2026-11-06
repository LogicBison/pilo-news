# Editorial console — screen SPEC

**What it is:** screen SPEC for `/{locale}/admin` (`/en/admin`, `/es/admin`) — the single-operator console behind the public sites: sign in, then work through twelve tabs over channels, sources, topics, articles, pins, refresh runs, API keys, audit, leads, partners and the funnel read-out.
**Status:** Implemented (2026-11-06) — built and verified; 78 Playwright tests pass on a production build
**Slug:** admin-console
**Path:** `.work.ui/screens/admin-console/20261106-SCREEN-SPEC.md`

## 1. Summary

One operator account runs this screen (domain SPEC §3; the owner uses the same account) to keep the pipeline honest: add a feed, fix a topic weight, hide a bad story, pin a lead story, check a run, read a lead, revoke a key. The job is to do one of those in under a minute and not break anything by accident. There is no public entry point; the page sets `robots: noindex, nofollow` (`apps/web/src/app/[locale]/admin/page.tsx:9`).

Today the screen is one 750-line client component (`AdminConsole.tsx`) with twelve tabs, `sn-card`/`sn-input`/`sn-btn` classes, and no catalog primitives. Seven gaps show:

- **The sign-in form arrives prefilled** with `admin@example.com` (`AdminConsole.tsx:169`), so the public login screen ships an operator address by default.
- **Hide and pin use `window.prompt`** (`AdminConsole.tsx:555`, `:560`) — no label, no length limit for the R8 reason, no validation feedback.
- **Deleting a lead and revoking a key have no confirmation**, while the copy key `admin.confirmDelete` exists unused (`apps/web/src/messages/en.json:248`).
- **A 401 mid-session shows "Something went wrong (401)"** and leaves stale panels; R2 requires a return to sign-in.
- **Every create form is placeholder-only** (`aria-label` + `placeholder`), and bootstrap renders the sign-in form before `/auth/me` resolves.
- **The tab strip has no tab semantics and no deep link**: twelve buttons, `aria-selected` nowhere, the active tab lost on refresh.
- **`legal` is hardcoded twice** — the workspace default (`AdminConsole.tsx:155`) and the home link (`:327`) — so a deployment on another default channel opens on the wrong one.

## 2. Personas & jobs

| Persona | Job |
|---------|-----|
| Operator (single v1 account) | One console task per visit: fix a source, hide/pin a story, read a lead, check a run |
| Operator on call | Tell a failed run from a stale one without opening logs |
| Owner, same account | Reads the funnel and the audit trail; does not mutate |

## 3. States

| State | Treatment |
|-------|-----------|
| Checking session | a quiet pending state (`admin.loading`), never the sign-in form |
| Signed out | sign-in card: h1, intro, email, password, submit, error line; no prefilled values |
| Signed in, tab idle | header + tab strip + the active panel's data |
| Tab loading | panel-level pending line or skeleton row; the tab strip stays usable |
| Mutating | the submitting control is disabled and relabelled (`admin.saving`); other controls stay usable |
| Success | one status line in a polite live region (`admin.saved`), cleared when the next action starts |
| Error (4xx/5xx/network) | status line with the problem `detail` when present, else `common.error` and the status code; form values preserved |
| Session expired (401) | sign-in screen + `admin.sessionExpired`; cookies cleared client-side; panels drop their data |
| CSRF rejected (403) | one status line naming the cause; no silent retry loop |
| Empty table | `admin.empty` inside the panel, table header still visible |
| New key issued | the one-time key panel stays visible until dismissed; no second render of the value |
| Full reset armed | typed `RESET` confirmation; submit disabled until it matches exactly |

## 4. Layout & hierarchy

| Region | Content | Notes |
|--------|---------|-------|
| Sign-in | h1, one-line intro, email, password, submit, error | centered, `max-w-md`; no brand art, no marketing copy |
| Header | h1 "Editorial console", operator email, view-site link, sign out | sign out is secondary; the view-site link targets `/` so the server picks the default channel |
| Tab strip | twelve tabs | `role="tablist"`, wraps at `lg` and below; the active tab carries `aria-selected` and an accent rule |
| Panel | forms, then the tab's table or list | one `role="tabpanel"`, labelled by its tab |
| Status line | results and errors | one region, above the panel; `role="status"` for results, `role="alert"` for failures |
| Footer | none | the console does not carry the public footer |

Breakpoints: `sm` 640, `md` 768, `lg` 1024, `xl` 1280. At 390 the tab strip wraps to multiple rows, forms stack to one column, and tables scroll inside their panel — the page itself never scrolls horizontally.

## 5. Content

Copy lives in `apps/web/src/messages/{en,es}.json`; key sets are equal and CI-checked (`pnpm check`). Reused keys: `admin.title`, `admin.loginTitle`, `admin.loginIntro`, `admin.email`, `admin.password`, `admin.signIn`, `admin.signOut`, `admin.invalid`, `admin.notConfigured`, `admin.tabs.*`, `admin.empty`, `admin.confirmDelete`, `admin.confirmReset`, `admin.fullReset`, `admin.keyShownOnce`, `admin.create`, `admin.save`, `admin.delete`, `admin.revoke`, `admin.hide`, `admin.unhide`, `admin.pin`, `admin.unpin`, `admin.reason`, `admin.position`, `common.loading`, `common.error`.

New keys this SPEC requires (both locales):

| Key | Intent |
|-----|--------|
| `admin.loading` | session check / panel load line |
| `admin.saving` | disabled submit label |
| `admin.saved` | result line after a successful mutation |
| `admin.sessionExpired` | the 401 return-to-sign-in message |
| `admin.cancel` | cancel a two-step confirmation (no `common.cancel` today) |
| `admin.reasonCount` | reason length counter, e.g. "{n}/200" |

Rules: the sign-in form starts empty — the `admin@example.com` default is removed. Console copy stays plain and operational: no exclamation marks, no "oops", no emoji, no marketing voice.

## 6. Interactions

- **Tab strip:** APG tabs — `role="tablist"`, each tab `role="tab"` with `aria-selected` and `aria-controls`; Left/Right move, Home/End jump, Enter/Space activate; the panel is `role="tabpanel"` with `tabIndex={0}` and `aria-labelledby`. Focus moves into the panel on tab change.
- **Forms:** visible labels above every control (no placeholder-only fields), `common.requiredNote` where required, submit disabled while sending.
- **Hide a story:** an inline disclosure per row with a labelled reason field (required, ≤200 chars, live counter) and Save/Cancel. No `window.prompt`.
- **Pin a story:** inline position select (1-5) plus weight field, then Save/Cancel. No `window.prompt`.
- **Delete a lead / revoke a key:** two-step inline confirmation — the first control reads Delete/Revoke, the second reads `admin.confirmDelete` and can be cancelled with `admin.cancel`. No `window.confirm`.
- **Full reset:** keeps the typed `RESET` field; submit stays disabled until the text matches.
- **New key:** shown once in a panel with a dismiss control (`common.dismiss`); the plaintext value is never re-fetched or re-rendered.
- **Sign out:** clears operator, CSRF token and all panel data before showing the sign-in card.
- **Default channel:** the workspace starts on `SN_DEFAULT_INDUSTRY`, passed from the server — not a hardcoded slug.
- **Audit filter:** a labelled select of the actions present in the loaded page plus "all"; changing it refetches with `?action=`.
- **Keyboard:** every action reachable by keyboard; escape closes an inline confirmation without submitting.

## 7. Data dependencies

- Auth: `POST /v1/admin/auth/login`, `GET /v1/admin/auth/me`, `POST /v1/admin/auth/logout`; httpOnly `sn_admin` cookie, `sn_csrf` cookie read for the `X-CSRF-Token` header on every mutation. Contract: `.work/features/editorial-console/20261105-SPEC.md` R1-R3 (link only).
- Tabs read `GET /v1/admin/{industries,sources,topics,articles,pins,refresh,api-keys,audit,leads,partners,funnel}`; mutations are `POST`/`PATCH`/`DELETE` on the same paths.
- Failure mapping: `401` with `type=session-expired` → sign-in state (`admin.sessionExpired`); `403` → CSRF message; `409` → the problem `detail` (lock held, duplicate position); `422` → form-level message; `0` (network) or `5xx` → `common.error` with the status.
- All calls go through `/api/proxy/...` with `credentials: "same-origin"` and `cache: "no-store"`.
- No new endpoint and no schema change; this SPEC adds no analytics call.

## 8. Tokens & components

Craft tier **utilitarian** (foundation 01; `HANDOFF_UI` records the console as the mixed-tier exception). At this tier the control rules allow native inputs; primitives are used where they already exist.

| Component | Catalog status | Native waiver |
|-----------|----------------|---------------|
| Button | shipped | — for sign-in, submit and destructive actions |
| TextField | shipped | — for labeled text inputs where a form is composed |
| SectionHeader | shipped | — panel headings, if a panel needs one |
| Chip | shipped | — the active-tab pill may reuse it |
| Native `<select>` | — | **native allowed** — lead status, pin position, channel picker (utilitarian tier, `SURFACE-AND-CONTROL-CRAFT.md` §5) |
| Native `<table>` | — | **native allowed** — data tables; no grid library |

Tokens: `color.surface.base`, `color.surface.elevated` (panels only), `color.border.subtle`, `color.text.primary`, `color.text.muted`, `color.focus.ring`, `color.brand.primary` (active tab), `font.size.*`, `space.*`. No raw hex; the amber/red action borders in the current console are replaced by token colours.

## 9. Accessibility

WCAG 2.2 AA.
- Sign-in: labeled fields, one `h1`, error announced (`role="alert"`), no prefilled values.
- Tab strip follows the APG tabs pattern; the panel is focusable and labelled.
- Tables: a `<caption>` (may be visually hidden), `scope="col"` on every header cell, numeric columns right-aligned, no layout tables.
- One live region per status, `role="status"` for results and `role="alert"` for failures — not one red div reused for both.
- Focus is never lost after a mutation: it returns to the control that started it, or to the panel heading when the row is gone.
- Target size ≥24 px minimum (WCAG 2.2), 44 px for primary actions; focus ring 3 px accent.
- Contrast from tokens on the base scheme; `pnpm check` stays green.
- No motion beyond token transitions; `prefers-reduced-motion` honoured.

## 10. Analytics & observability

No client analytics on the console. The audit trail (`audit_events`, R6) is the record of operator action, and API metrics cover the rest. Never send lead PII, keys or reasons to any client event.

## 11. Acceptance criteria

- [ ] The sign-in form renders empty; `admin@example.com` is gone from `AdminConsole.tsx:169`.
- [ ] Bootstrap shows a pending state until `/auth/me` resolves; an authenticated reload never flashes the sign-in form.
- [ ] A 401 on any request returns to the sign-in card with `admin.sessionExpired`, and the panels hold no data afterwards.
- [ ] The tab strip exposes `role="tablist"`/`tab`/`tabpanel`, `aria-selected`, arrow-key roving focus, Home/End, and a labelled panel.
- [ ] No `window.prompt`, `window.confirm` or `window.alert` remains on the screen — hide, pin, delete and revoke are inline forms.
- [ ] Hiding requires a reason of 1-200 characters, counted live, and cancelling leaves the article visible.
- [ ] Pinning offers positions 1-5 and a weight; a `409` (duplicate position) surfaces the problem message without losing the form.
- [ ] Deleting a lead and revoking a key each require the two-step confirmation and can be cancelled.
- [ ] Full reset submits only when the typed confirmation equals `RESET`.
- [ ] Every mutation ends in a status line: `admin.saved` on success, the problem detail or `common.error (status)` on failure.
- [ ] Every form control has a visible label; no placeholder-only field remains in the console.
- [ ] Tables have a caption and `scope="col"`; an empty table shows `admin.empty` with its header intact.
- [ ] At 390 px the page has no horizontal overflow; tables scroll inside their panel; the tab strip wraps.
- [ ] EN and ES render complete, unmixed console copy; `pnpm check` stays green.
- [ ] Panels are flat surfaces with separators, not a card per row.
- [ ] Each form has exactly one primary action; destructive actions read quieter than the primary.
- [ ] The workspace opens on `SN_DEFAULT_INDUSTRY`; neither `AdminConsole.tsx:155` nor `:327` hardcodes `legal`.
- [ ] The audit tab filters by action through the `?action=` parameter the API already accepts (`apps/api/src/news_api/editorial/http/audit.py:14`).
- [ ] axe-core: zero critical or serious violations on `/en/admin` (sign-in), and on the signed-in console when `E2E_ADMIN_PASSWORD` is set.
- [ ] No chart, no chart library, and no new dependency is added for this screen.

## 12. Concept / UIS registry

| UIS id | Applies | Reason | Status |
|--------|---------|--------|--------|
| UIS-01 | yes | scan path: header → tabs → form → table | pending |
| UIS-02 | yes | target sizes on tabs, row actions and destructive confirmations | pending |
| UIS-03 | yes | no added motion; reduced-motion honoured | pending |
| UIS-04 | yes | contrast on the base scheme; dark scheme does not apply to the console | pending |
| UIS-05 | yes | tabs keyboard model, inline forms, focus return after mutations | pending |
| UIS-06 | yes | agent-authored UI: no slop, no decorative chrome | pending |
| UIS-07 | no | utilitarian tier (foundation 01); the craft checklist targets customer-facing screens | N/A |
| UIS-08 | yes | session check, loading, empty, error, session expired, confirmations | pending |
| UIS-09 | no | the funnel read-out is a table; no charts on this screen | N/A |
| UIS-10 | no | internal tool; no signature moment | N/A |

## 13. Visual references

| Field | Value |
|-------|-------|
| **exampleIds** | none required — utilitarian tier; the screen SPEC standard requires example ids from `refined` upward |
| **manifestPaths** | none — no example manifest applies at this tier |
| **craftStandard** | `.ai.ui/standards/20260523-SURFACE-AND-CONTROL-CRAFT.md` (utilitarian tier, control anatomy) |
| **craftTier** | utilitarian |
| **extractedRules** | native controls allowed; clear borders over elevation; grouping by section, not by card |
| **regionMap** | header → craft §2 separators · tab strip → craft §4 grouping · forms → craft §3 anatomy · tables → the data-grid rules below |

### extractedRules (binding)

- Flat or single-elevation surfaces with clear borders; one panel surface, not a card per row (`SURFACE-AND-CONTROL-CRAFT.md` §1).
- Group by section with spacing and a separator, not by nesting boxes (§2, §4).
- Native controls are allowed at this tier; every control still carries a visible label and a distinct focus state (§3, §5).
- One primary action per form; destructive actions are visually quieter than the primary, never the loudest control on the panel.
- Tables read as data: caption, scoped headers, aligned numerics, no zebra stripes required.

### Deliberately not carried

- **Charts or sparklines in the funnel tab.** The read-out is a table; chart primitives do not ship and adding a chart library is not this milestone.
- **A URL-backed tab state (`?tab=`).** It would improve refresh and sharing, but it is a separate routing change; recorded as an open question.
- **Roles and permissions UI.** v1 has one operator account (R12); the console does not grow a role matrix.
- **Storybook stories for console compositions.** The catalog covers primitives; the console composes them.

## Decisions

1. **Utilitarian tier confirmed** for the console, as recorded in `HANDOFF_UI`; primitives are reused where they exist, native select and table stay.
2. **No browser dialogs.** Hide, pin, delete and revoke move to inline forms and two-step confirmations; `window.prompt`/`confirm`/`alert` are banned on the screen.
3. **The sign-in form ships empty.** The `admin@example.com` default is removed; the e2e test already fills the field from `ADMIN_EMAIL` (`apps/web/e2e/admin.spec.ts:14`).
4. **One status region, two roles.** Success uses `role="status"`, failure `role="alert"`; the console stops reusing one red div for both.
5. **No new dependencies** for this screen — no table, form or chart library.
6. **The audit filter ships in S1.** `GET /v1/admin/audit` already takes `?action=` (`audit.py:14`); the console only has to expose it.
7. **URL-backed tabs are deferred.** `?tab=` needs router coupling and a Suspense boundary in the client component; revisit when an operator asks for shareable console links or a second surface deep-links a tab.

## Next action

None — implemented. Follow-ups live in `.work.ui/plans/NEXT_UI.md`.