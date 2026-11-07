# Adding an industry channel

System News is a single deployment with channel-as-data. To add a vertical you
do **not** add routes or components: create the channel, add feed sources, and
the public site plus `/v1` discover it.

For a reproducible deployment — every channel, source, topic, and partner in one
file — use the profile importer instead: see `docs/deployment-profile.md`. The
admin calls below remain the interactive path.

## 1. Create the channel

Copy `apps/api/config/industry-template.json` as the starting payload; the
`theme` object and `topics` array are optional but recommended.

Admin session required. The theme is validated for required tokens and WCAG AA
contrast before it is saved. `locales` is optional (defaults to `en` + `es` with
the same name); `topics` seed the scoring vocabulary.

```bash
curl -s -X POST "$API/v1/admin/industries" \
  -H "content-type: application/json" \
  -H "X-CSRF-Token: $CSRF" \
  -b cookies.txt \
  -d '{
    "slug": "manufacturing",
    "code": "MFG_OPS",
    "name": "Manufacturing Operations",
    "theme": {
      "layout": "professional",
      "primary": "#0b4f6c",
      "accent": "#0f766e",
      "bg": "#ffffff",
      "surface": "#f1f5f9",
      "text": "#0f172a",
      "muted": "#475569",
      "border": "#cbd5e1",
      "radius": "6px",
      "font_heading": "Arial, Helvetica, sans-serif",
      "font_body": "system-ui, -apple-system, Segoe UI, sans-serif"
    },
    "locales": {
      "en": {"name": "Manufacturing Operations", "tagline": "Plants, quality, and industrial policy."},
      "es": {"name": "Operaciones de Manufactura", "tagline": "Plantas, calidad y política industrial."}
    },
    "disclaimers": {
      "en": "News, not operational or safety advice.",
      "es": "Noticias, no asesoría operativa ni de seguridad."
    },
    "cta": {
      "kind": "consultation",
      "headline": {"en": "Talk to an industrial partner", "es": "Hable con un socio industrial"},
      "body": {"en": "Tell us what you need.", "es": "Cuéntenos qué necesita."},
      "label": {"en": "Request a consultation", "es": "Solicitar una consulta"}
    },
    "topics": [
      {
        "slug": "automation",
        "label": {"en": "Automation", "es": "Automatización"},
        "weight": 1.3,
        "keywords": {"en": ["automation", "robotics"], "es": ["automatización", "robótica"]}
      }
    ]
  }'
```

The admin console (`/admin` → Channels) exposes the same create form with a
layout preset.

## 2. Add sources

Each source declares one supported language. There is no language detection and
no cross-language dedupe.

```bash
curl -s -X POST "$API/v1/admin/sources" \
  -H "content-type: application/json" \
  -H "X-CSRF-Token: $CSRF" -b cookies.txt \
  -d '{"industry":"manufacturing","name":"Industry Week","feed_url":"https://example.com/feed.xml","language":"en","trust":0.85}'
```

Use `POST /v1/admin/sources/{id}/test` before enabling a feed. HTTP feeds need
`allow_http: true`; private/loopback hosts are blocked.

## 3. Refresh and verify

```bash
POST /v1/admin/refresh {"industry":"manufacturing","force":true}
GET  /v1/news/bundle?industry=manufacturing&locale=en
GET  /v1/industries/manufacturing
```

Curated pinned seeds (`apps/api/config/seeds.json`) are optional; they bypass
fetch and survive the retention window while pinned.

## 3b. Keep the channel inventory current

`docs/channel-inventory.md` lists every live channel with its subdomain address
and layout. It is generated, and it is gated — it cannot go stale quietly:

```bash
./bin/channels.sh --write    # regenerate (live API first, deployment profiles as fallback)
./bin/channels.sh --check    # fail when the file is stale
./bin/channels.sh --urls     # concrete URLs for this machine, port included
```

Three gates catch a stale file: `./bin/start.sh migrate` warns after the seeds
land, `./bin/start.sh test` fails on the check, and CI fails on the check with no
server and no env file (it reads the deployment profiles). Commit the regenerated
file with the channel change.

## 4. Theme contract

Every channel theme must provide `primary`, `accent`, `bg`, `surface`, `text`,
`muted`, `border`, `radius`, `font_heading`, `font_body`, and a `layout` of
`editorial`, `professional`, or `academic`. The server rejects invalid colors,
missing tokens, more than two font families, unknown layouts, and insufficient
contrast. `pnpm check` in `apps/web` verifies all live channels against the same
rules.

## 5. What is automatic

- `/{industry}` and `/es/{industry}` pages, theming, disclaimers, CTA, lead form.
- `/v1/industries`, `/v1/news`, `/v1/news/bundle`, `/v1/topics`, `/v1/sources`.
- Sitemap entries with EN/ES alternates.
- Language fallback semantics and partition isolation.

No application deploy is required; only the data changes. This is the template
contract for any industry.
