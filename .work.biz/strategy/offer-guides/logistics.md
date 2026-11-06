# US Port & Customs Notice Digest

**Status:** planned · **Type:** asset · **Cadence:** weekly, Monday · **Scope:** US
**Reviewer:** customs or freight operations reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a freight operations lead, a customs broker, and a 3PL manager who has to reroute or re-paper a shipment.

The job: know which port disruption or customs notice changes a lane this week.

## 2. Deliverable

US table of port disruptions, customs notices, and border changes with the lane each one touches

Row cap: 5-10. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| US CBP CSMS | primary record or verification |
| port authority notices | primary record or verification |
| logistics channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract notice dates, ports, and effective windows; summarize the operational change; never quote a rate or transit-time guarantee

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give customs or trade advice for a specific shipment.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: logistics
OFFER: US Port & Customs Notice Digest
FORMAT: asset
READER: a freight operations lead, a customs broker, and a 3PL manager who has to reroute or re-paper a shipment.
SCOPE: US
MAX_ROWS: 5-10
REGULATED_ADVICE: customs or trade advice for a specific shipment
SELECT: a port closure, a customs procedure change, a tariff or documentation change, or a border delay with a dated window. exclude rate commentary, earnings, and vendor marketing.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: rate guarantee; transit-time guarantee; cheapest; guaranteed capacity. Reject any row that contains one.
```

The user prompt is the common one. Pass the normalized records, the last issue date, and the scope. Do not pass full article bodies; pass the fields the schema needs.

## 6. Validation

- schema valid; every `source_url` returns 200 on publish day;
- no duplicate URL or event;
- every date parses and falls in the scope window;
- row count within 5-10;
- banned-claim scan clean;
- no second-person promise;
- reviewer name present;
- EN/ES row count and dates match.

## 7. Review and publication

Review time: 30-45 minutes per weekly issue.

The reviewer opens every source, checks every date, edits the one-line change, and signs the issue. The page shows the issue date, the scope, the source version, and the reviewer. A correction is a dated note, not a silent edit.

Publication: a dated page at `/<locale>/logistics/brief/<issue-date>` or `/<locale>/logistics/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of offer views join and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Add a CBP CSMS adapter and a port-notice adapter. publish a dated page and a weekly email. do not build a rate index.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- rate guarantee
- transit-time guarantee
- cheapest
- guaranteed capacity

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
