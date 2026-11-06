# US Consumer Policy & Recall Calendar

**Status:** planned · **Type:** asset · **Cadence:** monthly, fourth Tuesday · **Scope:** US
**Reviewer:** retail compliance reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: an ecommerce operations lead, a compliance manager, and a merchandising lead.

The job: know which consumer-protection date or recall changes a product, listing, or return process.

## 2. Deliverable

US table of consumer-protection effective dates, recalls, and regulatory comment windows with the commercial action

Row cap: 8-12. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| FTC | primary record or verification |
| CPSC | primary record or verification |
| retail channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract dates, products, and obligations; summarize the commercial change; never forecast demand or promise sales lift

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give commercial or legal advice for a specific product.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: retail
OFFER: US Consumer Policy & Recall Calendar
FORMAT: asset
READER: an ecommerce operations lead, a compliance manager, and a merchandising lead.
SCOPE: US
MAX_ROWS: 8-12
REGULATED_ADVICE: commercial or legal advice for a specific product
SELECT: an effective date, a comment window, a recall, or a consumer-protection action with a commercial action. exclude demand forecasts, sales data, and vendor marketing.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: sales lift; demand forecast; guaranteed conversion; best seller. Reject any row that contains one.
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

Publication: a dated page at `/<locale>/retail/brief/<issue-date>` or `/<locale>/retail/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of offer views join and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Add FTC and CPSC adapters. do not build a demand index.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- sales lift
- demand forecast
- guaranteed conversion
- best seller

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
