# US Regulatory Calendar

**Status:** waitlist · **Type:** asset · **Cadence:** monthly, first Tuesday · **Scope:** US
**Reviewer:** legal reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: in-house counsel, a compliance lead at a mid-size company, and a small-firm partner who tracks deadlines for clients.

The job: know which rule takes effect, which comment window closes, and which filing date is close enough to act on this month.

## 2. Deliverable

US federal table of rule effective dates, comment windows, filing deadlines, and the one action each date triggers

Row cap: 8-12. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| Federal Register API | primary record or verification |
| agency press releases | primary record or verification |
| legal channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract dates and entities from primary notices; draft one-line plain-language rows; never interpret whether a rule applies

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give legal advice or a prediction of how a court or agency will rule.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: legal
OFFER: US Regulatory Calendar
FORMAT: asset
READER: in-house counsel, a compliance lead at a mid-size company, and a small-firm partner who tracks deadlines for clients.
SCOPE: US
MAX_ROWS: 8-12
REGULATED_ADVICE: legal advice or a prediction of how a court or agency will rule
SELECT: a new final rule, a comment window that opens or closes, a compliance date within 90 days, or a court/agency action that changes a deadline. exclude opinions, law-firm marketing, and anything without an official citation.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: legal advice; we win; guaranteed outcome; applies to you. Reject any row that contains one.
```

The user prompt is the common one. Pass the normalized records, the last issue date, and the scope. Do not pass full article bodies; pass the fields the schema needs.

## 6. Validation

- schema valid; every `source_url` returns 200 on publish day;
- no duplicate URL or event;
- every date parses and falls in the scope window;
- row count within 8-12;
- banned-claim scan clean;
- no second-person promise;
- reviewer name present;
- EN/ES row count and dates match.

## 7. Review and publication

Review time: 45-60 minutes per issue for 8-12 rows.

The reviewer opens every source, checks every date, edits the one-line change, and signs the issue. The page shows the issue date, the scope, the source version, and the reviewer. A correction is a dated note, not a silent edit.

Publication: a dated page at `/<locale>/legal/brief/<issue-date>` or `/<locale>/legal/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 10 waitlist joins and at least one consultation attributed to the calendar within 45 days of issue 1.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Implemented 2026-11-06: Federal Register adapter with a legal-relevant agency allow-list, `offer_issues` storage, and `news_api.cli offer build`. The first 12-row draft is generated at scope `US`. Public pages and reviewer-gated publish are built; remaining: named reviewer, email.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- legal advice
- we win
- guaranteed outcome
- applies to you

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
