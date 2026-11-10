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

## 2. Overlap

`overlap` is the share of a candidate's current titles the desk already carries
(a normalised exact-title match over the last 30 days). Above 50 % the feed adds
work, not coverage: a fourth wire on the same twenty stories. It is a cheap
upper bound, not a similarity model — a reworded headline counts as new.

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
get out of it. `items_30d`, `items_7d` and `consecutive_failures` are the other
half: a source with clicks but no fresh items is coasting on old coverage.

## 5. The pitch, honestly

"We send you readers" is true and measurable here, and it opens doors with
regulators, exchanges and trade presses. It is not a licence. Where a publisher
says no, the answer is `/bot`, an outreach note, and a replacement source — not
a browser user agent.
