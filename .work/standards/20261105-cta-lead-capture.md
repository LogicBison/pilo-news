# CTA and lead capture - binding rules

**What it is:** the engineering and UX contract for lead CTAs, forms, consent, routing, and funnel instrumentation.
**Status:** Approved for implementation (2026-11-05) · **Needs:** nothing.
**Related:** `.work.biz/strategy/lead-generation.md`, `.work.ui/design-system/20261105-CTA-BRIEF.md`, ADR 013.

---

## 1. Non-negotiables

1. **One primary CTA per page.** Secondary actions never compete visually.
2. **Explicit consent** - unchecked by default, purpose stated, versioned text, timestamp stored.
3. **No dark patterns** - no fake urgency, no pre-checked boxes, no hidden fees, no confirm-shaming, no exit-intent traps.
4. **No sensitive data requests.** Forms warn against PHI/account numbers/SSNs; the server rejects obvious sensitive patterns.
5. **Professional tone per channel** - legal/financial/health copy follows the disclaimers in §4.
6. **No PII in logs, analytics, or URLs** - lead data lives only in `leads` and partner delivery.
7. **Every CTA is measurable** - impression, click, start, submit, qualification events.

## 2. Placement rules

| Surface | Primary CTA | Constraint |
|---------|-------------|------------|
| Channel home | hero card + sticky mobile bar | visible above the fold on 390×844 |
| Article | after summary + end of article | never mid-paragraph; not inside the reading column |
| Search/topic | compact block after results | max 1 |
| About | compact card | - |
| Footer | quiet link | never the only path |
| Mobile | sticky bar after 60% scroll, dismissible | must not cover content permanently |

## 3. Form contract

- Fields: name, email, phone (optional except logistics), company (logistics), need/message, channel-specific select, consent.
- Client + server validation; server is authoritative.
- Honeypot field; rate limit 5/hour/IP; duplicate submission within 10 minutes dropped silently.
- Success replaces the form with a confirmation; no PII echoed; response expectation stated.
- Errors are field-level + summary; rate limit returns 429 with `Retry-After`.

## 4. Per-channel disclaimers (required near the CTA)

| Channel | Disclaimer |
|---------|------------|
| Legal | "News, not legal advice. Attorney advertising. No outcome is guaranteed." |
| Financial | "News, not investment advice. Investing involves risk." |
| Behavioral health | "News, not medical advice. If this is an emergency, call 911." |
| Education | "Program details and outcomes vary; verify with the institution." |
| Logistics | "Rates and timelines vary by lane and season." |

Disclaimers are content (per locale), not hardcoded JSX, and must appear with the CTA, not only in the footer.

## 5. Consent and privacy

- Consent text version stored on the lead; withdrawal deletes/marks the record.
- Retention: 24 months for lead records; 90 days for rejected/spam records; deletion on request within 30 days.
- No sale of the list; partner routing only for the requested channel.
- Privacy policy link beside the consent field.
- DSAR: export and erase supported by the admin API.

## 6. Routing and response

- One partner per channel at v1; assignment stored on the lead; partner receives an email notification and the admin inbox shows it.
- Partner acknowledgment SLA: 24 h; lead status transitions `new → routed → contacted → qualified → closed | spam`.
- No partner sees another partner's leads; no public lead listing.

## 7. Attribution

- Capture `utm_*`, referrer, landing path, article id, channel, locale, and timestamp server-side.
- Store `ip_hash` and `user_agent_hash` (hashed, not raw) for abuse review.
- No third-party marketing pixels without owner approval (U9).

## 8. Instrumentation

Events: `cta_impression`, `cta_click`, `lead_form_start`, `lead_submit` (result), `lead_qualified`. Payloads exclude PII. Server metrics: `leads_total{industry,status}`, `leads_rate_limited_total`, `lead_route_latency_seconds`.

## 9. Acceptance

- [ ] CTA visible above the fold on mobile home; one primary per page.
- [ ] Consent unchecked by default; version + timestamp stored.
- [ ] Form rejects sensitive patterns; no PII in logs/analytics/URLs.
- [ ] 429 after 5 submissions/hour/IP; duplicate within 10 min dropped.
- [ ] Lead routed to partner within 24 h; status transitions audited.
- [ ] Disclaimer present per channel/locale beside the CTA.
- [ ] Funnel events observable in the dashboard.

## Next action

None - binding as written; amend by a new dated standard if the partner model or consent basis changes.
