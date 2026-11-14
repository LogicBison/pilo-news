# UNKNOWNS - planning registry

**Updated:** 2026-11-14 · **Maintained by:** plan-foundation / plan-master

| ID | Question / blocker | Blocks | Owner | Status |
|----|-------------------|--------|-------|--------|
| U1 | Final project/brand name ("System News" is the working name from the repo directory) | Domain, branding, legal entity, README copy | owner | Open |
| U2 | Production URL shape: one domain with English unprefixed (`/{industry}`) + `/es/{industry}`, or per-industry domains? | SEO, Caddy config, canonical URLs, ADR 007/008 | owner | Open |
| U3 | Hosting provider selection (budget approved: ≤ USD 40/month) | Backup destination, deploy runbook | owner | Open - budget approved 2026-11-05; provider chosen at deploy |
| U4 | AI monthly budget cap value (`AI_MONTHLY_BUDGET_USD`, default 20) | Cost alerts, run sizing | owner | Closed - default 20 approved 2026-11-05 |
| U5 | Feed portfolio per industry: which publishers, are their terms compatible with aggregation? | Legal risk R1, source seeding, M1 acceptance | owner | Closed (technical) - 25 verified feeds across 6 channels, quality policy applied (ADR 014); legal terms review tracked under U11 |
| U6 | Primary launch industry / pilot channel (recommendation: legal, then financial) | First shipped site, editorial workload | owner | Closed - pilot = `legal` (default channel, widest portfolio, most content); financial second |
| U7 | Editorial workflow depth: single admin, or roles/review queue at launch? | Editorial console SPEC scope | owner | Open |
| U8 | Contact-form delivery: transactional email vendor vs SMTP mailbox | Contact flow, secrets, deliverability | owner | Closed - `pilo-mail` gateway (Brevo upstream) chosen 2026-11-05; integration deliberately deferred until after v1 lead capture |
| U9 | Analytics/consent posture: first-party only, or third-party analytics? | Cookie banner, privacy policy, threat model | owner | Open |
| U10 | Expected traffic at launch (< 10k or > 100k daily sessions) and growth plan | Sizing, cache TTLs, scaling trigger | owner | Open |
| U11 | Legal review of disclaimers for legal, financial, and health channels | Channel enablement gate | owner + advisor | Open |
| U12 | Whether sponsored/paid placements are in v1 (affects labeling + disclosure rules) | Content model, disclosure UI | owner | Open |
| U32 | Which trusted edge header supplies country, and what is its value? | `GEO_COUNTRY_HEADER`; country attribution | owner | Open |
| U33 | Does the contact form consent cover marketing use, or is a separate opt-in needed? | marketing use of contact data | owner + counsel | Open |
| U34 | Which reviewer signs the first legal/cybersecurity reference issue? | publish gate; D-005 | owner | Open |
| U36 | Should the worker expose a `/metrics` endpoint, and should compose deploy Prometheus? Every `ai_*` and `ingest_*` series is emitted in the worker process, which has no exporter, and no Prometheus runs in dev or prd - so `ops/prometheus/alerts.yml` (including the new `AiHalted` / `AiCapReached`) and the three Grafana dashboards read nothing today | AI cap + halt alerting (ingestion SPEC R19), observability spec §4, M8 "alerts" claim | owner | Open - raised 2026-11-14 by `@code-verify milestone - M22` gap 4 |

## Deferred (recorded decisions the owner may revisit)

| ID | Decision | Deferred on | Revisit trigger |
|----|----------|-------------|-----------------|
| U13 | Dedicated search engine (Meilisearch/Typesense) | 2026-11-05 | > 100k articles or sub-50 ms search requirement |
| U14 | Object storage/CDN for media | 2026-11-05 | First image/asset feature or > 50 GB egress/month |
| U15 | Native mobile apps | 2026-11-05 | Post-GA, after API adoption |
| U16 | Opt-in translation of selected stories across languages | 2026-11-05 | Spanish coverage gap (R17) or editor demand |
| U17 | Per-channel refresh interval override | 2026-11-05 | A channel needs a different cadence than the global 720 min |
| U18 | Lead monetization: per lead, per qualified lead, or subscription; one partner per channel or multi | 2026-11-05 | First partner contract |

## Review log

| Date | Reviewer | Action |
|------|----------|--------|
| 2026-11-05 | plan-foundation | Seeded from doc 01, doc 04 §13 (deferrals), probe ledger |
| 2026-11-05 | plan-foundation | U4 narrowed to budget; U16/U17 added after ADR 007/010 amendments |
| 2026-11-05 | operator + agent | U5 closed to technical scope (ADR 014); U6 = legal |
| 2026-11-14 | code-repair (from `@code-verify milestone - M22`) | U36 opened: the AI and ingest series are emitted in the worker process and no Prometheus is deployed, so the alert rules are inert |

## Next action

None - owner answers tracked in `.work/context/HANDOFF.md` O5.
