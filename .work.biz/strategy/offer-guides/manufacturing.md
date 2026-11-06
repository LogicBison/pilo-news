# US Recall & Regulator Notice Tracker

**Status:** planned · **Type:** asset · **Cadence:** monthly, second Thursday · **Scope:** US
**Reviewer:** quality or EHS reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a plant manager, a quality lead, and an EHS manager.

The job: know which recall, safety notice, or regulator action affects a product or process this month.

## 2. Deliverable

US table of recalls, safety notices, and regulator actions with product, hazard, and action

Row cap: 8-12. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| CPSC | primary record or verification |
| FDA | primary record or verification |
| manufacturing channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract product, hazard, and remedy; link the notice; never certify compliance or reinterpret a standard

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give compliance certification or a legal interpretation.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: manufacturing
OFFER: US Recall & Regulator Notice Tracker
FORMAT: asset
READER: a plant manager, a quality lead, and an EHS manager.
SCOPE: US
MAX_ROWS: 8-12
REGULATED_ADVICE: compliance certification or a legal interpretation
SELECT: a new recall, a safety notice, or a regulator action with a product and a remedy. exclude ISO/EN standard text, vendor marketing, and compliance certification claims.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: compliant; certified; safe; meets ISO. Reject any row that contains one.
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

Review time: 30-45 minutes per issue.

The reviewer opens every source, checks every date, edits the one-line change, and signs the issue. The page shows the issue date, the scope, the source version, and the reviewer. A correction is a dated note, not a silent edit.

Publication: a dated page at `/<locale>/manufacturing/brief/<issue-date>` or `/<locale>/manufacturing/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of offer views join and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Add CPSC and FDA recall adapters. do not republish ISO/EN standards. publish a dated page and a monthly email.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- compliant
- certified
- safe
- meets ISO

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
