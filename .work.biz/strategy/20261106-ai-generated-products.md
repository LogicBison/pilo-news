# AI-generated products - what else can be put together

**What it is:** a product catalog for System News built from what AI can do with the data the system already has or can cite. It covers the 7-day briefing, the legal calendar question, and six more products that fit the same pipeline.
**Status:** Recommendation (2026-11-06).
**Needs:** a product priority decision; a jurisdiction filter decision; email delivery (U8) for any subscription product.
**Builds on:** `20261106-ai-offer-system.md`, `offer-inventory.md`, `.work/features/offer-generation/20261106-SPEC.md`.

---

## 1. Loaded context

```
LOADED CONTEXT
  Build target:  extension of the live System News platform (11 channels, 2 reference adapters)
  User:          professionals in each channel: counsel, compliance, practice manager, freight ops, IT generalist
  Buyer:         partner firms routing inquiries; the reader is not the payer
  Stack:         FastAPI, Postgres, Redis worker, Next 15, DeepSeek, offer_issues, Federal Register + CISA KEV
  Build capacity: solo + agent, 6-12 week envelope
  Price point:   free lead magnet; partner-funded inquiries; no paid tier in v1
  Gaps:          traffic baseline (U10), partner model (U18), named reviewers for publish, email delivery (U8)
```

The stack already does the expensive part: ingest, score, summarize, store, serve, and capture. The next products should reuse that, not add a second content system.

---

## 2. Verdict

Seven-day news selection is the easiest product, but it is not the strongest. It is a **habit product**: cheap to generate, weak to differentiate, and easy to copy. It should be the baseline on every channel because it costs little and gives the list a reason to exist.

The stronger products are **structured, dated, and filterable**:

1. a jurisdiction-tagged calendar (not one calendar per country);
2. a change log that says what moved since the last issue;
3. a watchlist filtered to the reader's stack, state, or topics;
4. a recall/enforcement watch where a public register already publishes rows;
5. a document checklist generated from cited rules;
6. an answer pack that turns one question into a sourced response;
7. an exportable dataset for analysts and partners.

The binding constraint is not generation. It is **source access and review**. AI can draft every one of these. It cannot make a weak source authoritative, and it cannot carry the liability of a wrong deadline.

Recommendation: build the **7-Day Desk Brief** as the baseline, then the **jurisdiction filter** on the existing calendar, then the **change log**. Do not build a separate calendar per country.

---

## 3. What AI can actually do

Five levels, ordered by trust and effort. Most product ideas fail because they are pitched at level D but described as level A.

| Level | AI job | Example | Source requirement | Review |
|-------|--------|---------|--------------------|--------|
| **A. Select and summarize** | choose 5 items from the existing feeds, write a short brief | 7-Day Desk Brief | the feed item itself | light |
| **B. Extract from a structured API** | pull dates, entities, status from a public JSON/XML API | Federal Register calendar, CISA KEV, CPSC recalls | API field + URL | medium |
| **C. Extract from an unstructured public page** | read a regulator page, pull the date and action | state licensing board, port notice | page URL + quote | heavy |
| **D. Discover via web search** | find sources and facts the system does not subscribe to | "what changed in Spain this week" | primary URL after discovery | heavy, and AI search is not a source |
| **E. Advise or personalize a decision** | tell the reader what to do | "should I file?" | none | out of bounds |

The viable products sit in A-C. Level D is useful for **finding** a source, never for publishing a fact. Level E is the partner's job, not the desk's.

---

## 4. The legal calendar question

The user's instinct is right: do not generate one calendar per country if one dataset can carry a jurisdiction tag. But "per country is easy" is false at the source layer. The generation is easy; the source acquisition and verification are not.

### 4.1 Four ways to handle jurisdiction

| Option | What it means | Pros | Cons | Verdict |
|--------|----------------|------|------|---------|
| **A. One calendar per country** | a separate issue, generator, and reviewer per country | clear scope; simple page | duplicated infrastructure; coverage gaps; false completeness on each page | reject |
| **B. One dataset, rows tagged by jurisdiction** | one issue, every row has a `jurisdiction`; the reader filters | one schema, one generator, one reviewer; new country = new adapter; no global claim | needs a jurisdiction taxonomy; filter UI | **recommended** |
| **C. IP-based default** | the reader's country sets the default filter | zero-friction | VPN/corporate egress gets it wrong; privacy; no consent | use only as a **default with a visible override**, never a hidden assumption |
| **D. AI web search as the source** | the model searches and writes the calendar | broad coverage | hallucination, no stable citation, ToS, maintenance | discovery only; never publish |

### 4.2 Recommended shape

- One `offer_issues` row per issue, with `scope` = the issue's stated coverage (`US`, later `EU`, later `US + EU`).
- Every row carries `jurisdiction` (`US`, `EU`, `US-CA`, etc.). The data model already has this field.
- The page shows a jurisdiction filter. Default order: saved preference, then IP country, then `all`. The reader can always override.
- A `US + EU` issue is allowed only after both adapters run and one reviewer signs the combined table. A title never implies coverage the adapters do not have.
- IP handling: read a country header at the edge, keep only the two-letter code in the session, do not store the IP, and show the choice. No geolocation database in v1.

### 4.3 What it costs

| Piece | US | EU | Per additional country |
|-------|----|----|------------------------|
| Source adapter | Federal Register, done | EUR-Lex + Commission, 1-2 weeks | 1-3 weeks, source dependent |
| Taxonomy | federal + state codes | member state + EU | mapping work |
| Reviewer | one US reviewer | one EU reviewer | per jurisdiction |
| Generation | cheap | cheap | cheap |

The cost is the adapter and the reviewer, not the AI call. That is why "one dataset + filter" wins: the adapter is reusable and the reader sees only what applies.

### 4.4 What I would not do

- A separate generator per country. It multiplies maintenance and hides gaps.
- A calendar that claims "global" because the model found a few rows.
- A hidden IP assumption. A wrong country is worse than asking.

---

## 5. Product catalog

Eight products, ordered by how directly they reuse the current stack.

### 5.1 7-Day Desk Brief

**Type:** free email + public issue, every channel.
**Primary user:** the professional who reads the channel weekly, not daily.
**Core problem:** the site shows the news; the reader still has to decide what mattered in the last seven days.
**What it does:** selects 5 items from the last 7 days, writes one line on what changed, one date to watch, and one question the reader can ask. Every item links to the source.
**MVP features:**
1. 5 items, one line each.
2. "What changed", "date to watch", "what to ask" sections.
3. archive page, one CTA to the inquiry form, EN/ES.
**Integrations:** existing feeds, `offer_issues`, AI client, email later.
**Tech fit:** 80% built. The issue table and builder exist; a brief renderer is a smaller variant of the reference renderer.
**Pricing:** free; partner-funded inquiry.
**How to validate in 2 weeks:** send two issues to 10 target readers by hand; ask "would you open this every week?" and count replies. Success: 3 yes or 2 replies with a specific item they used.
**MVP build estimate:** 3-5 days.
**The thing that makes it hard:** selection quality. A feed dump with a summary is not a brief.
**Why it has not been built:** the current brief is capture-only; the reference pipeline was built first.

### 5.2 Jurisdiction-Tagged Calendar

**Type:** reference table with a filter.
**Primary user:** counsel, compliance, plant EHS, energy developer, retailer.
**Core problem:** a deadline matters only if it applies to the reader's jurisdiction.
**What it does:** one dated table, rows tagged by country/state, filterable; AI extracts dates and actions from a primary source; the reader sees only the selected jurisdiction.
**MVP features:**
1. rows with `jurisdiction`, `date`, `action`, `source_url`;
2. filter by jurisdiction, remembered locally;
3. issue scope stated in the title;
4. no "global" claim.
**Integrations:** Federal Register (done), EUR-Lex (next), state/agency sources later.
**Tech fit:** 90% built for US; the filter is a UI change; EU is a new adapter.
**Pricing:** free; the filtered dataset can become a paid export later.
**How to validate in 2 weeks:** add the filter to the existing legal draft; ask 10 readers which jurisdiction they would pick; measure filter use and joins.
**MVP build estimate:** 3-5 days for the filter and page; 1-2 weeks for EU.
**The thing that makes it hard:** source coverage and one reviewer per jurisdiction, not generation.
**Why it has not been built:** the first legal draft is US-only and has no public page yet.

### 5.3 Change Log / Delta Brief

**Type:** short delta block, all reference channels.
**Primary user:** the returning reader who already saw the last issue.
**Core problem:** a full issue is too much when only three rows moved.
**What it does:** compares the new issue to the previous one, labels each row `new`, `updated`, `closed`, or `removed`, and writes a one-line delta. It can be a short email or a tab on the issue page.
**MVP features:**
1. stable row identity (source URL + date);
2. diff against the previous issue;
3. one-line delta per changed row;
4. "no change" state that is honest.
**Integrations:** `offer_issues` history; no new source.
**Tech fit:** 95% built; a diff function and a renderer.
**Pricing:** free; improves retention.
**How to validate in 2 weeks:** run it against the two existing drafts; show 5 readers; ask whether the delta alone is enough.
**MVP build estimate:** 2-3 days.
**The thing that makes it hard:** stable identity. A URL change looks like a new row unless the adapter supplies a stable key.
**Why it has not been built:** only one issue exists per channel so far.

### 5.4 Recall & Enforcement Watch

**Type:** structured table, manufacturing, retail, behavioral-health, financial.
**Primary user:** quality/EHS, retail compliance, practice manager, compliance lead.
**Core problem:** recalls and enforcement actions are scattered across registers and buried in news.
**What it does:** pulls recent recalls/actions from CPSC, FDA, FTC, SEC; AI extracts product, hazard, remedy, status, and date; every row links to the notice.
**MVP features:**
1. 8-12 rows per month;
2. product/hazard/remedy/status;
3. jurisdiction and source URL;
4. no compliance certification.
**Integrations:** CPSC, FDA, FTC, SEC; three are public APIs or feeds.
**Tech fit:** the reference pipeline; one adapter per source.
**Pricing:** free; strong inquiry fit.
**How to validate in 2 weeks:** one source, one issue, 10 readers; ask whether they would act on a row.
**MVP build estimate:** 1-2 weeks per source.
**The thing that makes it hard:** source schemas and the liability of a missed recall.
**Why it has not been built:** the reference pipeline has only two adapters.

### 5.5 Personalized Watchlist

**Type:** filtered view + email link.
**Primary user:** IT generalist (vendor stack), digital-tech lead (topics), legal reader (jurisdictions).
**Core problem:** the full list is noise; the reader wants only their stack or their topic.
**What it does:** reader selects vendors, topics, or jurisdictions; the page filters immediately; a shareable link stores the selection without an account. Email can send only matching rows later.
**MVP features:**
1. 10-20 checkboxes or a multi-select;
2. localStorage + URL param;
3. no account, no PII;
4. count of hidden rows.
**Integrations:** existing issue rows.
**Tech fit:** 95% built; a client filter and a URL state.
**Pricing:** free; the saved link is a subtle retention hook.
**How to validate in 2 weeks:** add it to the cybersecurity draft; measure filter use and return visits.
**MVP build estimate:** 3-5 days.
**The thing that makes it hard:** identity across devices; not needed for v1.
**Why it has not been built:** the page exists; the jurisdiction filter is not built.

### 5.6 Document & Deadline Checklist

**Type:** interactive checklist / PDF.
**Primary user:** legal ops (corporate filing), education (enrollment), logistics (customs), energy (interconnection).
**Core problem:** the reader knows the date but not what to prepare.
**What it does:** the reader picks a scenario; AI assembles a checklist of documents and steps from cited rules; every item links to the source; the page says it is not advice.
**MVP features:**
1. 5-10 items;
2. source URL per item;
3. disclaimer;
4. no document upload, no PII.
**Integrations:** the reference rows; a scenario mapping.
**Tech fit:** build on the issue schema; a new renderer.
**Pricing:** free; high inquiry intent.
**How to validate in 2 weeks:** one scenario, 10 readers, ask whether the checklist is complete enough to use.
**MVP build estimate:** 1-2 weeks.
**The thing that makes it hard:** liability. It must list what the source requires, not what the reader should do.
**Why it has not been built:** it needs reviewed reference rows first.

### 5.7 Ask-the-Desk Answer Pack

**Type:** one-question form + sourced answer.
**Primary user:** a reader with a specific question but no appetite for a call.
**Core problem:** the reader wants an answer, not a consultation.
**What it does:** the reader submits one question; AI drafts an answer from the archive and primary sources; a human or partner reviews before send; the answer becomes a lead.
**MVP features:**
1. one question, email, consent;
2. answer with 2-3 sources;
3. human review before send;
4. no advice, no PII.
**Integrations:** `AskQuestion` exists; needs an answer workflow.
**Tech fit:** 70% built; the form and lead capture exist, the answer workflow does not.
**Pricing:** free; highest-touch lead.
**How to validate in 2 weeks:** answer 5 real questions manually; measure whether they convert to a consultation.
**MVP build estimate:** 1-2 weeks plus human time.
**The thing that makes it hard:** review time, not generation.
**Why it has not been built:** no reviewer and no delivery.

### 5.8 Exportable Dataset

**Type:** CSV/JSON download, later API.
**Primary user:** analyst, partner firm, developer.
**Core problem:** the reader wants the rows, not a page.
**What it does:** exports the calendar, KEV, or recall rows with source URLs and issue date; a free CSV, a partner API later.
**MVP features:**
1. CSV/JSON of one issue;
2. source URL and scope columns;
3. attribution and licence note;
4. no proprietary data.
**Integrations:** `offer_issues`; a new endpoint.
**Tech fit:** 90% built; one serializer and one route.
**Pricing:** free CSV; partner API later.
**How to validate in 2 weeks:** offer the CSV on one issue; count downloads and replies.
**MVP build estimate:** 3-5 days.
**The thing that makes it hard:** licensing. Do not export paywalled data.
**Why it has not been built:** the public page does not exist.

---

## 6. Prioritization

```
HIGH VALUE / LOW EFFORT  -> Build first
  7-Day Desk Brief
  Change Log
  Personalized Watchlist
  Exportable Dataset (after the public page is populated)

HIGH VALUE / HIGH EFFORT -> Plan for phase 2
  Jurisdiction-Tagged Calendar (EU adapter)
  Recall & Enforcement Watch
  Document & Deadline Checklist

LOW VALUE / LOW EFFORT   -> Quick wins / lead-gen only
  Audio brief (TTS) after retention is proven
  Source digest

LOW VALUE / HIGH EFFORT  -> Do not build
  One calendar per country
  AI-search-only calendar
  Quarterly benchmark maps without licensed data
  A paid tier before traffic and partners exist
```

### 6.1 Sequence

1. **7-Day Desk Brief** on one channel, 2 weeks, manual send.
2. **Public issue page + jurisdiction filter** for the existing legal draft.
3. **Change Log** on the two live reference channels.
4. **Personalized Watchlist** on cybersecurity.
5. **EU adapter** for the legal calendar, if the filter shows demand.
6. **Recall/Enforcement Watch** for manufacturing or retail.
7. **Checklist** and **Answer Pack** only after a reviewer is named.
8. **Export** after the public page is stable.

---

## 7. Per-channel product map

| Channel | Best first product | Second | AI level | Source today | Main risk |
|---------|--------------------|--------|----------|--------------|-----------|
| legal | 7-day docket brief | jurisdiction calendar | A/B | Federal Register | wrong deadline |
| financial | 7-day rules brief | change log | A/B | SEC/Fed | advice drift |
| behavioral-health | 7-day practice brief | payer/safety watch | A/B | CMS/FDA | clinical claim |
| education | deadline brief | checklist | A/B | state boards | admissions promise |
| logistics | port/customs digest | change log | B | CBP/ports | rate implication |
| cybersecurity | KEV digest | personalized watchlist | A/B | CISA/NVD | false safety |
| stem-cell | trial/regulatory digest | change log | B | ClinicalTrials.gov | efficacy claim |
| manufacturing | recall watch | change log | B | CPSC/FDA | compliance claim |
| energy | queue/docket digest | change log | B | RTO/PUC | approval prediction |
| retail | policy/recall calendar | change log | B | FTC/CPSC | demand claim |
| digital-technology | 7-day stack brief | personalized watchlist | A | official changelogs | benchmark claim |

The 7-day brief is the only product that fits every channel without a new adapter. That is why it is the baseline, not the differentiator.

---

## 8. MVP for the top concept: 7-Day Desk Brief

**Problem statement:** the reader has seven days of channel coverage and no five-minute way to know what changed for them.

**Core user story:** as a compliance lead, I want five sourced items from the last seven days with one line on why each matters, so that I can decide what to act on before the next issue.

**MVP feature set:**
- 5 items from the last 7 days, one per item;
- three fields: what changed, date to watch, what to ask;
- every item links to the source;
- a public archive and one inquiry CTA;
- EN and ES;
- a `drafted_by` flag and a reviewer field, empty in v1.

**Explicitly out of scope:**
- email delivery, double opt-in, unsubscribe;
- personalization beyond channel;
- audio, PDF, or slides;
- more than 5 items;
- a paid tier.

**Definition of done:**
- draft generated from the existing feeds for one channel;
- every item has a live source URL;
- a reader can open the archive and read it;
- one CTA routes to the existing lead form;
- no claim that an email was sent.

**First 3 users:**
1. one reader from the legal channel's existing audience;
2. one compliance lead in the operator's network;
3. one partner's client, with permission.

**Success metric at 30 days:**
- 10 readers asked, 3 say they would open it weekly, and at least 2 reply with a specific item they used.

---

## 9. What not to build

- **One calendar per country.** It multiplies adapters and hides coverage gaps.
- **AI-search-only calendars.** A search result is not a source.
- **A "global" product.** If the adapters cover the US and EU, say so.
- **An advice product.** The partner gives advice; the desk gives sourced facts.
- **A paid tier.** No traffic baseline, no payment surface, no partner contract.
- **Audio before retention.** TTS is easy; a voice and a reason to listen are not.
- **A second newsletter.** The 7-day brief and the reference issue must not compete on the same page.

---

## 10. Decisions needed

1. Build the 7-Day Desk Brief first, or add the jurisdiction filter to the public page first?
2. Is the jurisdiction filter a public product or a reader preference only?
3. Is the first new adapter EU, or the next US source (recall, energy, education)?
4. Does the partner want the export dataset, or only inquiries?
5. Is a human reviewer available for the 7-day brief, or does it ship as an unreviewed AI draft behind a clear label?

## Open questions

1. What is the traffic baseline? Without it, "1% of offer views" is not measurable.
2. Does the reader want a country filter, a state filter, or both?
3. Is the IP default allowed under the privacy posture (U9)?
4. Is the 7-day brief a separate email, or the first section of the reference issue?

---

## 11. Honesty ledger

| Claim | Grade | Evidence |
|-------|-------|----------|
| The 7-day brief is the cheapest product to generate | A | the feeds and summaries already exist; no new source |
| A jurisdiction filter is cheaper than one calendar per country | A | one schema, one issue, one renderer; adapters stay separate |
| IP geolocation is unreliable for jurisdiction | B | VPN and corporate egress are common; no first-party data yet |
| AI search is not a source | A | the system requires a source URL per row; a search result is not stable |
| A reference issue beats a generic newsletter | C | directional; not yet tested |
| Review is the recurring cost | B | KEV plan estimates 30-60 min per issue |
| The other products fit the existing stack | A | same issue table, worker, AI client, and Next app |

---

## 12. Next action

Build the 7-Day Desk Brief for one channel and put it in front of ten readers before adding another adapter. If the brief does not earn a weekly open, a calendar filter will not save it.
