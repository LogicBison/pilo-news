# CISA KEV Digest

**Status:** waitlist · **Type:** asset · **Cadence:** weekly, Wednesday · **Scope:** global
**Reviewer:** security reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: the IT generalist at a 20-200 person organization who also does security.

The job: know which newly exploited vulnerability touches software they run, and what to do about it.

## 2. Deliverable

5-12 new known-exploited vulnerabilities, filtered to the reader's vendor stack, one action per row

Row cap: 5-12. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| CISA KEV JSON | primary record or verification |
| NVD 2.0 | primary record or verification |
| cybersecurity channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Filter, dedupe, and paraphrase the required action; never claim a system is safe or a patch is sufficient

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give security or incident-response advice for a specific environment.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: cybersecurity
OFFER: CISA KEV Digest
FORMAT: asset
READER: the IT generalist at a 20-200 person organization who also does security.
SCOPE: global
MAX_ROWS: 5-12
REGULATED_ADVICE: security or incident-response advice for a specific environment
SELECT: entries added since the last issue; include a 'missed in the last four weeks' block of up to 15 rows. exclude older catalog rows, vendor marketing, and exploit tutorials.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: you are secure; patch is sufficient; no risk; guaranteed protection. Reject any row that contains one.
```

The user prompt is the common one. Pass the normalized records, the last issue date, and the scope. Do not pass full article bodies; pass the fields the schema needs.

## 6. Validation

- schema valid; every `source_url` returns 200 on publish day;
- no duplicate URL or event;
- every date parses and falls in the scope window;
- row count within 5-12;
- banned-claim scan clean;
- no second-person promise;
- reviewer name present;
- EN/ES row count and dates match.

## 7. Review and publication

Review time: 30-60 minutes per weekly issue.

The reviewer opens every source, checks every date, edits the one-line change, and signs the issue. The page shows the issue date, the scope, the source version, and the reviewer. A correction is a dated note, not a silent edit.

Publication: a dated page at `/<locale>/cybersecurity/brief/<issue-date>` or `/<locale>/cybersecurity/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 10 waitlist joins, >= 3 distinct company domains, and one attributed readiness inquiry within 45 days of issue 1.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Implemented 2026-11-06: CISA KEV adapter and `offer_issues` storage; the first 12-row draft is generated at scope `global`. The vendor stack filter, public issue page, reviewer sign-off, and email remain. The page must exist before the card promises an email.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- you are secure
- patch is sufficient
- no risk
- guaranteed protection

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
