#!/usr/bin/env bash
# Generate or check .work.biz/strategy/offer-inventory.md from the running API.
#
# Usage:
#   .work.biz/scripts/offers.sh --write
#   .work.biz/scripts/offers.sh --check
#   .work.biz/scripts/offers.sh --print
#
# Reads the dev env file by default; override API_URL for another environment.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.dev}"
read_env() {
	[ -f "$ENV_FILE" ] || return 0
	grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2- || true
}

API_PORT="${API_PORT:-$(read_env API_PORT)}"
API_URL="${API_URL:-http://127.0.0.1:${API_PORT:-46105}}"
export API_URL

exec node .work.biz/scripts/offer-inventory.mjs "${1:---write}"
