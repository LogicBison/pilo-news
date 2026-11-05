"""Operator CLI for System News (refresh, status, keys, password hashing)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from news_api.articles.application.queue import enqueue, wait_for_run
from news_api.articles.infrastructure.repo import (
    active_run,
    create_run,
    list_runs_simple,
)
from news_api.channels.infrastructure.repo import list_channels
from news_api.editorial.infrastructure.repo import create_api_key, list_api_keys
from news_api.platform.cache import close_redis, lock_holder
from news_api.platform.db import dispose
from news_api.platform.logging import configure_logging, get_logger
from news_api.platform.security import generate_api_key, hash_password
from news_api.platform.settings import get_settings

log = get_logger(__name__)


async def _refresh(args: argparse.Namespace) -> int:
    if args.industry == "all":
        channels = await list_channels(enabled_only=True)
    else:
        channels = [c for c in await list_channels(enabled_only=True) if c.slug == args.industry]
        if not channels:
            print(f"unknown industry: {args.industry}", file=sys.stderr)
            return 2
    if args.full_reset and args.confirmation != "RESET":
        print("full_reset requires --confirmation RESET", file=sys.stderr)
        return 2

    queued: list[tuple[str, str]] = []
    for channel in channels:
        if await active_run(channel.id) or await lock_holder(f"ingest:lock:{channel.slug}"):
            print(f"{channel.slug}: a refresh is already running", file=sys.stderr)
            continue
        trigger = "reset" if args.full_reset else "manual"
        run_id = await create_run(channel.id, trigger=trigger, requested_by="cli", status="queued")
        await enqueue(
            run_id=run_id,
            industry=channel.slug,
            trigger=trigger,
            full_reset=args.full_reset,
        )
        queued.append((channel.slug, run_id))
        print(f"{channel.slug}: queued {run_id}")
    if not queued:
        return 1
    if args.wait:
        for slug, run_id in queued:
            run = await wait_for_run(run_id, timeout_seconds=args.timeout)
            status = run["status"] if run else "unknown"
            stats = run.get("stats", {}) if run else {}
            print(f"{slug}: {status} new={stats.get('new', 0)} errors={stats.get('errors', 0)}")
    return 0


async def _status(_args: argparse.Namespace) -> int:
    runs = await list_runs_simple(limit=10)
    print(json.dumps(runs, indent=2, default=str))
    return 0


async def _hash(args: argparse.Namespace) -> int:
    print(hash_password(args.password))
    return 0


async def _create_key(args: argparse.Namespace) -> int:
    plaintext, key_hash, prefix = generate_api_key()
    row = await create_api_key(
        label=args.label,
        key_hash=key_hash,
        key_prefix=prefix,
        scopes=["read"],
        rate_limit=args.rate_limit,
    )
    if not row:
        print("failed to create key", file=sys.stderr)
        return 1
    print(json.dumps({"id": str(row["id"]), "label": args.label, "key": plaintext}, indent=2))
    return 0


async def _keys(_args: argparse.Namespace) -> int:
    print(json.dumps(await list_api_keys(), indent=2, default=str))
    return 0


async def _apply_profile(args: argparse.Namespace) -> int:
    from news_api.provisioning.application.apply import (
        ProfileError,
        apply_profile,
        load_profile,
    )

    try:
        profile = load_profile(Path(args.file))
        report = await apply_profile(
            profile, dry_run=args.dry_run, only_industry=args.only_industry
        )
    except ProfileError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0


async def _verify_sources(args: argparse.Namespace) -> int:
    from news_api.sources.application.verify import verify_sources

    industry = None if args.industry in (None, "all") else args.industry
    try:
        report = await verify_sources(industry)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["summary"]["failed"] == 0 else 1


async def _run(args: argparse.Namespace) -> int:
    if args.command == "refresh":
        return await _refresh(args)
    if args.command == "status":
        return await _status(args)
    if args.command == "hash-password":
        return await _hash(args)
    if args.command == "create-key":
        return await _create_key(args)
    if args.command == "keys":
        return await _keys(args)
    if args.command == "apply-profile":
        return await _apply_profile(args)
    if args.command == "verify-sources":
        return await _verify_sources(args)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="news-api", description="System News operator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    refresh = sub.add_parser("refresh", help="enqueue an ingestion run")
    refresh.add_argument("--industry", default="all")
    refresh.add_argument(
        "--force", action="store_true", help="bypass the schedule (manual runs do)"
    )
    refresh.add_argument("--full-reset", action="store_true")
    refresh.add_argument("--confirmation", default=None)
    refresh.add_argument("--wait", action="store_true", default=True)
    refresh.add_argument("--no-wait", dest="wait", action="store_false")
    refresh.add_argument("--timeout", type=float, default=600.0)
    refresh.set_defaults(func=_refresh)

    status = sub.add_parser("status", help="recent refresh runs")
    status.set_defaults(func=_status)

    hashing = sub.add_parser("hash-password", help="print an Argon2id hash")
    hashing.add_argument("--password", required=True)
    hashing.set_defaults(func=_hash)

    create_key = sub.add_parser("create-key", help="create an API key (plaintext shown once)")
    create_key.add_argument("--label", required=True)
    create_key.add_argument("--rate-limit", type=int, default=600)
    create_key.set_defaults(func=_create_key)

    keys = sub.add_parser("keys", help="list API keys")
    keys.set_defaults(func=_keys)

    profile = sub.add_parser(
        "apply-profile", help="reconcile a declarative deployment profile into the database"
    )
    profile.add_argument("--file", required=True, help="path to the deployment profile JSON")
    profile.add_argument(
        "--dry-run", action="store_true", help="report what would change without writing"
    )
    profile.add_argument(
        "--only-industry", default=None, help="apply a single industry slug from the profile"
    )
    profile.set_defaults(func=_apply_profile)

    verify = sub.add_parser(
        "verify-sources", help="fetch enabled sources and grade them against the quality policy"
    )
    verify.add_argument("--industry", default="all")
    verify.set_defaults(func=_verify_sources)
    return parser


async def _async_main(argv: list[str]) -> int:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return await args.func(args)
    finally:
        await close_redis()
        await dispose()


def main() -> None:
    raise SystemExit(asyncio.run(_async_main(sys.argv[1:])))


if __name__ == "__main__":
    main()
