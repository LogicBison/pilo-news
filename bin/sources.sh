#!/usr/bin/env bash
# Discover, inspect and record source acquisitions.
#
# Usage:
#   ./bin/sources.sh discover --file candidates.txt --industry legal
#   ./bin/sources.sh discover --url https://example.com/feed.xml
#   ./bin/sources.sh report
#   ./bin/sources.sh health [--industry legal]
#   ./bin/sources.sh outreach --source <id> --note "asked for allowlisting"
#
# `discover` is read-only: it grades candidates and prints a profile snippet.
# Adding a source is still an explicit profile edit plus `apply-profile`.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.dev}"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f "docker-compose.${ENV_FILE#.env.}.yml")

exec "${COMPOSE[@]}" exec -T api python -m news_api.cli sources "$@"
