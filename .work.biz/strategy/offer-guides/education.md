# Enrollment Deadline Brief

**Status:** brief live · **Type:** brief · **Cadence:** weekly during term, monthly otherwise · **Scope:** US
**Reviewer:** education policy reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a prospective student or a program administrator who tracks enrollment, aid, and accreditation dates.

The job: know which enrollment, aid, or accreditation date is close enough to act on.

## 2. Deliverable

Five-item brief on enrollment dates, accreditation actions, and aid deadlines with a dated action list

Row cap: 5. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| state higher-ed boards | primary record or verification |
| NCES | primary record or verification |
| accreditor notices | primary record or verification |
| education channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Extract dates and institution names; summarize the decision the date forces; never guarantee admission, aid, or outcomes

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give admissions or financial-aid advice.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: education
OFFER: Enrollment Deadline Brief
FORMAT: brief
READER: a prospective student or a program administrator who tracks enrollment, aid, and accreditation dates.
SCOPE: US
MAX_ROWS: 5
REGULATED_ADVICE: admissions or financial-aid advice
SELECT: a new or changed enrollment window, a financial-aid deadline, an accreditation action, or a state licensing change. exclude rankings, opinion, and program marketing.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: guaranteed admission; guaranteed aid; accredited by; best program. Reject any row that contains one.
```

The user prompt is the common one. Pass the normalized records, the last issue date, and the scope. Do not pass full article bodies; pass the fields the schema needs.

## 6. Validation

- schema valid; every `source_url` returns 200 on publish day;
- no duplicate URL or event;
- every date parses and falls in the scope window;
- row count within 5;
- banned-claim scan clean;
- no second-person promise;
- reviewer name present;
- EN/ES row count and dates match.

## 7. Review and publication

Review time: 20-30 minutes per issue.

The reviewer opens every source, checks every date, edits the one-line change, and signs the issue. The page shows the issue date, the scope, the source version, and the reviewer. A correction is a dated note, not a silent edit.

Publication: a dated page at `/<locale>/education/brief/<issue-date>` or `/<locale>/education/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of brief views join and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Keep the brief. a US deadline calendar is a later reference only after registrar sources are stable. scope the title to US; do not imply EU or Asia coverage.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- guaranteed admission
- guaranteed aid
- accredited by
- best program

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
