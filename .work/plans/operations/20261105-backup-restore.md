# Backup and restore - volume tar.gz

**Status:** implemented and drilled (2026-11-05) · **Needs:** off-site encrypted storage for prd.
**Decision:** snapshots are `.tar.gz` archives of the Docker volumes. No `pg_dump`.

## Why volumes

Postgres, Redis, and Caddy data live in named volumes. A volume archive captures
the complete state (including Postgres WAL and Redis AOF) and restores the stack
without a database dump tool. The tradeoff is size and a short write pause while
the archive is made.

## Backup

```bash
./bin/start.sh --env dev backup
# -> backups/news-dev-volumes-YYYYMMDD-HHMMSS.tar.gz
```

What happens:

1. `api`, `worker`, `postgres`, `redis` are stopped so Postgres is not writing.
2. `alpine:3.20` mounts `pgdata`, `redisdata` (and Caddy volumes when present)
   read-only and writes one tar.gz under `backups/`.
3. Services restart; the script waits for `/v1/health`.

Encrypt before leaving the host:

```bash
age -r "$AGE_PUBLIC_KEY" -o backups/$(date -u +%Y%m%d).tar.gz.age backups/news-dev-volumes-*.tar.gz
```

The archive contains PII (contact messages, leads). Treat it as Confidential,
store off-site with a 30-day lifecycle, and never commit `backups/`.

## Restore

```bash
./bin/start.sh --env dev restore
```

The menu lists archives, asks for a number, then requires the literal
`restore-dev` confirmation. It stops api/worker/postgres/redis, clears the
mounted volume directories, extracts the archive, and restarts the stack.

## Drill evidence

| Date | Archive | Result |
|------|---------|--------|
| 2026-11-05 | `news-dev-volumes-20261105-170737.tar.gz` (14 MB) | restored; `/v1/health` ok; 19 AI summaries still present after restore |

RPO is the backup interval (daily in prd); RTO is the time to extract the
archive plus API health (single-digit minutes for this dataset). Re-run the
drill after changing the volume set or Postgres major version.

## Notes

- `bin/start.sh backup` uses `COMPOSE_PROJECT_NAME` to find `${project}_pgdata`,
  `${project}_redisdata`, and Caddy volumes.
- Restoring an archive that lacks a volume leaves that volume's mount empty; the
  script only mounts the volumes found in the archive.
- Redis is disposable by design; restoring it is still included for a faithful
  snapshot.
