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
from news_api.platform.errors import DomainError
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


async def _offer(args: argparse.Namespace) -> int:
    from datetime import date

    from news_api.offers.application.build import build_offer_issue
    from news_api.offers.infrastructure.repo import (
        get_issue_by_id,
        issue_dto,
        list_issues,
        publish_issue,
        unpublish_issue,
    )

    if args.offer_command == "build":
        parsed = None
        if args.date:
            try:
                parsed = date.fromisoformat(args.date)
            except ValueError:
                print("invalid --date; use YYYY-MM-DD", file=sys.stderr)
                return 2
        try:
            result = await build_offer_issue(
                args.industry,
                offer_slug=args.offer,
                issue_date=parsed,
                dry_run=args.dry_run,
            )
        except DomainError as exc:
            print(exc.detail, file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001 - CLI reports the failure
            print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, default=str))
        return 0

    if args.offer_command == "list":
        industry_id = None
        if args.industry:
            from news_api.channels.infrastructure.repo import get_channel

            channel = await get_channel(args.industry, enabled_only=False)
            if not channel:
                print(f"unknown industry: {args.industry}", file=sys.stderr)
                return 2
            industry_id = channel.id
        rows = await list_issues(industry_id=industry_id, limit=args.limit)
        print(json.dumps([issue_dto(row) for row in rows], indent=2, default=str))
        return 0

    if args.offer_command == "publish":
        if len(args.reviewer.strip()) < 2:
            print("--reviewer must name the person signing the issue", file=sys.stderr)
            return 2
        row = await publish_issue(args.issue_id, args.reviewer.strip())
        if not row:
            print("only a draft with rows can be published", file=sys.stderr)
            return 2
        stored = await get_issue_by_id(args.issue_id)
        print(json.dumps(issue_dto(stored) if stored else None, indent=2, default=str))
        return 0

    if args.offer_command == "unpublish":
        row = await unpublish_issue(args.issue_id)
        if not row:
            print("only a published issue can be unpublished", file=sys.stderr)
            return 2
        stored = await get_issue_by_id(args.issue_id)
        print(json.dumps(issue_dto(stored) if stored else None, indent=2, default=str))
        return 0

    if args.offer_command == "show":
        row = await get_issue_by_id(args.issue_id)
        if not row:
            print("offer issue not found", file=sys.stderr)
            return 2
        payload = issue_dto(row)
        if args.markdown:
            from news_api.offers.application.render import render_issue_markdown

            print(render_issue_markdown(payload))
            return 0
        print(json.dumps(payload, indent=2, default=str))
        return 0

    return 2


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
    if args.command == "offer":
        return await _offer(args)
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

    offer = sub.add_parser("offer", help="build and inspect dated offer issues")
    offer_sub = offer.add_subparsers(dest="offer_command", required=True)
    build = offer_sub.add_parser("build", help="build a draft issue from public sources")
    build.add_argument("--industry", required=True)
    build.add_argument(
        "--offer", default=None, help="offer slug (defaults to the channel definition)"
    )
    build.add_argument(
        "--date", default=None, help="issue date YYYY-MM-DD (defaults to the latest due date)"
    )
    build.add_argument("--dry-run", action="store_true", help="print rows without writing")
    build.set_defaults(func=_offer)
    list_issues_parser = offer_sub.add_parser("list", help="list generated issues")
    list_issues_parser.add_argument("--industry", default=None)
    list_issues_parser.add_argument("--limit", type=int, default=20)
    list_issues_parser.set_defaults(func=_offer)
    show = offer_sub.add_parser("show", help="show one issue")
    show.add_argument("issue_id")
    show.add_argument("--markdown", action="store_true", help="render the issue as markdown")
    show.set_defaults(func=_offer)
    publish = offer_sub.add_parser("publish", help="publish a draft after reviewer sign-off")
    publish.add_argument("issue_id")
    publish.add_argument("--reviewer", required=True, help="named person signing the issue")
    publish.set_defaults(func=_offer)
    unpublish = offer_sub.add_parser("unpublish", help="return a published issue to draft")
    unpublish.add_argument("issue_id")
    unpublish.set_defaults(func=_offer)
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
