# Digital Technology channel — MVP scope

**What it is:** scoped MVP for an eleventh channel (`digital-technology`): computers, chips, datacenters, and AI — what changed in the stack and the rules, and whether it touches the reader's build.
**Status:** Approved for build (2026-11-06) — operator expects the channel (D-014). Feeds probed, none graded yet; no profile, skin, or source exists.
**Needs:** D-011 (name), D-012 (asset), D-013 (skin) confirmed during the build; the §11 window is now a keep/kill check, not a gate.

---

## Verdict

the build is cheap and the feeds are alive. the demand is not proven, and the neighbour is the problem.

- **cheap:** a channel is data — profile → `apply-profile` → `bin/channels.sh --write`. no routes, no components. 1.5–2 days including skin and art.
- **alive:** ten candidate feeds answered 200 with 10–50 items each on 2026-11-06 (8 EN, 2 ES). liveness is not quality; `verify-sources` still has to grade them.
- **unproven:** nothing says a digital-tech reader wants another AI news site. the cybersecurity channel already carries breach/AI-policy stories.
- **the neighbour:** two channels competing for the same story split SEO and dilute both. overlap is measurable before building (shared `canonical_url`), and a topic hub is the cheaper first move.

so: **build it, and let the 21-day topic window decide whether it keeps its own surface** (D-014 supersedes the test-first sequence in D-010).

## 1. Context loaded

| Field | Value |
|-------|-------|
| **Build target** | eleventh channel on the existing deployment (channel-as-data) |
| **User** | CTO / VP Engineering or AI product lead at a 20–200 person software company; second reader: infrastructure procurement |
| **Buyer** | none directly. the inquiry is an AI-governance readiness review, routed to a partner (U18 still open) |
| **Stack** | profile JSON → `apply-profile` (`docs/deployment-profile.md`); skins with a layout fallback (`apps/web/src/lib/skins.ts:269`); topics + keyword scoring; feed policy `verify-sources` |
| **Build capacity** | solo, 6–12 week envelope; this channel is 1.5–2 days (estimated, §9) |
| **Price point** | free channel; the money is the inquiry and the asset waitlist |
| **Gaps** | traffic baseline (U10), partner (U18), asset reviewer (D-005), quality grades for the candidate feeds |

## 2. The concept

**Problem:** the reader cannot tell which AI/chip/datacenter change affects their build or their compliance obligations, because the coverage is launch marketing and funding rounds.

**Core user story:** as an engineering lead running AI workloads, i want the week's infrastructure and rule changes that touch my stack, so that i plan capacity and compliance before they are forced on me.

**One-line pitch:** "what changed in chips, datacenters, and AI rules — and whether it touches your build."

**It is not:** a startup-funding feed, a product-launch feed, a security-incident feed (that is the cybersecurity channel), or a benchmark leaderboard.

**Lenses:** data→insight (regulator and vendor disclosures → a decision), platform extension (channel-as-data), workflow automation (the capacity/compliance review).

## 3. Evidence base

Measured on 2026-11-06 unless stated.

| Fact | Value | Grade |
|------|-------|-------|
| candidate feeds answering 200 with items | 10 / 10 — Ars Technica, The Register, HPCwire, DatacenterDynamics, EE Times, Semiconductor Engineering, IEEE Spectrum, Google AI Blog (EN); Xataka, Hipertextual (ES) | measured (liveness only) |
| items per feed on the probe | 10–50 | measured |
| editorial vocabulary already defined | `.work/docs/integration/industries-v1.2.0/data.json:707` — `digital_technology`: terminology, 7 custom fields (GPU hours, model id, chip lot, datacenter region, AI risk class, availability SLA), 5 workflow states | measured |
| channel creation path | `docs/adding-an-industry.md:1`, `docs/deployment-profile.md` — profile import, no code | confirmed (repo docs) |
| channel without a skin | ships, but falls back to Chambers (`apps/web/src/lib/skins.ts:269`) — breaks the P0 "professional per industry" promise | confirmed (code) |
| topic hubs already ship | `/{industry}/topic/{slug}`; backlog item R8 in `20261105-offer-and-leadgen-brief.md` §3 | confirmed (routes) |
| inventory + sitemap | `apps/web/scripts/channel-inventory.mjs`, `bin/channels.sh --write`; `./bin/start.sh test` fails on a stale list | confirmed |
| ES parity is the recurring gap | retail ships 1 ES story vs 10 EN (HANDOFF residual risks) | measured (earlier) |
| story overlap with cybersecurity | not measured — the decisive number for this decision | unknown |

## 4. What ships in the MVP

1. **profile** `apps/api/config/deployments/digital-technology.json`: slug `digital-technology`, EN/ES names + taglines, theme (light, monospace headings, square corners), disclaimers ("news, not engineering or legal advice"), `cta.kind = consultation`, `cta.asset = ai-rules-calendar`, retention 30 d.
2. **five topics** with EN/ES keywords: `ai-models`, `chips-supply`, `datacenter-power`, `ai-rules`, `platform-pricing`.
3. **six sources minimum** from the probed list (≥ 2 ES), trust 0.80–0.90, every one graded by `verify-sources`.
4. **skin** `datacenter`: motif + one licensed photo with credit in `credits.json`, list rhythm `grid3`, bar `center`.
5. **14 published items** before the channel is enabled — an empty or near-empty channel is worse than none.
6. **asset card as a waitlist only** (`cta.asset` + `waitlist: true`, copy in `messages/*.json`), no send date promised until delivery exists (D-002).

## 5. Out of scope

- any new route, component, or API surface — the channel is data
- paid tier, daily cadence, model/price trackers (proprietary or unverifiable)
- Asia sources or translation beyond EN/ES
- partner routing automation, partner console
- the asset itself (a rules calendar is a separate scope, gated by D-005 reviewer)
- replacing or merging the cybersecurity channel

## 6. Definition of done

- `python -m news_api.cli verify-sources --industry digital-technology` exits 0 with every source grade A or B and zero coverage warnings
- `apply-profile` applied twice — second run reports 0 created / 0 updated
- channel serves `/v1/news/bundle` and `/v1/industries` in EN and ES; sitemap lists both locales; `bin/channels.sh --check` green
- Playwright public + layout + axe pass for the new channel (11 channels in the loops)
- `pnpm check` contrast 11/11; `./bin/start.sh --env dev test` green

## 7. First 3 users

| # | Who | Reached how | Status |
|---|-----|-------------|--------|
| 1 | the operator's own software/AI contacts | direct | Unknown — none named |
| 2 | cybersecurity-channel readers who click a digital-tech story | in-product link | traffic unknown (U10) |
| 3 | one AI-governance consultant as the inquiry partner | direct | Unknown — none named |

## 8. Success metric at 30 days

**primary:** the channel holds **≥ 3% of site sessions** over a rolling 14 days, measured from the funnel read-out per channel.

**guardrail:** ≥ 1 attributed readiness-review inquiry within 60 days of launch. sessions without inquiries make it a newsletter, not a lead channel.

## 9. Build shape and effort

| Piece | Where | Estimate |
|-------|-------|----------|
| profile (theme, locales, disclaimers, CTA, topics, 6 sources) | `apps/api/config/deployments/digital-technology.json` | 0.5 d |
| skin + motif + photo + credit | `apps/web/src/lib/skins.ts`, `apps/web/public/skins/`, `photos/credits.json` | 0.5–1 d |
| source verification + seeding | `verify-sources`, `apply-profile` | 0.25 d |
| inventory, sitemap, test coverage (11 channels) | `bin/channels.sh --write`, `e2e/layout.spec.ts:3` array, `e2e/public.spec.ts` | 0.25 d |
| **total** | | **1.5–2 d (estimated)** |

**Running cost:** feeds poll every 720 min inside the existing worker; ~20–40 new articles/day at these publication rates, within the `AI_MONTHLY_BUDGET_USD=20` cap only if per-run caps hold — measure the first week (`estimated`, unverified).

## 10. Variants

| | low effort | high effort |
|---|---|---|
| **high value** | **build first:** three topic hubs on cybersecurity, 21 days of data (§11) | phase 2: full channel with its own skin and art |
| **low value** | quick win: one SEO landing page "AI rules calendar" | don't build: a second skin family, per-channel console |

## 11. Evidence window (21 days, running now)

The operator expects the channel (D-014), so the window no longer gates the build — it decides whether the channel keeps its own surface.

1. three topics added to the cybersecurity profile and seeded by migration 012 (M10, done 2026-11-06).
2. the window runs **2026-11-06 → 2026-11-27**; stories route into `/cybersecurity/topic/{ai-infrastructure,chips-supply,ai-rules}` as they match.
3. read `/v1/admin/funnel`: CTA impressions and clicks with `placement="topic"`, plus `brief-topic` starts.
4. **decision rule at 2026-11-27:** keep the channel if the topic pages hold **≥ 1% of site sessions** (or ≥ 1% of CTA impressions when sessions are unavailable) and the channel itself has produced **≥ 1 inquiry** or **≥ 5 list signups**. otherwise demote: `enabled: false` on the channel, topics stay.

caveat: session share needs U10. without it the denominator is CTA impressions and the result is marked `estimated`.

## 12. Kill criterion

- after launch, **< 1% of site sessions for six weeks and no inquiries** → disable the channel (`enabled: false`, config-only rollback) and keep the topics under cybersecurity.
- **shared stories > 40%** with cybersecurity, measured by `canonical_url` overlap over two weeks → merge instead of running both.
- `verify-sources` fails twice, or enabled sources fall below the policy floor of four → do not launch.
- no named reader for the asset (§7) → the channel ships without an asset card, not with a false promise.

## 13. What makes it hard

- **the neighbour.** cybersecurity already covers AI incidents and AI policy. two channels on one story split the SEO and the reader's attention; the overlap number is unmeasured, and that is the single fact that decides this.
- **general tech feeds dilute the niche.** Ars and The Register publish phones and consumer gear. topic weights help, but a general feed makes a general channel.
- **no proprietary data.** the asset can only be a calendar of public rules — the same shape as the legal channel, and the same liability if a row is wrong.
- **ES coverage is thin.** the two Spanish feeds are general technology, not semiconductors; parity will be structural, not fixable with more sources.
- **AI news is saturated.** differentiation has to be "what it changes for your build", which is an editorial stance, not a feed.
- **a channel without its own skin** breaks the one promise this product makes — every industry looks professionally suited.

## 14. Open technical questions

| # | Question | Grade | Note |
|---|----------|-------|------|
| T1 | do the ten feeds pass the quality policy? | `Unknown` | liveness only; `verify-sources` grades reachability, freshness and duplication |
| T2 | is a hyphenated slug supported? | `Confirmed` | `behavioral-health` and `stem-cell` already ship |
| T3 | what happens without a skin entry? | `Confirmed` | falls back to Chambers (`skins.ts:269`) — functional, off-brand |
| T4 | are the ES topic keywords adequate? | `Unknown` | the two Spanish feeds are general; keyword coverage will be shallow |
| T5 | does anything else need updating for an 11th channel? | `Confirmed` | inventory script and sitemap iterate the channel list; the e2e channel arrays are hardcoded (`e2e/layout.spec.ts:3`) and must be extended by hand |
| T6 | how much does this channel overlap cybersecurity? | `Unknown` | measurable from `canonical_url` after three weeks of topics |

## 15. Decisions needed

- **D-010 — sequence:** test with three topic hubs first (recommended) or build the channel now. affects this doc §11 and the next iteration.
- **D-011 — name and slug:** `digital-technology` / "Digital Technology", per the completed industries file; Spanish "Tecnología Digital".
- **D-012 — asset:** the `ai-rules-calendar` waitlist, or no asset card until the calendar is scoped.
- **D-013 — skin:** a new `datacenter` skin, or ship on the `grid` skin until the channel proves itself (saves 0.5–1 d, costs the brand promise).

## Open questions

1. who is the partner for an AI-governance readiness review — a consultancy, a law firm, or a platform vendor? answers U18 for this channel.
2. does the operator have three named readers who would subscribe today? if not, the topic test is the only honest evidence.
3. is a shared skin acceptable for the first month, given the ten other channels are distinct?
4. does the channel inherit the cybersecurity disclaimer set, or does it need its own (no engineering advice, no compliance certification)?

## Next action

approve D-010; if approved, apply the three topics to the cybersecurity profile and start the 21-day read-out before writing any profile, skin, or source.
