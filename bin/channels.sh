#!/usr/bin/env bash
# Generate or check docs/channel-inventory.md.
#
# Usage:
#   ./bin/channels.sh --write    # regenerate the inventory
#   ./bin/channels.sh --check    # fail when the file is stale (also runs in CI)
#   ./bin/channels.sh --print    # print the generated block
#   ./bin/channels.sh --urls     # concrete URLs for this machine (subdomains in dev)
#
# Channels come from the live API when it answers and from the deployment
# profiles otherwise, so --check needs no server. Reads the dev env file by
# default; set ENV_FILE=.env.prd or override API_URL / APP_BASE_URL /
# SN_DEFAULT_INDUSTRY / SN_CHANNEL_DOMAIN for another environment.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${ENV_FILE:-.env.dev}"
read_env() {
	[ -f "$ENV_FILE" ] || return 0
	grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2- || true
}

API_PORT="${API_PORT:-$(read_env API_PORT)}"
WEB_PORT="${WEB_PORT:-$(read_env WEB_PORT)}"
APP_BASE_URL="${APP_BASE_URL:-$(read_env APP_BASE_URL)}"
SN_DEFAULT_INDUSTRY="${SN_DEFAULT_INDUSTRY:-$(read_env SN_DEFAULT_INDUSTRY)}"
APP_ENV="${APP_ENV:-$(read_env APP_ENV)}"
APP_DOMAIN="${APP_DOMAIN:-$(read_env APP_DOMAIN)}"

# Same resolution order as the web app (apps/web/src/lib/hosts.ts): explicit
# SN_CHANNEL_DOMAIN, else APP_DOMAIN in prd, else path mode.
SN_CHANNEL_DOMAIN="${SN_CHANNEL_DOMAIN:-$(read_env SN_CHANNEL_DOMAIN)}"
if [ -z "$SN_CHANNEL_DOMAIN" ] && [ "$APP_ENV" = "prd" ]; then
	SN_CHANNEL_DOMAIN="$APP_DOMAIN"
fi

API_URL="${API_URL:-http://127.0.0.1:${API_PORT:-46105}}"
APP_BASE_URL="${APP_BASE_URL:-http://localhost:${WEB_PORT:-43991}}"
SN_DEFAULT_INDUSTRY="${SN_DEFAULT_INDUSTRY:-stem-cell}"

export API_URL APP_BASE_URL SN_DEFAULT_INDUSTRY API_PORT WEB_PORT APP_ENV APP_DOMAIN SN_CHANNEL_DOMAIN
exec node apps/web/scripts/channel-inventory.mjs "${1:---write}"
