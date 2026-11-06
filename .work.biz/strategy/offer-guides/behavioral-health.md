# Practice & Payer Brief

**Status:** brief live · **Type:** brief · **Cadence:** weekly, Thursday · **Scope:** US
**Reviewer:** clinical operations reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a practice manager at a small behavioral-health group and a solo clinician who also runs the business side.

The job: know which payer policy, telehealth rule, or safety notice changes how the practice operates this week.

## 2. Deliverable

Five-item weekly brief on payer policy, telehealth rules, and safety alerts that change practice operations

Row cap: 5. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| FDA MedWatch | primary record or verification |
| EMA | primary record or verification |
| CMS | primary record or verification |
| state licensing boards | primary record or verification |
| behavioral-health channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Summarize regulator and payer notices; label operational impact; never give clinical guidance or triage

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give medical or clinical advice.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: behavioral-health
OFFER: Practice & Payer Brief
FORMAT: brief
READER: a practice manager at a small behavioral-health group and a solo clinician who also runs the business side.
SCOPE: US
MAX_ROWS: 5
REGULATED_ADVICE: medical or clinical advice
SELECT: a payer policy change, a telehealth coverage change, a safety alert, or a licensing rule that affects practice operations. exclude clinical studies, opinion pieces, and patient stories.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: medical advice; diagnosis; treatment recommendation; safe for patients. Reject any row that contains one.
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

Publication: a dated page at `/<locale>/behavioral-health/brief/<issue-date>` or `/<locale>/behavioral-health/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of brief views join, and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Keep the current brief capture. add a five-item template and a payer-notice source adapter first; a reference asset only after six weeks of stable sources and a named reviewer. do not add PHI fields.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- medical advice
- diagnosis
- treatment recommendation
- safe for patients

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
