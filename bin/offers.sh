#!/usr/bin/env bash
# Build or inspect dated offer issues from the running API container.
#
# Usage:
#   ./bin/offers.sh build --industry legal [--date YYYY-MM-DD] [--dry-run]
#   ./bin/offers.sh list [--industry legal]
#   ./bin/offers.sh show <issue-id>
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.dev}"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f "docker-compose.${ENV_FILE#.env.}.yml")

exec "${COMPOSE[@]}" exec -T api python -m news_api.cli offer "$@"
