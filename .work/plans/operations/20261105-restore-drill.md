# Restore drill - 2026-11-05

**Status:** pass · **Environment:** dev stack, single host.
**Archive:** `backups/news-dev-volumes-20261105-170737.tar.gz` (14 MB).

1. `./bin/start.sh --env dev backup` stopped api/worker/postgres/redis and
   archived `pgdata` + `redisdata`.
2. Stack restarted; `/v1/health` returned 200 with db/redis/migrations true.
3. `printf '1\nrestore-dev\n' | ./bin/start.sh --env dev restore` cleared the
   mounted volume contents and extracted the archive.
4. `/v1/health` returned 200 after restore.
5. `select count(*) from articles where summary is not null` returned 19,
   matching the pre-restore state.

**Result:** restore path works; RTO on this host is minutes. Re-run before prd
launch and after any volume layout change.
