# Integrating HeraldFox content

**Status:** verified against production 2026-11-10 · **Audience:** developers and AI agents · **Needs:** nothing
**Scope:** read-only public content — headlines, summaries, topics, sources, theme tokens, feeds.
**Contract:** `docs/api/openapi.v1.json` is the generated schema; this page is the practical path.

Every example below runs against production as written. If one does not, the API changed and this
page is wrong — treat that as a bug in the docs, not in your client.

---

## 1. What you get

HeraldFox publishes twelve editorial desks. Each desk exposes a paginated JSON feed of published
stories with headline, excerpt, an AI-written summary, publisher, publication time, topic tags and a
readable article URL — plus the desk's metadata (name, tagline, theme tokens, disclaimer, active
offers) so a third party can render a native-looking page instead of a generic list.

- **Base URL:** `https://heraldfox.com/v1`
- **Auth:** none for reads. An `X-API-Key: sn_live_...` header raises the rate limit.
- **CORS:** `Access-Control-Allow-Origin: *` on `GET` — browser calls work with no proxy.
- **Format:** JSON, RFC 7807 errors, RSS 2.0 fallback.
- **Rate limit:** 120 requests/min per IP keyless.

## 2. The `health-medicine` desk

| | |
|---|---|
| Slug | `health-medicine` |
| Name | Health & Medicine (`Salud y Medicina` in Spanish) |
| Own host | https://health-medicine.heraldfox.com |
| Topics | `clinical-practice`, `public-health`, `pharma-biotech`, `health-policy`, `hospitals-systems` |
| Sources | KFF Health News, MedCity News, MedPage Today, Fierce Healthcare, WHO News, Redacción Médica, Diario Médico |
| Offers | weekly brief only (no consultation form, no partner routing) |
| Locales | `en`, `es` |

Path URLs work too: `https://heraldfox.com/health-medicine` renders the same desk. Use the subdomain
when you want canonical article links, the apex when you want one origin for every desk.

## 3. Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v1/health` | liveness, no auth |
| `GET /v1/desks?locale=en` | every desk in one call: slug, name, tagline, accent, layout, offers, latest story time |
| `GET /v1/industries` | desk summaries |
| `GET /v1/industries/health-medicine?locale=en` | one desk with theme tokens, cta, disclaimer, offers |
| `GET /v1/news?industry=health-medicine&locale=en&limit=20` | paginated stories |
| `GET /v1/news/bundle?industry=health-medicine&locale=en` | **the one call for a desk page**: featured, columns, items, topics, sources, theme |
| `GET /v1/news/{id}?industry=health-medicine&locale=en` | one story by UUID |
| `GET /v1/topics?industry=health-medicine&locale=en` | topic list with counts |
| `GET /v1/sources?industry=health-medicine&locale=en` | publishers behind the desk |

Query parameters for `/v1/news`: `industry` (required unless the deployment has one desk), `locale`
(`en`/`es`), `limit` (1–50, default 20), `cursor` (opaque `meta.next_cursor`), `topic`, `q` (3–64
chars). **Unknown parameters are a 400**, so build the query string from this list and nothing else.

`limit=51` → `400 limit must be between 1 and 50.` · unknown industry → `404 No industry with slug …`

## 4. First call

```bash
curl -s "https://heraldfox.com/v1/news?industry=health-medicine&locale=en&limit=5"
```

```json
{
  "data": [
    {
      "id": "4a34179c-0f44-5561-86aa-133e3f2e4549",
      "title": "Another Option for Rare Benign Soft-Tissue Tumor Wins FDA Approval",
      "excerpt": "(MedPage Today) -- The FDA approved the small-molecule inhibitor...",
      "summary": "US regulators approved pimicotinib for selected patients...",
      "publisher": "MedPage Today",
      "published_at": "2026-11-10T20:22:20Z",
      "url": "https://health-medicine.heraldfox.com/article/4a34179c-0f44-5561-86aa-133e3f2e4549",
      "language": "en",
      "topics": [{ "slug": "clinical-practice", "label": "Clinical Practice" }],
      "corroboration": 1,
      "verification": "trusted-source"
    }
  ],
  "meta": { "locale": "en", "language": "en", "fallback": false, "next_cursor": null, "generated_at": "..." }
}
```

Field notes that bite:

- `summary` can be `null` (fail-open by design). Fall back to `excerpt`, then to `title`.
- `topics[].label` is already localized; `topics[].slug` is stable — filter on the slug.
- `meta.fallback: true` means the requested locale had no bundle and you got English. Render the
  language honestly.
- `url` points at the story on the desk host; it is safe to link.
- `meta.next_cursor` is opaque. Do not parse it.

## 5. Recipes

### 5.1 A desk page in one request (recommended)

```js
const res = await fetch(
  "https://heraldfox.com/v1/news/bundle?industry=health-medicine&locale=en",
  { headers: { "If-None-Match": cachedEtag ?? "" } },
);
if (res.status === 304) return render(cachedBundle);
const { data } = await res.json();

document.documentElement.style.setProperty("--brand", data.industry.theme.primary);
render(data.industry.name, data.featured.lead, data.items, data.sources);
```

The bundle carries everything a page needs: `industry` (theme, tagline, disclaimer, offers),
`featured.lead` + `featured.favorites`, `columns[]` (pre-grouped stories), `items[]`, `topics[]`,
`sources[]`, `splash[]`, `ai_summary`, `total`, `retention_max_age_days`.

### 5.2 Paginate a feed

```python
import requests

items, cursor = [], None
while True:
    params = {"industry": "health-medicine", "locale": "en", "limit": 50}
    if cursor:
        params["cursor"] = cursor
    body = requests.get("https://heraldfox.com/v1/news", params=params, timeout=10).json()
    items.extend(body["data"])
    cursor = body["meta"]["next_cursor"]
    if not cursor:
        break
```

### 5.3 Theme a page from the API

`GET /v1/industries/health-medicine?locale=en` returns the tokens the site itself uses:

```json
{
  "theme": {
    "primary": "#155e63", "accent": "#b91c1c", "bg": "#ffffff", "surface": "#f2f7f8",
    "text": "#0f172a", "muted": "#4b5563", "border": "#d5e4e2", "radius": "10px",
    "font_heading": "Georgia, Times New Roman, serif",
    "font_body": "system-ui, -apple-system, Segoe UI, sans-serif",
    "layout": "professional"
  },
  "offers": { "brief": true, "consultation": false, "question": false, "asset": false },
  "disclaimer": "News, not medical advice. …"
}
```

Map them straight onto CSS custom properties. Render `disclaimer` verbatim near the stories — the
medical desk's copy is a legal statement, not decoration.

### 5.4 When you cannot run JavaScript

```bash
curl -s https://health-medicine.heraldfox.com/feed.xml      # RSS 2.0, 40 items
curl -s https://health-medicine.heraldfox.com/es/feed.xml   # Spanish
curl -s https://health-medicine.heraldfox.com/sitemap.xml   # every article URL
```

Each RSS item carries `<title>`, `<link>`, `<pubDate>`, `<description>` (the summary) and
`<category>` tags. Poll it on a schedule; it is cheap and cache-friendly.

## 6. Caching, limits, failures

- **ETag:** public reads return a weak `ETag`. Send it back as `If-None-Match` and handle `304` —
  the body does not change until the next ingest or publication.
- **Cache-Control:** `public, max-age=60, stale-while-revalidate=300`. Cache for a minute; serve
  stale for five.
- **Rate limit:** `429` carries `Retry-After` plus `RateLimit-Limit` / `RateLimit-Remaining`. Back
  off, do not retry immediately.
- **Errors** are RFC 7807: `{ type, title, status, detail, instance, request_id }`. Log
  `request_id` — it is the only thing support can trace.
- **Empty desk:** `data: []` with `meta.fallback: false` is a legitimate answer. Render an empty
  state, not an error.

## 7. For AI agents

Read this section, then act. Do not crawl the HTML.

**Rules**

1. One request per page view: `GET /v1/news/bundle?industry=<slug>&locale=<en|es>`.
2. Never scrape `heraldfox.com/<desk>` — the HTML is for humans and changes without notice.
3. Always send `industry`; the API is multi-desk and will `400` rather than guess.
4. Send `If-None-Match` with the last `ETag`; a `304` means "keep what you rendered".
5. Respect `summary: null` — show `excerpt`, and never claim the piece is AI-written.
6. Preserve `publisher`, `published_at` and `url` exactly; attribution is part of the licence.
7. Cache at most 60 s; on `429` wait `Retry-After` seconds.
8. Render `disclaimer` verbatim on any page that shows health content.

**Prompt to hand an agent**

> Integrate HeraldFox's `health-medicine` desk into this site. Fetch
> `https://heraldfox.com/v1/news/bundle?industry=health-medicine&locale=en` once per page render,
> cache by `ETag` for 60 seconds, and render `data.featured.lead` as the hero, `data.items` as a
> story grid (title, publisher, `published_at`, `summary || excerpt`), and link each card to
> `item.url`. Style with `data.industry.theme` as CSS custom properties. Show
> `data.industry.disclaimer` under the grid. If `meta.fallback` is true, label the page as English
> fallback. Never scrape the HTML, never invent fields, and handle `summary: null` and empty `data`.

**Failure modes to expect**

| Symptom | Cause | Action |
|---|---|---|
| `400 invalid-query` | unknown query parameter or `limit` out of range | build the query from §3 |
| `404` on an article | story aged out of the 30-day window | link the desk home instead |
| `429` | keyless burst over 120/min | honour `Retry-After`, request an API key |
| `meta.fallback: true` | no bundle in that locale | render as the returned `language` |

## 8. Before you ship

- [ ] One `bundle` request per page, `ETag` reused, `304` handled.
- [ ] `summary: null` falls back to `excerpt`, never to fabricated text.
- [ ] Publisher and `published_at` rendered on every card.
- [ ] `disclaimer` visible on health pages.
- [ ] `429` and `404` paths handled with a readable state.
- [ ] Links point at `item.url` (the desk host), not at your own copy of the text.

## Next action

Run `curl -s "https://heraldfox.com/v1/news/bundle?industry=health-medicine&locale=en" | jq '.data.industry.name'`
— if it prints `"Health & Medicine"`, the integration path is open. Questions or a key:
`news@heraldfox.com`.
