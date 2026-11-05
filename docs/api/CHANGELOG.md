# API changelog

## v1 - 2026-11-05

- Initial public contract: `/v1/industries`, `/v1/news`, `/v1/news/bundle`,
  `/v1/news/splash`, `/v1/news/{id}`, `/v1/topics`, `/v1/sources`,
  `/v1/contact`, `/v1/leads`, `/v1/cta-events`.
- Admin contract: auth/session, sources, topics, moderation, pins, refresh,
  API keys, audit, industries (including channel creation), leads, partners.
- Language-partitioned reads (EN/ES), cursor pagination, weak ETags,
  RFC 7807 errors, optional API keys, and rate limiting.
- `POST /v1/admin/industries` creates a new industry channel from data; no code
  change is required to launch another vertical.
