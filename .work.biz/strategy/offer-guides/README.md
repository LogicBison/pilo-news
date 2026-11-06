# Offer generation guides

**What this is:** the common pipeline, prompt pack, and quality gate for every channel's free offer. Each channel has its own guide beside this file.
**Status:** Recommendation (2026-11-06). Legal and cybersecurity adapters are implemented; the rest are plans.
**Needs:** a named reviewer per reference channel; email delivery is U8.

## The rule

AI drafts. A named human signs. No source URL, no row. No reviewer, no issue.

An offer is one of two formats:

- **Reference** (asset): a dated table of deadlines, rule changes, recalls, or queue milestones, scoped to the jurisdiction in the title. 5-12 rows.
- **Brief**: a five-item decision note. Three sections: what changed, what date matters, what to ask. 5 items maximum.

The reference is the secondary offer. The email is its delivery, not a second offer. The weekly brief is the secondary offer where a reference cannot be built or reviewed honestly.

## Common pipeline

1. **Collect.** New records since the last issue, from the channel feeds plus the primary source named in the channel guide. Record the source version and the fetch time.
2. **Normalize.** One record becomes `{title, date, jurisdiction, entity, action, source_url, source_name}`. Drop anything missing a URL or a date.
3. **Select.** Keep only what changed and what a professional must act on. Cap at 5 rows for a brief, 12 for a reference.
4. **Draft.** The model returns JSON matching the schema below. It may paraphrase the source. It may not add a fact.
5. **Validate.** Schema, date parse, link check, duplicate check, banned-claim scan, row count, and a "no source, no row" gate. Fail closed.
6. **Review.** A named human opens every source, checks every date, edits the copy, and signs the issue.
7. **Translate.** Only after the English sign-off. Translate commentary; keep proper nouns and source titles in English; second-read every date and action row.
8. **Publish.** One JSON produces the dated page, the archive entry, and the email body. The page states the issue date, the scope, the source version, and the reviewer.
9. **Measure.** `offer_view`, `offer_join`, `issue_published`, `issue_open`, `issue_click`, `question_submit`, `consultation_submit`.

## Prompt pack

System prompt, used by every channel with the channel-specific values replaced:

```text
You are the <CHANNEL> desk editor for System News.
You write a dated <FORMAT> for <READER>.
You only use the records provided. Do not add facts, dates, names, or numbers.
Every row must carry a source_url from the records.
You do not give <REGULATED_ADVICE>. You report what the source published.
If a record is missing a date, a source, or an action, omit it.
Return JSON only. No markdown, no commentary.
```

User prompt:

```text
Offer: <OFFER_NAME>
Issue date: <YYYY-MM-DD>
Scope: <SCOPE>
Last issue date: <YYYY-MM-DD or none>
Max rows: <5 or 12>
Records: <JSON array of normalized records>
Banned claims: <channel banned list>

Select the records that changed since the last issue and that a reader must act on.
Write one plain-language line per row. Keep the source's meaning. Do not interpret
whether the rule applies to a specific reader.
Return the issue JSON.
```

Issue JSON:

```json
{
  "issue_date": "YYYY-MM-DD",
  "offer_slug": "channel-offer-slug",
  "scope": "US",
  "title": "Issue title",
  "standfirst": "One sentence on what changed this issue.",
  "rows": [
    {
      "headline": "What changed, in plain language",
      "change": "The operational change, one sentence",
      "date": "YYYY-MM-DD",
      "jurisdiction": "US",
      "action": "The one action the reader can take",
      "source_name": "Publisher or register",
      "source_url": "https://...",
      "confidence": "high"
    }
  ],
  "watchlist": [
    {"headline": "What is coming", "why": "Why it matters", "source_url": "https://..."}
  ],
  "sources": [
    {"name": "Source", "url": "https://...", "checked_at": "YYYY-MM-DD"}
  ]
}
```

## Validation gate

The build must fail on any of these:

- missing `source_url` or a URL that does not return 200 on publish day;
- a date that does not parse, or a date earlier than the last issue for a "new" row;
- a duplicate source URL or a duplicate event;
- a row count outside 3-12 (reference) or 3-5 (brief);
- a banned claim from the channel guide;
- a second-person promise ("you are covered", "you will save");
- an empty reviewer;
- EN/ES row-count mismatch or a translated date/action that differs from the reviewed English.

## Publication

- Page: `/{locale}/{channel}/brief/{issue-date}` (brief) or `/{locale}/{channel}/reference/{issue-date}` (reference).
- Archive: one index per channel, newest first, public.
- Email: double opt-in, unsubscribe, plain text and HTML from the same JSON.
- Correction: a dated note at the top of the page. Never a silent edit.
- Both locales: English is the source; Spanish is translated after sign-off.

## Measurement

| Event | Definition |
|-------|------------|
| `offer_view` | the card or archive page is seen |
| `offer_join` | waitlist or brief signup |
| `issue_published` | a dated issue is live |
| `issue_open` | email open (after delivery exists) |
| `issue_click` | click to a source or row |
| `question_submit` | ask-one-question form |
| `consultation_submit` | consultation form |

Kill rule per offer after 8 weeks: no issue shipped, reviewer missing for two issues, or joins under 0.2% of offer views. Keep rule: at least 1% of offer views join and at least one consultation is attributed.

## File map

| Path | Purpose |
|------|---------|
| `strategy/offers/catalog.json` | machine-readable offer plan; the inventory reads it |
| `strategy/offer-inventory.md` | generated offer inventory |
| `strategy/offer-guides/<channel>.md` | channel-specific inputs, prompt values, review, and build notes |
| `scripts/offer-inventory.mjs` | inventory generator/check |
| `scripts/offers.sh` | dev wrapper for the generator |

## Next action

Pick one channel from tier 0, name the reviewer, and build issue 1 with the schema above.
