# Source acquisition

How a feed becomes a source, and how the platform proves it earns its place.
Companion to [`source-quality.md`](source-quality.md) (grading) and
[`deployment-profile.md`](deployment-profile.md) (how sources are declared).

## 1. Discover

```bash
./bin/sources.sh discover --file candidates.txt --industry legal
./bin/sources.sh discover --url https://example.com/feed.xml
```

`candidates.txt` is either one URL per line or an OPML export from a feed
reader. Discovery is **read-only**: it never writes a source.

Each candidate gets four independent tests, in this order:

| Test | Failure looks like |
|---|---|
| Permission | `robots.txt disallows this path` — the feed is never contacted |
| Quality | the same policy `verify-sources` uses: <3 items, stale >45 days, language mismatch, duplicate titles |
| Novelty | `overlap 62%: the desk already carries these stories` |
| Fit | `already configured (disabled): The Register` |

Read the report top to bottom; `verdict` is `accept`, `review`, or `reject`.
`review` means it passed but is either thin (grade B/C) or overlaps more than
half the desk — a judgement call, not a yes.

Accepted candidates also come back as a `profile_snippet`: paste it into the
desk's `config/deployments/<slug>.json` under `sources`, then
`apply-profile`. Discovery never edits a profile for you, because the profile
is the reviewable record of what the desk publishes.

`--save` keeps the findings in a candidate queue instead of losing them with
the terminal:

```bash
./bin/sources.sh discover --file feeds.opml --industry legal --save
./bin/sources.sh candidates list --status new
./bin/sources.sh candidates decide --id <id> --status accepted --note "editorial review"
```

`accepted` prints the profile snippet; `shortlisted` and `dismissed` keep the
reason. A dismissed feed that shows up again in a later export is updated but
keeps its decision — discovery never silently reopens a closed call.

## 2. Overlap

`overlap` is the share of a candidate's current titles the desk already carries
over the last 30 days. Matching is token-based (Jaccard, plus the overlap
coefficient so a reworded headline still counts). Above 50 % the feed adds work,
not coverage: a fourth wire on the same twenty stories. It remains an
approximation — a rewritten headline with different words will slip through,
which is why a `review` verdict exists.

## 3. Licence and outreach

Every source carries `licence_type`: `unknown`, `public-domain`, `cc-by`,
`cc-by-sa`, `syndication`, `licensed`, `proprietary`. It answers "why may we
publish a headline and an excerpt" without re-reading a terms page. Government
and regulator feeds are `public-domain`; everything not yet checked stays
`unknown`, which is honest rather than optimistic.

```bash
./bin/sources.sh outreach --source <id> --note "asked to allowlist HeraldFoxBot"
```

Records `contacted_at` and the note; both show in the admin Sources row. Pair it
with the `/bot` page — that page is the thing you link to in the email.

## 4. Return traffic

Every "read the full story" link goes through `/go/{article_id}` →
`GET /v1/outbound/{article_id}`, which counts one click against that article and
302s to the publisher. Aggregate only: no reader identifier, no IP, no user
agent, no referrer (`Referrer-Policy: no-referrer`). Hidden and archived
articles 404.

```bash
./bin/sources.sh health --industry legal
```

`clicks_30d` per source is the number to quote when a publisher asks what they
get out of it. `attempts_30d`, `ok_30d`, `success_rate_30d`, `avg_ms_30d` and
`items_30d` are the other half: a source with clicks but no fresh items is
coasting on old coverage, and one with attempts but no successes is failing
quietly. Those counters come from `source_fetch_stats`, written by every ingest
fetch.

## 5. Publisher traffic page

```bash
./bin/sources.sh traffic --source <id>
# http://localhost:43991/traffic/<token>
```

An unguessable, per-source link that shows that publisher their own numbers:
stories we linked, clicks we sent, requests to their feed, and the success rate
over 30 days. No other source, no reader data, `noindex`. Send it with an
outreach note; it is what turns the traffic argument into a document.

## 6. Keeping the queue honest

```bash
./bin/sources.sh candidates refresh --older-than 7 --limit 10
```

Re-grades `new` and `shortlisted` candidates that have been sitting: grade,
overlap, language and verdict are refreshed, status is untouched. Run it
weekly (or from a cron) so a shortlist is never approved on last month's
evidence.

## 7. Value and retirement

`sources health` adds `value_score` (`items + 5 × clicks`) and
`retirement_reason`. A source is proposed for retirement when it produced no
items from at least three attempts, or fewer than five items with no return
clicks. Disabled sources are never proposed, and a thin source that sends
readers is left alone.

## 8. Formats

RSS 2.0, Atom and **JSON Feed 1.x** all parse into the same shape
(`parse_feed`). JSON Feed's `summary` / `content_text` becomes the excerpt,
`url` / `external_url` the link, `date_published` / `date_modified` the date.

## 9. Portability

```bash
./bin/sources.sh export > portfolio.opml
```

Exports the enabled portfolio as OPML grouped by desk; the same format
`discover` accepts, so it round-trips. Useful for backups, for handing the list
to a colleague, and for diffing dev against prd.

## 10. The pitch, honestly

"We send you readers" is true and measurable here, and it opens doors with
regulators, exchanges and trade presses. It is not a licence. Where a publisher
says no, the answer is `/bot`, an outreach note, and a replacement source — not
a browser user agent.
