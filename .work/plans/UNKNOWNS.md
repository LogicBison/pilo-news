# UNKNOWNS - planning registry

**Updated:** 2026-11-05 · **Maintained by:** plan-foundation / plan-master

| ID | Question / blocker | Blocks | Owner | Status |
|----|-------------------|--------|-------|--------|
| U1 | Final project/brand name ("System News" is the working name from the repo directory) | Domain, branding, legal entity, README copy | owner | Open |
| U2 | Production URL shape: one domain with `/{locale}/{industry}` paths, or per-industry domains? | SEO, Caddy config, canonical URLs, ADR 008 | owner | Open |
| U3 | Hosting provider and monthly budget (recommendation: 4 vCPU/8 GB VPS, ≤ USD 40/month) | ADR 005 ratification, backup destination | owner | Open |
| U4 | AI provider, model, and monthly token budget | ADR 010, cost alerts, summary quality | owner | Open |
| U5 | Feed portfolio per industry: which publishers, are their terms compatible with aggregation? | Legal risk R1, source seeding, M1 acceptance | owner | Open |
| U6 | Primary launch industry / pilot channel (recommendation: legal, then financial) | First shipped site, editorial workload | owner | Open |
| U7 | Editorial workflow depth: single admin, or roles/review queue at launch? | Editorial console SPEC scope | owner | Open |
| U8 | Contact-form delivery: transactional email vendor vs SMTP mailbox | Contact flow, secrets, deliverability | owner | Open |
| U9 | Analytics/consent posture: first-party only, or third-party analytics? | Cookie banner, privacy policy, threat model | owner | Open |
| U10 | Expected traffic at launch (< 10k or > 100k daily sessions) and growth plan | Sizing, cache TTLs, scaling trigger | owner | Open |
| U11 | Legal review of disclaimers for legal, financial, and health channels | Channel enablement gate | owner + advisor | Open |
| U12 | Whether sponsored/paid placements are in v1 (affects labeling + disclosure rules) | Content model, disclosure UI | owner | Open |

## Deferred (recorded decisions the owner may revisit)

| ID | Decision | Deferred on | Revisit trigger |
|----|----------|-------------|-----------------|
| U13 | Dedicated search engine (Meilisearch/Typesense) | 2026-11-05 | > 100k articles or sub-50 ms search requirement |
| U14 | Object storage/CDN for media | 2026-11-05 | First image/asset feature or > 50 GB egress/month |
| U15 | Native mobile apps | 2026-11-05 | Post-GA, after API adoption |

## Review log

| Date | Reviewer | Action |
|------|----------|--------|
| 2026-11-05 | plan-foundation | Seeded from doc 01, doc 04 §13 (deferrals), probe ledger |

---

## Next action

None - owner answers tracked in `.work/context/HANDOFF.md` O5.
