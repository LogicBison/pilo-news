# Sandbox onboarding - System News v1

**What it is:** how to exercise the three external dependencies (publisher feeds, AI provider, email) without touching production data or spend.
**Status:** Approved (2026-11-05) · **Needs:** nothing.

**Related:** doc 02 integration catalog, SPEC ingestion-pipeline.

---

## 1. Publisher feeds (RSS/Atom)

| Step | Action | Evidence to record |
|------|--------|--------------------|
| 1 | Pick 2 feeds per channel from the approved list (U5) | Feed URL + terms URL |
| 2 | Check `robots.txt` and feed terms allow aggregation + summary | Date + note in `sources.terms_checked_at` |
| 3 | Save sanitized fixtures under `apps/api/tests/fixtures/feeds/<source>.xml` | Fixture file committed; no live secrets |
| 4 | Run the fetcher against fixtures, then a single live fetch | `refresh_runs.stats` + `ingest_fetch_total` |
| 5 | Verify conditional GET: second fetch returns 304 | Log line `status=304` |

**Rules:** never store full article bodies in fixtures; truncate to the fields the parser needs. Do not mirror publisher content into `.work/docs/integration/`.

## 2. AI provider

| Step | Action | Evidence |
|------|--------|----------|
| 1 | Create a provider key with a hard monthly cap (e.g. USD 20) | Provider console screenshot not committed; note cap in HANDOFF |
| 2 | Point `AI_BASE_URL`/`AI_MODEL` at the sandbox | `.env.dev` (ignored) |
| 3 | Run with `AI_ENABLED=false` first - verify fail-open (no summary, still published) | `summaries_generated_total{status="skipped"}` |
| 4 | Run with a mock server returning malformed JSON → verify rejection | `status="invalid"`, no summary stored |
| 5 | Run a 6-item batch with real calls; verify cost metric and prompt-version caching | `ai_tokens_total`, `ai_estimated_cost_usd_total` |
| 6 | Bump `prompt_version` → verify regeneration; repeat without bump → verify reuse | Summary rows unchanged/rebuilt |

**Rules:** no PII to the provider; inputs are title + excerpt only; output never executed; failures never block publish.

## 3. Email (contact notifications)

| Step | Action | Evidence |
|------|--------|----------|
| 1 | Use a sandbox mailbox (Mailtrap/Ethereal or a local SMTP catcher) | `.env.dev` |
| 2 | Submit the contact form → verify delivery + no PII in logs | Inbox + log line without body |
| 3 | Simulate SMTP failure → verify the message is stored and retried | `contact_messages.status` |
| 4 | Verify rate limit (3/hour/IP) and honeypot | `429`, silent drop |

## 4. Client API sandbox (LogicBison)

| Step | Action | Evidence |
|------|--------|----------|
| 1 | Create a `read` API key in the console | Key prefix only in notes |
| 2 | curl `/v1/news?industry=legal&locale=en` | 200 + envelope |
| 3 | Point LogicBison's news client at the sandbox base URL | Its tests pass |
| 4 | Verify pagination, ETag/304, 429, and error shape | Integration checklist |

## 5. Cleanup

- Delete sandbox keys (revoke in console) after the drill.
- Remove `tmp/` exports.
- Record the drill result in `.work/context/HANDOFF.md` § What this cycle produced.

## 6. Exit criteria

- [ ] One real feed per channel fetched successfully with 304 on the second poll.
- [ ] Fail-open verified with AI disabled and with malformed AI output.
- [ ] Contact message delivered and stored, PII absent from logs.
- [ ] A third-party client (LogicBison) reads `/v1/news` successfully.

---

## Next action

Run the drill in the dev stack during M1; record results in `.work/context/HANDOFF.md`.
