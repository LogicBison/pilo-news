# AI Infrastructure & Policy Brief

**Status:** brief live · **Type:** brief · **Cadence:** weekly, Tuesday · **Scope:** US + EU
**Reviewer:** technology policy reviewer required
**Companion:** `strategy/offer-guides/README.md` (common pipeline, prompt schema, validation gate).

## 1. Reader and job

The reader: a CTO, platform lead, or infrastructure engineer who tracks model releases, AI rules, and chip supply.

The job: know which platform policy, model release, export rule, or datacenter constraint changed the build plan this week.

## 2. Deliverable

Five-item weekly brief on model releases, platform policy changes, chip export rules, and datacenter constraints

Row cap: 5. Every row has a date, a jurisdiction, a one-line change, an action, and a source URL. A row without all five does not ship.

## 3. Sources

| Source | Use |
|--------|-----|
| official model and platform changelogs | primary record or verification |
| EU AI Act | primary record or verification |
| BIS export controls | primary record or verification |
| digital-technology channel feeds | primary record or verification |

The channel feeds are context, not proof. A row needs a primary source, not a news article about the source.

## 4. What AI may do

Summarize official releases and policy text; link the primary source; never benchmark a model or predict procurement outcomes

It may not invent a date, a rule number, a product, a jurisdiction, or an obligation. It may not give procurement or compliance advice for a specific stack.

## 5. Prompt values

Use the common system prompt in the README with these values:

```text
CHANNEL: digital-technology
OFFER: AI Infrastructure & Policy Brief
FORMAT: brief
READER: a CTO, platform lead, or infrastructure engineer who tracks model releases, AI rules, and chip supply.
SCOPE: US + EU
MAX_ROWS: 5
REGULATED_ADVICE: procurement or compliance advice for a specific stack
SELECT: a model or platform release with a policy/API change, an AI rule with a date, an export control change, or a datacenter/power constraint. exclude benchmarks, rumors, and vendor marketing.
```

Channel addition to the system prompt:

```text
BANNED CLAIMS: best model; benchmark winner; guaranteed savings; future-proof. Reject any row that contains one.
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

Publication: a dated page at `/<locale>/digital-technology/brief/<issue-date>` or `/<locale>/digital-technology/reference/<issue-date>`, an archive entry, and an email body from the same JSON. Spanish is translated after the English sign-off.

## 8. Distribution and capture

- Card: the channel's secondary offer. It must name the deliverable, the cadence, and the scope.
- Capture: email + consent; double opt-in when delivery is wired.
- Email: `pilo-mail`/Brevo, plain text and HTML, unsubscribe in every send.
- Archive: public, newest first. The email is the habit, not the paywall.

## 9. Metrics and kill rule

Primary: >= 1% of brief views join and one attributed consultation within 60 days.

Kill after 8 weeks if no issue ships, the reviewer is missing for two issues, or joins are under 0.2% of offer views. Keep if at least 1% of offer views join and at least one consultation is attributed.

## 10. Build notes

Keep the brief. a reference asset only after six weeks of stable changelog sources and a reviewer. do not build a model benchmark or a pricing tracker.

The common build seam is `offer_issues` (`industry_id`, `offer_slug`, `issue_date`, `scope`, `reviewer`, `items jsonb`, `published_at`), one CLI command `news_api.cli offer build|publish`, and one page template that renders the issue JSON. Do not fork the pipeline per channel; vary the adapter and the prompt values.

## 11. Never say

- best model
- benchmark winner
- guaranteed savings
- future-proof

## Next action

Name the reviewer, run the first issue in dry-run, and publish only when every row has a live source.
