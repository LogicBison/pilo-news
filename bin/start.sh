#!/usr/bin/env bash
# System News - stack control for dev and prd.
# Every environment-specific file is suffixed with the same dev|prd value:
#   docker-compose.<env>.yml · Dockerfile.<env> · .env.<env>
# There is exactly one .env template (.env.example) and one .env.<env> per
# environment, both at the repo root. Services never carry their own .env.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV="${ENV:-dev}"
CMD="menu"
SERVICE=""
ASSUME_YES=0
shifted=0

usage() {
	cat <<'EOF'
System News stack control

Usage:
  ./bin/start.sh                        interactive menu (default env: dev)
  ./bin/start.sh --env prd up           run a command against prd
  ./bin/start.sh dev status             positional env also works
  ./bin/start.sh prd logs api           follow one service

Commands:
  up        build + start the stack
  down      stop containers (volumes kept)
  restart   restart the stack
  status    containers + /v1/health
  logs      follow logs (optional service)
  shell     open a shell in a service
  test      lint + type + tests in the containers
  migrate   run SQL migrations
  refresh   force a news fetch now
  backup    pg_dump into backups/
  restore   restore a backup
  init-env  create .env.<env> from .env.example
  destroy   stop + delete volumes (typed confirmation)
  menu      interactive menu
  help      this text

Environment files (all at repo root):
  docker-compose.dev.yml / docker-compose.prd.yml
  apps/*/Dockerfile.dev / apps/*/Dockerfile.prd
  .env.example (tracked) -> .env.dev / .env.prd (ignored)
EOF
}

info() { printf '\033[36m%s\033[0m\n' "$*"; }
ok() { printf '\033[32m%s\033[0m\n' "$*"; }
warn() { printf '\033[33m%s\033[0m\n' "$*" >&2; }
err() { printf '\033[31m%s\033[0m\n' "$*" >&2; }

validate_env() {
	case "$ENV" in
	dev | prd) ;;
	*)
		err "invalid environment '$ENV' - use dev or prd"
		exit 2
		;;
	esac
	COMPOSE_FILE="docker-compose.${ENV}.yml"
	ENV_FILE=".env.${ENV}"
}

compose() {
	docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

env_value() {
	local key="$1" default="${2:-}"
	local value
	value="$(grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- || true)"
	printf '%s' "${value:-$default}"
}

ensure_env() {
	if [[ ! -f "$ENV_FILE" ]]; then
		warn "$ENV_FILE missing - creating it from .env.example"
		init_env
	fi
}

init_env() {
	if [[ -f "$ENV_FILE" ]]; then
		ok "$ENV_FILE already exists (left untouched)"
		return 0
	fi
	cp .env.example "$ENV_FILE"
	chmod 600 "$ENV_FILE"
	local secret
	secret="$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')"
	sed -i.bak \
		-e "s/^COMPOSE_PROJECT_NAME=.*/COMPOSE_PROJECT_NAME=system-news-${ENV}/" \
		-e "s/^STACK_SUFFIX=.*/STACK_SUFFIX=${ENV}/" \
		-e "s/^APP_ENV=.*/APP_ENV=${ENV}/" \
		-e "s/^SECRET_KEY=.*/SECRET_KEY=${secret}/" \
		"$ENV_FILE"
	rm -f "${ENV_FILE}.bak"
	ok "created $ENV_FILE (mode 600)"
}

require_compose() {
	if [[ ! -f "$COMPOSE_FILE" ]]; then
		err "$COMPOSE_FILE missing"
		exit 2
	fi
	ensure_env
}

wait_health() {
	local url="http://localhost:$(env_value API_PORT 8080)/v1/health"
	local tries="${1:-30}"
	for ((i = 1; i <= tries; i++)); do
		if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
			return 0
		fi
		sleep 2
	done
	return 1
}

cmd_up() {
	require_compose
	info "building and starting $ENV stack"
	compose up -d --build
	if wait_health 45; then
		ok "stack up: http://localhost:$(env_value WEB_PORT 3000)  api: http://localhost:$(env_value API_PORT 8080)/v1/health"
	else
		warn "api health not ready yet - check: ./bin/start.sh --env $ENV logs api"
	fi
}

cmd_down() {
	require_compose
	info "stopping $ENV stack (volumes kept)"
	compose down
}

cmd_restart() {
	require_compose
	compose restart
	wait_health 30 && ok "restarted" || warn "health not ready"
}

cmd_status() {
	require_compose
	compose ps
	local url="http://localhost:$(env_value API_PORT 8080)/v1/health"
	if curl -fsS --max-time 2 "$url" 2>/dev/null; then
		echo
		ok "api healthy"
	else
		warn "api not responding at $url"
	fi
}

cmd_logs() {
	require_compose
	if [[ -n "$SERVICE" ]]; then
		compose logs -f --tail=100 "$SERVICE"
	else
		compose logs -f --tail=100
	fi
}

cmd_shell() {
	require_compose
	if [[ -z "$SERVICE" ]]; then
		read -r -p "service (api|worker|web|postgres|redis) [api]: " SERVICE
		SERVICE="${SERVICE:-api}"
	fi
	compose exec "$SERVICE" sh
}

cmd_test() {
	require_compose
	info "api: ruff + mypy + pytest"
	compose exec -T api sh -c "cd /app && ruff check . && ruff format --check . && mypy src && pytest -q"
	info "web: lint + typecheck"
	compose exec -T web sh -c "cd /app && pnpm lint && pnpm typecheck"
	ok "all checks passed"
}

cmd_migrate() {
	require_compose
	compose exec -T api python -m news_api.platform.migrations
}

cmd_refresh() {
	require_compose
	compose exec -T api python -m news_api.cli refresh --industry all --force
}

cmd_backup() {
	require_compose
	mkdir -p backups
	local stamp db user file
	stamp="$(date -u +%Y%m%d-%H%M%S)"
	db="$(env_value POSTGRES_DB news)"
	user="$(env_value POSTGRES_USER news)"
	file="backups/news-${ENV}-${stamp}.dump"
	info "dumping $db -> $file"
	compose exec -T postgres pg_dump -U "$user" -d "$db" -Fc >"$file"
	ok "backup written: $file"
}

cmd_restore() {
	require_compose
	local files=()
	while IFS= read -r f; do files+=("$f"); done < <(ls -1t backups/news-"${ENV}"-*.dump 2>/dev/null || true)
	if [[ ${#files[@]} -eq 0 ]]; then
		err "no backups for $ENV in backups/"
		return 1
	fi
	local i=1
	for f in "${files[@]}"; do
		printf '  %d) %s\n' "$i" "$f"
		i=$((i + 1))
	done
	read -r -p "restore which number? " pick
	local chosen="${files[$((pick - 1))]:-}"
	[[ -n "$chosen" ]] || {
		err "invalid choice"
		return 1
	}
	if [[ $ASSUME_YES -ne 1 ]]; then
		read -r -p "restore $chosen over the $ENV database? [y/N] " answer
		[[ "$answer" == "y" || "$answer" == "Y" ]] || return 0
	fi
	local db user
	db="$(env_value POSTGRES_DB news)"
	user="$(env_value POSTGRES_USER news)"
	compose exec -T postgres pg_restore -U "$user" -d "$db" --clean --if-exists <"$chosen"
	ok "restored $chosen"
}

cmd_destroy() {
	require_compose
	warn "this deletes the $ENV containers AND volumes (database, redis, caddy data)"
	if [[ $ASSUME_YES -ne 1 ]]; then
		read -r -p "type destroy-${ENV} to confirm: " answer
		[[ "$answer" == "destroy-${ENV}" ]] || {
			info "aborted"
			return 0
		}
	fi
	compose down -v
	ok "$ENV stack destroyed"
}

banner() {
	local line="System News - stack control"
	printf '\n\033[1m%s\033[0m\n' "$line"
	printf 'environment: \033[36m%s\033[0m   compose: %s   env file: %s\n' "$ENV" "$COMPOSE_FILE" "$ENV_FILE"
	printf '%s\n' "------------------------------------------------------------"
}

menu() {
	if [[ ! -f "$ENV_FILE" && -t 0 ]]; then
		read -r -p "$ENV_FILE missing - create it from .env.example now? [Y/n] " answer
		[[ "$answer" == "n" || "$answer" == "N" ]] || init_env
	fi
	while true; do
		banner
		cat <<'EOF'
 1) up        build + start the stack
 2) down      stop (volumes kept)
 3) restart
 4) status    containers + health
 5) logs      follow logs
 6) shell     shell into a service
 7) test      lint + type + tests
 8) migrate   run SQL migrations
 9) refresh   force a news fetch now
10) backup    pg_dump into backups/
11) restore   restore a backup
12) init-env  create .env.<env> from .env.example
13) destroy   stop + delete volumes (typed confirm)
 0) exit
EOF
		read -r -p "select> " choice || exit 0
		case "$choice" in
		1) cmd_up ;;
		2) cmd_down ;;
		3) cmd_restart ;;
		4) cmd_status ;;
		5) read -r -p "service (blank = all): " SERVICE; cmd_logs ;;
		6) SERVICE=""; cmd_shell ;;
		7) cmd_test ;;
		8) cmd_migrate ;;
		9) cmd_refresh ;;
		10) cmd_backup ;;
		11) cmd_restore ;;
		12) init_env ;;
		13) cmd_destroy ;;
		0 | q | quit) exit 0 ;;
		*) warn "unknown option" ;;
		esac
		echo
		read -r -p "press enter to continue" _ || exit 0
	done
}

# --- argument parsing -------------------------------------------------------
while [[ $# -gt 0 ]]; do
	case "$1" in
	-e | --env)
		ENV="${2:-}"
		shift 2
		;;
	-y | --yes)
		ASSUME_YES=1
		shift
		;;
	-h | --help)
		usage
		exit 0
		;;
	dev | prd)
		if [[ $shifted -eq 0 ]]; then
			ENV="$1"
		else
			SERVICE="$1"
		fi
		shift
		;;
	menu | up | down | restart | status | logs | shell | test | migrate | refresh | backup | restore | init-env | destroy)
		CMD="$1"
		shifted=1
		shift
		# everything after the command is the optional service/target
		if [[ $# -gt 0 && "$1" != -* ]]; then
			SERVICE="$1"
			shift
		fi
		;;
	*)
		SERVICE="$1"
		shift
		;;
	esac
done

validate_env

case "$CMD" in
menu) menu ;;
up) cmd_up ;;
down) cmd_down ;;
restart) cmd_restart ;;
status) cmd_status ;;
logs) cmd_logs ;;
shell) cmd_shell ;;
test) cmd_test ;;
migrate) cmd_migrate ;;
refresh) cmd_refresh ;;
backup) cmd_backup ;;
restore) cmd_restore ;;
init-env) init_env ;;
destroy) cmd_destroy ;;
*)
	err "unknown command: $CMD"
	usage
	exit 2
	;;
esac
