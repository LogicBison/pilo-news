#!/usr/bin/env bash
# Generate or check docs/channel-inventory.md from the running API.
#
# Usage:
#   ./bin/channels.sh --write    # regenerate the inventory
#   ./bin/channels.sh --check    # fail when the file is stale
#   ./bin/channels.sh --print    # print the generated block
#
# Reads the dev env file by default; set ENV_FILE=.env.prd or override
# API_URL / APP_BASE_URL / SN_DEFAULT_INDUSTRY for another environment.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.dev}"
read_env() {
	[ -f "$ENV_FILE" ] || return 0
	grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2- || true
}

API_PORT="${API_PORT:-$(read_env API_PORT)}"
APP_BASE_URL="${APP_BASE_URL:-$(read_env APP_BASE_URL)}"
SN_DEFAULT_INDUSTRY="${SN_DEFAULT_INDUSTRY:-$(read_env SN_DEFAULT_INDUSTRY)}"

API_URL="${API_URL:-http://127.0.0.1:${API_PORT:-46105}}"
APP_BASE_URL="${APP_BASE_URL:-http://localhost:43991}"
SN_DEFAULT_INDUSTRY="${SN_DEFAULT_INDUSTRY:-stem-cell}"

export API_URL APP_BASE_URL SN_DEFAULT_INDUSTRY API_PORT
exec node apps/web/scripts/channel-inventory.mjs "${1:---write}"
