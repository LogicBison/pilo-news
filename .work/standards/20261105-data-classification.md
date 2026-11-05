# Data Classification - System News v1

**What it is:** data classes, entity mapping, handling rules, and retention for every stored field.
**Status:** Approved for implementation (2026-11-05) · **Needs:** owner confirmation of the contact-message retention period (U9/U12 context).

---

## 1. Classes

| Class | Definition | Examples | Handling |
|-------|------------|----------|----------|
| **Public** | Safe to publish; already public | article titles, publisher names, summaries, channel themes | No restriction; cacheable at the edge |
| **Internal** | Operational data; not secret but not public | source feed URLs, scores, fetch state, refresh stats | Auth for admin reads; never in public API |
| **Confidential** | PII or business-sensitive | contact name/email/phone/message, admin email | Encrypted at rest (disk), least-privilege access, no logs, retention limits |
| **Restricted** | Credentials and keys | API key hashes/pepper, AI key, JWT signing key, DB password | Env/secret store only; never logged; rotation policy |

## 2. Entity-to-class map

| Entity | Field | Class | Notes |
|--------|-------|-------|-------|
| `industries` | slug, name, code | Public | |
| `industries` | theme, disclaimers | Public | Rendered |
| `sources` | name, site_url | Public | Attribution |
| `sources` | feed_url, trust, status | Internal | Admin/ops only |
| `articles` | title, summary, url, publisher, published_at, topics | Public | |
| `articles` | score, corroboration, verification, summary_source | Internal | Exposed only where the API chooses (score not exposed in v1) |
| `topics` | label, keywords | Public / Internal | Labels public; keywords internal |
| `pins` | position, weight | Internal | Effect is public, values are not |
| `api_keys` | label, scopes, rate_limit | Internal | |
| `api_keys` | key_hash, pepper | Restricted | Never returned |
| `contact_messages` | name, email, phone, message | Confidential | PII |
| `leads` | name, email, phone, company, message, ip_hash, ua_hash | Confidential | PII; consent version stored |
| `leads` | industry_id, partner_id, status, utm, source_page | Confidential | Context |
| `partners` | name, contact_email | Confidential | Business contact |
| `cta_events` | event, placement, article_id, locale, session_hash | Internal | No PII; 90-day retention |
| `contact_messages` | industry_id, locale, status | Confidential | Context |
| `audit_events` | actor, action, entity | Internal | May contain admin email → treat as Confidential if so |
| `refresh_runs` | stats | Internal | |
| Logs | request_id, route, status, duration | Internal | No PII, no query strings with emails |
| Backups | full DB dump | Restricted | Encrypted, off-site, 30 days |

## 3. PII inventory

| Field | Purpose | Legal basis | Retention | Erasure |
|-------|---------|-------------|-----------|---------|
| Contact name | Reply to inquiry | Legitimate interest / consent | 90 days | Delete row on request |
| Contact email | Reply | Same | 90 days | Delete row on request |
| Contact phone | Optional callback | Same | 90 days | Delete row on request |
| Contact message | Understand request | Same | 90 days | Delete row on request |
| Lead name | Route to partner | Consent | 24 months | Delete on request (30 days) |
| Lead email/phone | Contact + routing | Consent | 24 months | Delete on request (30 days) |
| Lead message | Understand need | Consent | 24 months | Delete on request (30 days) |
| Lead ip_hash/ua_hash | Abuse review | Legitimate interest | 90 days | Purged with spam retention |
| Admin email | Login identity | Contract | Life of account | Remove account |
| Client API key label + hash | Authentication | Contract | Life of key + 30 days | Revoke/delete |
| Server logs (IP) | Security/rate limiting | Legitimate interest | 14 days | Rotated |

**No** PHI, FERPA education records, PCI card data, or government IDs are collected or ingested. Industry compliance labels in `data.json` describe the **audience**, not data we process.

## 4. Handling rules

- **At rest:** full-disk encryption on the VPS; Postgres data volume encrypted where the provider supports it; backups encrypted before upload.
- **In transit:** TLS 1.2+ everywhere; internal compose network for DB/Redis (no host exposure in prd).
- **Access:** DB access restricted to the app containers; admin PII reads are logged as audit events.
- **Logs:** no emails, phones, message bodies, tokens, or full URLs with query strings; `request_id` correlation only.
- **Exports:** any export containing PII goes to `tmp/`, is deleted after use, and never committed.
- **Third parties:** AI provider receives titles + excerpts (public content) only; email provider receives contact fields for delivery.

## 5. Retention schedule

| Data | Retention | Mechanism |
|------|-----------|-----------|
| Articles (hot) | 7 days visible | Query filter (`published_at >= now - 7d`) |
| Articles (rows) | 30 days | Nightly purge job |
| Contact messages | 90 days | Nightly purge job |
| Leads | 24 months | Nightly purge job |
| Spam/rejected leads | 90 days | Nightly purge job |
| CTA funnel events | 90 days | Nightly purge job |
| Logs | 14 days | Log rotation |
| Audit events | 1 year | Append-only; purge job at 12 months |
| Backups | 30 days | Bucket lifecycle |
| Rate-limit counters (Redis) | 24 h | TTL |

## 6. GDPR-style rights

- **Access/portability:** contact messages exported as JSON on verified request.
- **Erasure:** delete contact rows + audit note; backups age out within 30 days (documented limitation).
- **Objection:** unsubscribe/stop-contact honored by deleting the message and blocking the email hash locally.

## 7. Review log

| Date | Reviewer | Change |
|------|----------|--------|
| 2026-11-05 | plan-foundation | Initial classification |

---

## Next action

None - binding as written; amend with a new dated standard when the stack, threat model, or API contract changes.
