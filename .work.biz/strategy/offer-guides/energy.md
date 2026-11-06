# US Grid Queue & Docket Digest

**Status:** planned · **Type:** asset · **Cadence:** monthly, first Thursday · **Scope:** US
**Reviewer:** energy regulatory reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a project developer, a utility analyst, and a regulatory affairs lead.

The job: know which interconnection queue or docket milestone moved this month.

## 2. Deliverable

US table of interconnection queue changes, docket milestones, and rate-case dates with the project each one touches

Row cap: 6-12. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| ISO/RTO queue pages | primary record or verification |
| LBNL queue data | primary record or verification |
| state PUC dockets | primary record or verification |
| energy channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract queue status, dates, and jurisdictions; summarize the milestone; never forecast prices or interconnection outcomes

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give investment or regulatory advice for a specific project.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: energy
OFFER: US Grid Queue & Docket Digest
FORMAT: asset
READER: a project developer, a utility analyst, and a regulatory affairs lead.
SCOPE: US
MAX_ROWS: 6-12
REGULATED_ADVICE: investment or regulatory advice for a specific project
SELECT: a queue status change, a docket milestone, a rule effective date, or a grid constraint with a date. exclude price forecasts, vendor marketing, and opinion.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: price guarantee; will be approved; guaranteed interconnection; cheapest power. Reject any row that contains one.
```

The user prompt is the common one. Pass the normalized records, the last issue date, and the scope. Do not pass full article bodies; pass the fields the schema needs.

## 6. Validation

- schema valid; every `source_url` returns 200 on publish day;
- no duplicate URL or event;
- every date parses and falls in the scope window;
- row count within 6-12;
- banned-claim scan clean;
- no second-person promise;
- reviewer name present;
- EN/ES row count and dates match.

## 7. Review and publication

Review time: 45 minutes per issue.

The reviewer opens every source, checks every date, edits the one-line change, and signs the issue. The page shows the issue date, the scope, the source version, and the reviewer. A correction is a dated note, not a silent edit.

Publication: a dated page at `/<locale>/energy/brief/<issue-date>` or `/<locale>/energy/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of offer views join and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Start with two RTOs and one state PUC. US only. add EU as a separate adapter and scope later.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- price guarantee
- will be approved
- guaranteed interconnection
- cheapest power

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
