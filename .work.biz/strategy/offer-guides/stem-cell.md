# US Trial & Regulatory Digest

**Status:** planned · **Type:** asset · **Cadence:** monthly, third Tuesday · **Scope:** US
**Reviewer:** clinical or regulatory reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a lab operations lead, a trial-site coordinator, and a regulatory affairs manager.

The job: know which trial status, regulator notice, or manufacturing change moved this month.

## 2. Deliverable

US table of trial status changes, FDA notices, and manufacturing updates with a plain-language change line

Row cap: 6-12. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| ClinicalTrials.gov | primary record or verification |
| FDA | primary record or verification |
| stem-cell channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract registry status, phase, sponsor, and dates; summarize what changed; never call a therapy safe, effective, or approved

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give medical advice or a treatment recommendation.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: stem-cell
OFFER: US Trial & Regulatory Digest
FORMAT: asset
READER: a lab operations lead, a trial-site coordinator, and a regulatory affairs manager.
SCOPE: US
MAX_ROWS: 6-12
REGULATED_ADVICE: medical advice or a treatment recommendation
SELECT: a registry status change, a new regulator notice, a manufacturing or safety communication, or a trial start/completion. exclude preclinical hype, clinic marketing, and patient testimonials.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: safe; effective; cure; approved treatment; clinical advice. Reject any row that contains one.
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

Publication: a dated page at `/<locale>/stem-cell/brief/<issue-date>` or `/<locale>/stem-cell/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of offer views join and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Add a ClinicalTrials.gov adapter and an FDA adapter. keep the digest to registry facts. store the issue in `offer_issues`; publish a dated page and an email.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- safe
- effective
- cure
- approved treatment
- clinical advice

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
