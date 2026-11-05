# Feature SPECs (`.work/features/`)

One folder per feature **slug** (kebab-case).

| File | Purpose |
|------|---------|
| `YYYYMMDD-SPEC.md` | Binding behaviour (FEATURE_STANDARD §3) |
| `CHANGELOG.md` | Release notes after merge |
| `YYYYMMDD-SPEC-amendment-NN.md` | Post-approval changes (do not edit merged SPEC) |

## Index

| Slug | SPEC | Status |
|------|------|--------|
| `news-api` | `news-api/20261105-SPEC.md` | Draft - public read/admin API contract |
| `news-api` acceptance | `news-api/20261105-acceptance-matrix.md` | Draft - 28 reference scenarios adapted |
| `ingestion-pipeline` | `ingestion-pipeline/20261105-SPEC.md` | Draft - feeds, scoring, dedupe, AI summaries |
| `industry-sites` | `industry-sites/20261105-SPEC.md` | Draft - themed landing pages, i18n, SEO |
| `editorial-console` | `editorial-console/20261105-SPEC.md` | Draft - minimal admin surface |

**Create:** `@feature-spec create - <slug>`
**Template:** `.ai/templates/work/features/example-slug/YYYYMMDD-SPEC.md.template`
