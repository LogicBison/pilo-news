# US Rule-Change Tracker

**Status:** planned · **Type:** asset · **Cadence:** monthly, second Wednesday · **Scope:** US
**Reviewer:** financial compliance reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a compliance or operations lead at a bank, payments firm, or fintech, and an independent advisor who has to change a process before a rule takes effect.

The job: see which proposed or final rule changes an operational process, and when.

## 2. Deliverable

US table of proposed and final rules, compliance dates, and the operational change each one forces

Row cap: 8-12. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| SEC press releases and rulemaking | primary record or verification |
| Federal Reserve | primary record or verification |
| financial channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract rule status, dates, and affected entities; summarize the operational change; never rate an investment or predict markets

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give investment, tax, or legal advice.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: financial
OFFER: US Rule-Change Tracker
FORMAT: asset
READER: a compliance or operations lead at a bank, payments firm, or fintech, and an independent advisor who has to change a process before a rule takes effect.
SCOPE: US
MAX_ROWS: 8-12
REGULATED_ADVICE: investment, tax, or legal advice
SELECT: a new proposal, a final rule, a compliance date, or a regulator statement that changes a reporting or operational obligation. exclude market commentary, earnings, and investment research.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: investment advice; returns; risk-free; buy; sell. Reject any row that contains one.
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

Review time: 45-60 minutes per issue.

The reviewer opens every source, checks every date, edits the one-line change, and signs the issue. The page shows the issue date, the scope, the source version, and the reviewer. A correction is a dated note, not a silent edit.

Publication: a dated page at `/<locale>/financial/brief/<issue-date>` or `/<locale>/financial/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 10 waitlist joins and at least one consultation within 45 days of issue 1.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Add SEC and Federal Reserve adapters. store the issue in `offer_issues`; publish a dated page and an email body from the same JSON. keep the current brief live until issue 1 ships.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- investment advice
- returns
- risk-free
- buy
- sell

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
