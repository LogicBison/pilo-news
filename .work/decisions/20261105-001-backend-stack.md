# ADR 001 - Backend stack: Python 3.12 + FastAPI

**Status:** Decided · 2026-11-05 · **Decision authority:** prepared under owner instruction "prepare everything"; ratification tracked in `HANDOFF.md` O1.
**Needs:** owner ratification (HANDOFF O1-O3) - review action, not a blocker.

**Decides:** the API language and framework for `/v1` and the ingestion worker.

## Context

- The reference implementation (`/mnt/work/Projects/LogicBison/api`) is FastAPI with a working news aggregation and AI-summary module (`aggregator.py`, `summary.py`) that the brief says to copy.
- The workload is I/O-heavy: feed polling, HTTP caching, JSON parsing, batched AI calls, Postgres queries. It is not CPU-bound.
- Team size is 1-3; the Agent OS skills and existing tests are Python-friendly (`pytest`, `ruff`).
- NFRs: p95 < 250 ms cached, 1,000 req/min per node, 10k feed items/day/channel.

## Decision

Use **Python 3.12 + FastAPI 0.115.6 + Uvicorn 0.34.0 + Pydantic 2.10.5**, with:

- **SQLAlchemy 2.0 async** + **asyncpg** for Postgres.
- **httpx 0.28** for feed and AI-provider calls (one client, explicit timeouts).
- **A separate worker process** (`python -m news_api.worker`) consuming a Redis Stream for refresh/summarize jobs; the API only enqueues and reads.
- **Ruff** (lint + format) and **mypy** (type check); **pytest** + `pytest-asyncio` + `httpx.ASGITransport` for tests.

## Consequences

- **Positive:** direct reuse of the reference aggregation logic; strong typing at the HTTP boundary; async I/O suits the workload; single language for API + worker.
- **Negative:** GIL limits CPU parallelism (irrelevant here); Python packaging needs discipline (pinned `pyproject.toml`, `uv`/pip lock).
- **Neutral:** a Node/TypeScript backend would share types with the frontend, but would discard the reference implementation and increase rewrite risk.

## Alternatives considered

| Option | Why rejected |
|--------|--------------|
| TypeScript + Node (Fastify/Nest) | Discards the working reference code; no type-sharing benefit strong enough |
| Go | Fast and simple to deploy, but no reuse and slower iteration for a small team |
| Django | Heavier than needed; DRF adds surface without benefit |
| Rust | Overkill for I/O-bound CRUD + polling |

## References

- `/mnt/work/Projects/LogicBison/api/requirements.txt`
- `/mnt/work/Projects/LogicBison/api/src/news/aggregator.py`
- `.work/plans/foundation/20261105-04-foundation-architecture.md` §5, §10
- `DOCS_TECH_STACK.md` §1

---

## Next action

None - decision recorded; execution is tracked by the relevant SPEC and the master plan (`@plan-master greenfield`).
