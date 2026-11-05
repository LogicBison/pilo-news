# HANDOFF - session boundary

## Session status

**Open:** - · **Updated:** 2026-11-05 · **Closed:** 2026-11-05

**Repository state:** v1 implemented plus the post-v1 operator scope. Master plan v1.1
(Approved) executed end to end: schema/migrations (001-007), **seven** live channels
(five reference + `cybersecurity` + `stem-cell`, the last two existing only as
deployment profiles), 32 verified feeds, ingestion + DeepSeek summaries, public API, EN/ES sites,
editorial console, leads, observability, CI, docs, volume backups.
Provisioning is a ports/adapters module (`apply-profile`), source quality is an
enforced policy (`verify-sources`), the default industry switches at runtime
(`SN_DEFAULT_INDUSTRY` + `./bin/start.sh industry`), and the UI has a
material-inspired surface system. **Foundation-complete: yes. Plan-master-ready: yes.
Implementation-ready: yes. v1 implemented: yes. Custom-industry-ready: yes.**

**Recommended pick-up file:** `.work/plans/NEXT.md`
**Next session focus:** per-channel UI skin refresh. run `@ui-design-foundation greenfield`,
then per-channel specs, using the 14 lead-generation references recorded in
`.work/plans/20261105-ui-skin-refresh.md`. `.work.ui` is still greenfield.
Dev currently defaults to `stem-cell`; switch with `./bin/start.sh --env dev industry <slug>`
(quick reference: `docs/guides/switching-channels.md`).

**Lost or new?** Read `.cursorrules`, then `.work/plans/20261105-industry-template-verification.md`.

---

## Fresh start - what the next session should do first

1. Run **`@session-control start`**.
2. Read `.cursorrules` and this file.
3. Read `.work/plans/NEXT.md`.
4. Read `.work/plans/20261105-template-deployment-plan.md` (next deliverable) and
   `.work/plans/20261105-industry-template-verification.md` (current capability).
5. Clone a vertical by copying `apps/api/config/deployments/<slug>.json` and
   running `apply-profile` (see `docs/deployment-profile.md`).
6. Re-run `python -m news_api.cli verify-sources --industry all` after any
   portfolio change; it must exit 0.
7. Verify pending: k6 (`tests/perf/k6-smoke.js`), prd deploy/rollback, remote CI,
   and the production image smoke checks.
8. For launch: answer U9/U8/U10/U1, then run `.work/plans/operations/20261105-launch.md`.

### Conditional reads

| If the task touches… | Read first |
|----------------------|------------|
| Any code or new feature | `.work/standards/20261105-CONVENTIONS.md`, `20261105-DIRECTORY_MAP.md` |
| Public API | `.work/standards/20261105-api-style-guide.md`, `docs/api/README.md` |
| Adding an industry | `docs/adding-an-industry.md` |
| Ingestion/AI | `.work/features/ingestion-pipeline/20261105-SPEC.md`, `apps/api/config/` |
| Web/UI | `.work/features/industry-sites/20261105-SPEC.md`, `apps/web/src/` |
| Backups/restore | `.work/plans/operations/20261105-backup-restore.md` |
| Security | `.work/standards/20261105-threat-model.md`, `20261105-data-classification.md` |
| Any prose/chat | `.work/voice/README.md` |

---

## Gate snapshot

| Phase | Status | Evidence |
|-------|--------|----------|
| P0-P6 foundation | done | docs 01-04, ADRs 001-013, SPECs, standards |
| M1 scaffold | done | compose dev/prd, Dockerfiles, `bin/start.sh` |
| M2 schema/channels | done | migrations 001-003 run twice; 5 channels |
| M3 ingestion | done | fixture tests + live feeds + worker scheduler + refresh runs |
| M4 AI summaries | done | DeepSeek `deepseek-flash`; 19 legal summaries stored; fail-open tested |
| M5 public API | done | contract tests, ETag/304, bundle/fallback, rate limits, leads |
| M6 sites | done | lint/type/build, Playwright public + axe, EN/ES routes |
| M7 console | done | auth/CSRF contract tests, sources/pins/keys/audit/leads |
| M8 hardening | done (prd deploy pending) | metrics/alerts/dashboards, runbooks, security review, backup drill |
| Any-industry template | done | create-channel endpoint + web + docs + tests |
| Isolation | done | random host ports; `*-net`/`*-data`; DB/Redis internal |
| Backups | done | `.tar.gz` volume archive + restore drill 2026-11-05 |
| CI | written, not run on GitHub | `.github/workflows/ci.yml` |
| k6 / Lighthouse CI | scripts written, not run in prd | `tests/perf/k6-smoke.js` |
| prd deploy/rollback | images build + smoke; no host DNS deploy yet | owner U7/O7 |
| deployment profile | done | `apply-profile` CLI, `config/deployments/*.json` (6), `docs/deployment-profile.md`; ports/adapters seam |
| source quality | done | `verify-sources` CLI, 26/26 feeds grade A, 0 coverage warnings, ADR 014, `docs/source-quality.md` |
| custom industry proof | done | `cybersecurity` and `stem-cell` created from profiles only, serving content |
| stem-cell channel | done | `config/deployments/stem-cell.json`: 6 feeds (4 EN + 2 ES), 5 topics, 53 articles after first refresh |
| instant industry switch | done | `./bin/start.sh industry financial` -> `/` redirects to `/financial`, no rebuild |

**Integrity:** no known waivers. Dev stack running (`system-news-dev`).

---

## Verification evidence (this session)

| Check | Result |
|-------|--------|
| `ruff check . && ruff format --check .` (api) | pass |
| `mypy src` (api) | pass, 86 files |
| `pytest -q` (api) | 77 passed (unit + integration + contract, includes template tests) |
| `pnpm lint && pnpm typecheck` (web) | pass |
| `pnpm check` (catalogs + themes) | 220 keys; 5/5 channels pass contrast |
| `pnpm build` (web) | pass |
| Playwright public + axe (production build) | 9/9 pass (public, a11y, admin) |
| Admin e2e | login, console, refresh trigger pass |
| AI summaries | 92 articles across channels summarized; failures fail-open |
| Backup + restore | archive created (14 MB), restore passed, `/v1/health` ok, 19 summaries intact |
| OpenAPI snapshot | 41 paths, committed |
| `docker compose config` | valid dev/prd (ports + networks resolved) |
| prd images | API wheel image built + migrations/config verified; web standalone image built + `/legal` 200 |
| Deployment profile | `apply-profile --dry-run` + real apply on dev: 0 created, 0 updated, 20 skipped (example matches seeds) |
| Source verification | `verify-sources --industry all`: 7 industries, 32 sources, 32 pass, 0 fail, 0 coverage warnings |
| Stem-cell verification | `verify-sources --industry stem-cell`: 6/6 grade A; `apply-profile --dry-run`: 0 created, 0 updated, 15 skipped |
| Channel coverage | enabled sources per channel: 4, 4, 4, 5, 4, 5, 6 (policy floor 4) |
| Custom channel | `cybersecurity` apply: 13 created; `/v1/news/bundle` EN/ES + web page + sitemap render |
| Industry switch | legal -> financial -> legal via `./bin/start.sh industry`; `/` 307 to the new channel each time |
| API tests | 107 passed (unit + integration + contract, includes quality, ports, profile, ingest) |
| Web checks | `pnpm lint`, `pnpm typecheck`, `pnpm check` (221 keys, 6 channels contrast) |
| E2E + axe (production build) | 8 passed, 1 skipped (admin sign-in needs `E2E_ADMIN_PASSWORD`); 0 critical/serious a11y violations |
| Retention coherence | channel window (30d) now wins over the global scoring default; ES lists: education 1->5, cybersecurity 0->3 |
| Content check (API) | all 6 channels serve `news` + `bundle` (EN/ES); web pages 200 for all six |
| Logs/admin check | 11 browser routes 200; `/` 307 to `SN_DEFAULT_INDUSTRY` |
| Browser smoke 2026-11-05 | `/` 302→`/legal`; `/legal`, `/es/legal`, `/financial`, `/behavioral-health`, article, `/legal/{about,privacy,terms,contact,search}`, `/en/admin` all 200; API `/v1/health` ok |

---

## Open owner actions

| # | Action | Blocks | Owner | Where |
|---|--------|--------|-------|-------|
| O1 | ~~Ratify ADRs 001-013~~ approved | - | owner | `.work/decisions/` |
| O2 | ~~VPS provider/budget~~ approved | - | owner | ADR 005 |
| O3 | ~~NFR targets~~ approved | - | owner | doc 04 §5 |
| O4 | ~~Stack files~~ approved/created | - | owner | operations proposal |
| O5 | Fill remaining unknowns: U1 brand, U7 roles, U8 email, U9 analytics, U10 traffic, U11 legal review, U12 sponsored | launch | owner | `.work/plans/UNKNOWNS.md` |
| O6 | ~~Master plan~~ approved | - | owner | full plan v1.1 |
| O7 | prd domain/DNS + provider | prd deploy | owner | launch checklist |
| O8 | CDN/off-site backup bucket (optional) | RPO | owner | backup doc |

---

## What this cycle produced

| Date | Session | Artifacts |
|------|---------|-----------|
| 2026-11-05 | implementation | `apps/api` full service: platform, channels, sources, articles, publishing, editorial, worker, CLI; migrations 001-003; config scoring/seeds/prompts |
| 2026-11-05 | implementation | `apps/web` full Next app: themes, EN/ES, SEO, public pages, admin console, lead/contact forms, proxy, middleware |
| 2026-11-05 | verification | API 77 tests, web lint/type/build, Playwright public/axe, OpenAPI snapshot, AI smoke, backup/restore drill |
| 2026-11-05 | template | `POST /v1/admin/industries`, channels admin tab, `docs/adding-an-industry.md`, verification doc |
| 2026-11-05 | ops | runbooks, launch checklist, security review, restore drill, Prometheus alerts, Grafana dashboards, k6 |
| 2026-11-05 | isolation | random host ports, per-project `*-net`/`*-data`, DB/Redis internal-only |
| 2026-11-05 | custom subjects | `cybersecurity` + `stem-cell` channels from profiles only; 32 verified feeds |
| 2026-11-05 | docs | `docs/guides/switching-channels.md` quick reference; UI skin refresh brief |

---

## Explicit unknowns (promoted from UNKNOWNS)

| ID | Summary | Blocks |
|----|---------|--------|
| U1 | Final brand name | domain/branding |
| U2 | URL shape (one domain vs per-industry) | SEO/canonical |
| U4 | AI monthly budget cap | cost control |
| ~~U5~~ | Closed (technical): 26 verified feeds, quality policy applied; terms under U11 | - |
| ~~U6~~ | Closed: pilot = `legal` | - |
| U9 | Analytics/consent posture | cookie banner/privacy |
| U10 | Traffic expectation | sizing |
| U18 | Lead pricing/partner model | CTA routing |

---

## Cross-framework action (@x-director)

Lead generation remains integrated (ADR 013, FR-17): one primary CTA per page,
consent-first lead form, partner routing, DSAR export/erase, funnel events, and
lead dashboards/alerts. UI foundation and biz strategy docs remain in
`.work.ui/` and `.work.biz/`.

---

## Known residual risks

- Single VPS SPOF (R4); volume restore drilled, prd deploy/rollback not drilled.
- Feed licensing/terms (U11) and Spanish coverage (R17) remain owner inputs.
- The UI is a hand-made material pass, not a certified `.work.ui` design system.
- AI summaries are fail-open; some items are intentionally left without a
  summary when validation rejects output.
- CI is written but has not run on GitHub yet.
- prd images build and smoke; a real host/DNS deploy + rollback drill is still an owner action.
- `k6` and Lighthouse budgets are scripts only; no prd measurement yet.
- E2E runs against a production build; run `pnpm build` before `pnpm test`.
- AI validation intentionally rejects some provider output; those items publish
  without a summary.

---

## Next action

Run the UI skin refresh brief (`.work/plans/20261105-ui-skin-refresh.md`), then answer U9/U8/U10/U1 and run `.work/plans/operations/20261105-launch.md`.
