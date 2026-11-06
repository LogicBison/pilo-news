# Product feasibility and strategy verification

**What it is:** can the gated products be generated (AI + public sources) for the promised jurisdictions, and does the strategy survive an evidence pass? Where a product cannot be generated honestly, this names the replacement.
**Status:** Draft (2026-11-05) — verification of `.work.biz/strategy/lead-generation.md`, `20261105-lead-magnet-recommendations.md` and `20261105-offer-and-leadgen-brief.md`.
**Needs:** owner decision on D4 (jurisdiction scope: US + EU only, or add Asia per-market), D5 (drop the logistics rate index).

---

## 1. Verdict

| Channel | Offered product | AI-generatable? | Jurisdictions | Verdict |
|---------|-----------------|-----------------|--------------|---------|
| cybersecurity | CVE / KEV digest | **yes** — NVD + CISA KEV are free, machine-readable, daily | global | keep, strongest product |
| manufacturing | recall + standards tracker | **yes (recalls)** — CPSC, EU Safety Gate, FDA APIs | US + EU | keep, but standards part (ISO/EN) is paywalled — cite recalls and regulator notices only |
| stem-cell | trial + protocol digest | **yes** — ClinicalTrials.gov, EU CTR, WHO ICTRP | US + EU + global registries | keep; never phrase as clinical advice |
| financial | rule-change tracker | **yes** — SEC/Federal Reserve/FCA/ESMA publications | US + EU/UK | keep, scope stated as US + EU/UK |
| legal | regulatory calendar | **yes, with review** — Federal Register API, EUR-Lex | US + EU | keep, scope stated; Asia not covered |
| energy | grid / interconnection digest | **partial** — LBNL queue data + ISO/RTO queue pages; ENTSO-E for EU | US + EU | keep for US; EU needs one more source; Asia out |
| education | enrollment deadline calendar | **partial** — US state boards + NCES; EU national ministries are fragmented | US | keep US only; EU/Asia manual curation |
| behavioral-health | clinical/practice brief | **no as drafted** — would be clinical guidance | — | replace with safety-alert + reimbursement-policy digest |
| retail | demand/holiday calendar | **no** — demand data is proprietary | — | replace with consumer-policy + recall calendar |
| logistics | rate / lane index | **no** — rate indices (Freightos, Drewry) are licensed products | — | replace with port-disruption + customs-notice digest |

**Short answer to "any jurisdiction (America + Europe + Asia)": no, not today.** Three separate constraints:

1. **Source access.** US federal data is public domain and API-friendly. EU is reusable under Decision 2011/833/EU with attribution, but national transposition lives in 27 fragmented portals. Asia is uneven: Singapore, Japan, and Korea publish machine-readable law (JP/KR in local language); China and India are the hard cases (access restrictions, language, licence uncertainty).
2. **Language.** The product ships EN + ES only. Japanese, Korean, and Chinese primary sources would need translation before publication; AI translation is feasible, but a wrong translation of a legal deadline is a liability, not a typo.
3. **Liability.** A "calendar" row that is wrong, or a "tracker" that misses an amendment, is a false statement to a professional audience. Public sources plus AI drafting still need a named reviewer per issue.

## 2. What "generatable" actually requires

| Requirement | Why it binds |
|-------------|--------------|
| Primary source, machine-readable | AI cannot invent deadlines; every row needs a citation URL |
| Reuse licence | US public domain, EU reuse decision, Asia varies; paywalled standards cannot be republished |
| Freshness | a monthly calendar needs a weekly source check; CVE digest needs daily |
| Reviewer | one named human signs each issue; AI drafts, the human certifies |
| Language | EN/ES only today; other markets need translation plus a second reviewer |
| Non-advice framing | summary of what a regulator published, never what the reader should do |

Cost shape: a per-channel asset is ~2–6 hours of agent time to build the generator plus 1–2 hours of human review per issue. That is payable; a per-jurisdiction expansion multiplies review cost, not generation cost.

## 3. Jurisdiction matrix

| Source family | US | EU | Singapore | Japan | Korea | India | China |
|---------------|----|----|-----------|-------|-------|-------|-------|
| Legislation / regulation | Federal Register, eCFR — **yes** | EUR-Lex + national portals — **yes (fragmented)** | SSO — partial | e-Gov — partial, JA only | law.go.kr — partial, KO only | gazette — partial | NPRC — restricted |
| Recalls / product safety | CPSC, FDA — **yes** | Safety Gate — **yes** | HSA — partial | METI — partial | MFDS — partial | FSSAI — partial | SAMR — hard |
| Clinical trials | ClinicalTrials.gov — **yes** | EU CTR — **yes** | HSA — partial | jRCT — partial | CRIS — partial | CTRI — partial | hard |
| Security advisories | NVD, CISA KEV — **yes** | ENISA, CERT-EU — **yes** | CSA — yes | JPCERT — yes | KISA — partial | CERT-In — partial | CNCERT — hard |
| Energy grid | ISO/RTO queues, LBNL — **yes** | ENTSO-E — **yes** | EMA — partial | OCCTO — partial | KPX — partial | CEA — partial | hard |
| Freight rates | proprietary | proprietary | proprietary | proprietary | proprietary | proprietary | proprietary |

Current inventory for calibration: 45 enabled feeds, 28 EN / 17 ES, publishers concentrated in the US and Spain. Nothing today reads a regulator API. So the gap between "we have feeds" and "we have jurisdiction coverage" is a build, not a tweak.

## 4. Replacement products (keep the promise, change the promise)

| Channel | Ship this instead | Source | Why it is safe |
|---------|-------------------|--------|----------------|
| logistics | **Port disruption & customs notice digest** — weekly, US + EU ports | port authority notices, CBP CSMS, EU customs | public notices, no proprietary pricing, directly useful to a freight reader |
| retail | **Consumer policy & recall calendar** — monthly, US + EU | FTC/CPSC, EU Safety Gate, EUR-Lex consumer files | dated, citable, no demand forecasts |
| behavioral-health | **Safety-alert & reimbursement digest** — monthly | FDA MedWatch, EMA, CMS/local payer notices | regulator text summarized; no clinical guidance |
| education | **US enrollment deadline calendar** — per term | state boards, NCES, university registrar pages | dates are checkable; scope limited to US |
| legal / financial / energy / stem-cell / manufacturing / cybersecurity | keep as offered, with the jurisdiction stated in the asset title | see §3 | US + EU sources are citable and fresh |

Rule for all of them: the asset title carries the jurisdiction ("US + EU") and the issue date. No asset claims global coverage.

## 5. Strategy verification

Claim-by-claim, using what the repository and the sources actually support.

| # | Claim | Grade | Evidence / problem |
|---|-------|-------|--------------------|
| V1 | The brief promises a Monday email | **A** | `messages/en.json` `brief.value1`; no sender exists. Owner states delivery lands before production; until then the copy is ahead of the system |
| V2 | "45/45 sources verified" | **A for technical, unknown for legal** | `verify-sources` checks reachability/quality; publisher terms remain U11 |
| V3 | "Any jurisdiction" implied by the offer list | **A (false)** | 45 feeds, US + Spain publishers only; no regulator API integration; EN/ES only |
| V4 | "Reply within one business day" | **C** | Service commitment with no partner signed (U18); becomes false the day a lead is missed |
| V5 | Funnel targets (2% CTR, 40% start, 50% submit, 60% qualified) | **D** | Assumptions; no traffic baseline (U10), no read-out until this session's `/v1/admin/funnel` |
| V6 | "One partner per channel" | **C** | Design intent; partners table exists, none active in production |
| V7 | Lead routing within 24 h ≥ 95% | **D** | No SLA mechanism (R6 unbuilt) |
| V8 | "No PII in logs" | **A** | Contract tests assert lead responses carry no email/name/phone; log scrubbing pattern in place |
| V9 | Gated asset beats generic newsletter | **C** | Publisher benchmarks are vendor-reported; hypothesis only |
| V10 | Lower-friction ask (one question) raises conversion | **C** | Standard funnel behaviour; now measurable (question events + funnel read-out) |

Strategy-level findings:

- **The offer ladder was aspirational in one place and still is in another.** L2 capture exists; L2 delivery does not (V1). L1 consultation exists; L1 follow-through depends on a partner (V4/V7).
- **Jurisdiction scope was never stated, so it read as "everywhere".** Either scope it in the asset copy (recommended) or fund per-market curation.
- **The recommended product for logistics cannot be built.** Rate indices are licensed; promising a "rate and lane index" would force either fabrication or a vendor contract. Drop it now, not after the first complaint.
- **Two products would create clinical and financial-advice exposure.** "Practice brief" and "protocol digest" drift toward guidance; reframe as regulator-summary digests.
- **The funnel is now measurable, which retires the biggest unknown.** `/v1/admin/funnel` plus UTM capture turns V5 from opinion into data after a few weeks.

Implementation reality check (what shipped this session): UTM capture, funnel read-out (+ admin tab), ask-one-question rung, asset waitlist card, briefs archive, topic hubs, disposable-domain rejection, new lead kinds `question`/`asset` with migration 010. Not shipped: email delivery (owner: pre-production), partner SLA loop (U18), ES feed parity for retail.

## 6. Generation pipeline (what it takes to keep the promise)

1. **Source adapters** per family (Federal Register, EUR-Lex, CPSC, NVD/KEV, ClinicalTrials.gov, ISO queue pages) with a citation URL per row.
2. **Drafting** — AI turns fetched records into one-line plain-language entries; no interpretation beyond the source text.
3. **Validation** — every row must resolve to a live URL; a broken link blocks the issue.
4. **Human sign-off** — one named reviewer; the issue records who signed it.
5. **Publication** — dated archive page (the briefs archive already exists), email to the waitlist.
6. **Correction policy** — a wrong row gets a dated correction note; silent edits are not allowed.

## Decisions needed

1. **D4 — jurisdiction scope:** publish "US + EU" assets and say so in the title, or fund Asia curation per market (Singapore first)?
2. **D5 — drop the logistics rate index** in favour of the port/customs digest?
3. **D6 — reviewer:** who signs each asset issue (owner, advisor, or per-channel contractor)?

## Open questions

1. Is a paid data vendor (freight rates, ISO standards) ever in scope, or is the product permanently public-source only?
2. Does the asset archive need email-gated access, or is public-with-archive enough (current: public)?

## Next action

Approve D4–D6; then build one asset end to end (cybersecurity KEV digest is the cheapest proof) before promising any other channel's asset.
