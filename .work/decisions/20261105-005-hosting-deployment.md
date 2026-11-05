# ADR 005 - Hosting and deployment: single VPS + Docker Compose + Caddy

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; provider/budget ratification tracked in `HANDOFF.md` O2.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** where and how the platform runs.

## Context

- NFR-3: 99.9% monthly, RPO 24 h, RTO 4 h. NFR-10: ≤ USD 40/month assumed.
- Sibling projects deploy with Docker Compose (`docker-compose.dev.yml`, `docker-compose.prd.yml`, `bin/start.sh`); there is no existing Kubernetes/cloud footprint.
- Expected traffic at launch is unknown (U10) but assumed < 100k daily sessions.
- The workload is stateless web/API + one stateful Postgres + Redis; it fits one node.

## Decision

- **One VPS** (4 vCPU / 8 GB / 80 GB SSD; provider chosen at O2, e.g. Hetzner/Contabo) running **Docker Compose** with services: `caddy`, `web`, `api`, `worker`, `postgres`, `redis`.
- **Caddy** terminates TLS (automatic Let's Encrypt), sets security headers, reverse-proxies `/api/*` → `api` and everything else → `web`.
- **Docker volumes** for Postgres and Caddy data; Redis persists AOF for queue durability across restarts.
- **Backups:** nightly `pg_dump` piped to a compressed, encrypted file uploaded off-site (provider bucket per O3); 30-day retention; monthly restore drill.
- **Scaling trigger:** sustained CPU > 70% or p95 > target for 7 days → move Postgres to managed, add a second app node behind a load balancer (documented path, not built in v1).
- **Deploy:** image-based (`docker compose -f docker-compose.prd.yml pull && up -d`), health-gated, rollback to previous SHA (ADR 012).

## Consequences

- **Positive:** lowest cost, simple mental model, matches sibling projects, easy local parity.
- **Negative:** SPOF (R4); manual capacity planning; no managed backups unless configured; single-region latency.
- **Neutral:** managed cloud (AWS/GCP/Fly) remains a viable later move; the app is 12-factor and portable.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| AWS ECS/RDS | Strong ops posture, but 5-10x cost at this stage |
| Fly.io / Railway | Fast to start, but persistent Postgres + price/region tradeoffs at scale |
| Bare metal without containers | Loses reproducibility and the compose dev/prod parity |
| Kubernetes | Operational overkill for a 1-3 person team |

## References

- `.work/plans/operations/20261105-docker-compose-proposal.md`
- `DOCS_TECH_STACK.md` §3-4
- RISK_REGISTRY R4

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
