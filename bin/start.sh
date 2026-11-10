#!/usr/bin/env bash
# System News - stack control for dev and prd.
# Every environment-specific file is suffixed with the same dev|prd value:
#   docker-compose.<env>.yml · Dockerfile.<env> · .env.<env>
# There is exactly one .env template (.env.example) and one .env.<env> per
# environment, both at the repo root. Services never carry their own .env.
#
# Production serves each channel from its own subdomain through the host's
# nginx (`./bin/start.sh --env prd domains --write` renders ops/nginx/sites/).
# Dev gets the same behaviour on *.localhost with no proxy at all.

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
  industry  switch SN_DEFAULT_INDUSTRY (demo switch, no rebuild)
  domains   per-channel hosts: table, nginx sites (--write, --http-only)
  certs     certificate help, coverage check (--check), issuance (--run)
  hosts     verify channel subdomain routing against the running stack
  preflight production readiness checks (secrets, hosts, ports, config)
  backup    portable bundle: postgres dump + config + env + media + manifest
  restore   restore a bundle (asks about config/media/nginx) or a volume snapshot
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

# File value wins; a process-environment value is used when the file has no
# such key, so one-off overrides stay possible without editing the env file.
env_value() {
	local key="$1" default="${2:-}"
	local value
	value="$(grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- || true)"
	if [[ -z "$value" && -n "${!key:-}" ]]; then
		value="${!key}"
	fi
	printf '%s' "${value:-$default}"
}

env_set() {
	local key="$1" value="$2"
	if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
		sed -i.bak "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
		rm -f "${ENV_FILE}.bak"
	else
		printf '\n%s=%s\n' "$key" "$value" >>"$ENV_FILE"
	fi
}

ensure_env() {
	if [[ ! -f "$ENV_FILE" ]]; then
		warn "$ENV_FILE missing - creating it from .env.example"
		init_env
	fi
}

random_port() {
	local candidate=""
	for _ in $(seq 1 60); do
		candidate="$(shuf -i 20000-60000 -n1 2>/dev/null || (head -c 4 /dev/urandom | od -An -tu4 | awk '{print 20000 + ($1 % 40000)}'))"
		[[ -n "$candidate" ]] || continue
		if ! ss -ltn 2>/dev/null | grep -qE "[:.]${candidate}[[:space:]]"; then
			printf '%s' "$candidate"
			return 0
		fi
	done
	printf '%s' "$candidate"
}

init_env() {
	if [[ -f "$ENV_FILE" ]]; then
		ok "$ENV_FILE already exists (left untouched)"
		return 0
	fi
	cp .env.example "$ENV_FILE"
	chmod 600 "$ENV_FILE"
	local secret admin_password pg_password redis_password web api pg redis channel_domain cert_name pg_user pg_db
	pg_user="$(env_value POSTGRES_USER news)"
	pg_db="$(env_value POSTGRES_DB news)"
	secret="$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')"
	admin_password="$(openssl rand -base64 18 2>/dev/null | tr -d '\n' || head -c 18 /dev/urandom | base64 | tr -d '\n')"
	pg_password="$(openssl rand -hex 24 2>/dev/null || head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n')"
	redis_password="$(openssl rand -hex 24 2>/dev/null || head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n')"
	web="$(random_port)"; api="$(random_port)"; pg="$(random_port)"; redis="$(random_port)"
	while [[ "$api" == "$web" || "$pg" == "$web" || "$redis" == "$web" || "$api" == "$pg" || "$api" == "$redis" || "$pg" == "$redis" ]]; do
		web="$(random_port)"; api="$(random_port)"; pg="$(random_port)"; redis="$(random_port)"
	done
	# dev: channel subdomains on *.localhost (resolves to 127.0.0.1 everywhere).
	# prd: the domain comes from APP_DOMAIN, the certificate from SSL_CERT_NAME.
	if [[ "$ENV" == "dev" ]]; then
		channel_domain="localhost"
		cert_name=""
	else
		channel_domain=""
		cert_name="$(env_value APP_DOMAIN localhost)"
	fi
	sed -i.bak \
		-e "s/^COMPOSE_PROJECT_NAME=.*/COMPOSE_PROJECT_NAME=system-news-${ENV}/" \
		-e "s/^STACK_SUFFIX=.*/STACK_SUFFIX=${ENV}/" \
		-e "s/^APP_ENV=.*/APP_ENV=${ENV}/" \
		-e "s/^SECRET_KEY=.*/SECRET_KEY=${secret}/" \
		-e "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=${admin_password}|" \
		-e "s/^WEB_PORT=.*/WEB_PORT=${web}/" \
		-e "s/^API_PORT=.*/API_PORT=${api}/" \
		-e "s/^POSTGRES_PORT=.*/POSTGRES_PORT=${pg}/" \
		-e "s/^REDIS_PORT=.*/REDIS_PORT=${redis}/" \
		-e "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${pg_password}/" \
		-e "s#^DATABASE_URL=.*#DATABASE_URL=postgresql+asyncpg://${pg_user}:${pg_password}@postgres:5432/${pg_db}#" \
		-e "s#^REDIS_URL=.*#REDIS_URL=redis://:${redis_password}@redis:6379/0#" \
		-e "s/^SN_CHANNEL_DOMAIN=.*/SN_CHANNEL_DOMAIN=${channel_domain}/" \
		-e "s/^SSL_CERT_NAME=.*/SSL_CERT_NAME=${cert_name}/" \
		-e "s#^APP_BASE_URL=.*#APP_BASE_URL=http://localhost:${web}#" \
		-e "s#^NEXT_PUBLIC_API_BASE=.*#NEXT_PUBLIC_API_BASE=http://localhost:${api}#" \
		"$ENV_FILE"
	rm -f "${ENV_FILE}.bak"
	env_set REDIS_PASSWORD "$redis_password"
	ok "created $ENV_FILE (mode 600)"
	info "web: http://localhost:${web}  api: http://localhost:${api}/v1/health"
	if [[ -n "$channel_domain" ]]; then
		info "channel hosts: http://<slug>.${channel_domain}:${web}"
	fi
	info "admin: $(env_value ADMIN_EMAIL admin@example.com) / ${admin_password}"
}

require_compose() {
	if [[ ! -f "$COMPOSE_FILE" ]]; then
		err "$COMPOSE_FILE missing"
		exit 2
	fi
	ensure_env
}

api_url() { printf 'http://localhost:%s/v1/health' "$(env_value API_PORT 8080)"; }

wait_health() {
	local url tries="${1:-30}" i
	url="$(api_url)"
	for ((i = 1; i <= tries; i++)); do
		if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
			return 0
		fi
		sleep 2
	done
	return 1
}

wait_postgres() {
	local tries="${1:-30}" i
	for ((i = 1; i <= tries; i++)); do
		if compose exec -T postgres pg_isready -q >/dev/null 2>&1; then
			return 0
		fi
		sleep 1
	done
	return 1
}

cmd_up() {
	require_compose
	info "building and starting $ENV stack"
	compose up -d --build
	if wait_health 45; then
		ok "stack up: http://localhost:$(env_value WEB_PORT 3000)  api: $(api_url)"
		if [[ -n "$(channel_domain)" ]]; then
			ok "channel host: http://$(default_slug).$(channel_domain):$(env_value WEB_PORT 3000)"
		fi
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
	local url
	url="$(api_url)"
	if curl -fsS --max-time 2 "$url" 2>/dev/null; then
		echo
		ok "api healthy at $url"
		ok "web at http://localhost:$(env_value WEB_PORT 3000)"
		if [[ -n "$(channel_domain)" ]]; then
			ok "channels at http://<slug>.$(channel_domain):$(env_value WEB_PORT 3000)"
		fi
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
	info "web: lint + typecheck + catalogs/themes"
	compose exec -T web sh -c "cd /app && pnpm lint && pnpm typecheck && pnpm check"
	if command -v node >/dev/null 2>&1; then
		info "inventory: channel list"
		ENV_FILE="$ENV_FILE" ./bin/channels.sh --check
		if [ -x .work.biz/scripts/offers.sh ]; then
			info "inventory: offer list"
			.work.biz/scripts/offers.sh --check
		fi
	else
		warn "node not found - inventory checks skipped"
	fi
	if [[ -n "$(channel_domain)" ]]; then
		cmd_hosts
	fi
	ok "all checks passed"
}

cmd_migrate() {
	require_compose
	compose exec -T api python -m news_api.platform.migrations
	# Seeds and profile imports land here, so this is the moment a channel set
	# can go stale without anyone noticing. Check, do not rewrite: the operator
	# decides what enters the commit.
	if command -v node >/dev/null 2>&1 && ! ENV_FILE="$ENV_FILE" ./bin/channels.sh --check >/dev/null 2>&1; then
		warn "channel inventory is stale - run ./bin/channels.sh --write and commit docs/channel-inventory.md"
	fi
}

cmd_refresh() {
	require_compose
	compose exec -T api python -m news_api.cli refresh --industry all --force
}

# Switch the default industry used by the web root redirect. Runtime env only:
# recreates the web container, never rebuilds it.
cmd_industry() {
	require_compose
	local slug="${SERVICE:-}"
	if [[ -z "$slug" ]]; then
		err "usage: ./bin/start.sh --env $ENV industry <slug>"
		return 2
	fi
	local api_port
	api_port="$(env_value API_PORT 8080)"
	if ! curl -fsS --max-time 3 "http://localhost:${api_port}/v1/industries/${slug}" >/dev/null 2>&1; then
		err "unknown industry '$slug' - list with: curl http://localhost:${api_port}/v1/industries"
		return 2
	fi
	env_set SN_DEFAULT_INDUSTRY "$slug"
	info "SN_DEFAULT_INDUSTRY=${slug} in $ENV_FILE"
	compose up -d --force-recreate web >/dev/null
	ok "web recreated"
	if [[ -n "$(channel_domain)" ]]; then
		ok "open http://${slug}.$(channel_domain):$(env_value WEB_PORT 3000)/"
	else
		ok "open http://localhost:$(env_value WEB_PORT 3000)/"
	fi
}

# --- channel domains -------------------------------------------------------

channel_domain() {
	local explicit
	explicit="$(env_value SN_CHANNEL_DOMAIN "")"
	if [[ -n "$explicit" ]]; then
		printf '%s' "$explicit"
		return
	fi
	if [[ "$(env_value APP_ENV "$ENV")" == "prd" ]]; then
		env_value APP_DOMAIN ""
	fi
}

default_slug() {
	env_value SN_DEFAULT_INDUSTRY legal
}

# Deployment profiles on disk, plus any channel the running API knows about
# (channels created from the admin console exist only in the database).
channel_slugs() {
	local on_disk="" remote="" api_port
	if compgen -G "apps/api/config/deployments/*.json" >/dev/null; then
		on_disk="$(for f in apps/api/config/deployments/*.json; do
			basename "$f" .json
		done)"
	fi
	api_port="$(env_value API_PORT 8080)"
	if curl -fsS --max-time 3 "http://localhost:${api_port}/v1/industries" 2>/dev/null |
		tr ',' '\n' | sed -n 's/.*"slug":"\([a-z0-9-]*\)".*/\1/p' >/tmp/sn-slugs.$$ 2>/dev/null; then
		remote="$(cat /tmp/sn-slugs.$$)"
	fi
	rm -f /tmp/sn-slugs.$$
	{
		printf '%s\n' "$on_disk"
		printf '%s\n' "$remote"
	} | sed '/^$/d' | grep -vx example | sort -u
}

require_domain() {
	local domain
	domain="$(channel_domain)"
	if [[ -z "$domain" ]]; then
		err "no channel domain - set SN_CHANNEL_DOMAIN (dev: localhost) or APP_DOMAIN with APP_ENV=prd"
		return 1
	fi
	printf '%s' "$domain"
}

cmd_domains() {
	require_compose
	local domain
	domain="$(require_domain)" || return 1
	local web_port api_port scheme
	web_port="$(env_value WEB_PORT 3000)"
	api_port="$(env_value API_PORT 8080)"
	scheme="http"
	[[ "$(env_value APP_ENV "$ENV")" == "prd" ]] && scheme="https"
	local slugs
	slugs="$(channel_slugs)"
	if [[ -z "$slugs" ]]; then
		err "no channels found - run migrations or apply a deployment profile"
		return 1
	fi

	local suffix=""
	[[ "$scheme" == "http" ]] && suffix=":${web_port}"
	printf '\n%-38s %-18s %s\n' "host" "channel" "url"
	printf '%-38s %-18s %s\n' "--------------------------------------" "------------------" "---"
	printf '%-38s %-18s %s\n' "${domain}" "-" "${scheme}://${domain}${suffix}"
	printf '%-38s %-18s %s\n' "www.${domain}" "-" "${scheme}://www.${domain}${suffix}"
	while IFS= read -r slug; do
		printf '%-38s %-18s %s\n' "${slug}.${domain}" "${slug}" "${scheme}://${slug}.${domain}${suffix}"
	done <<<"$slugs"
	echo

	case " ${TARGETS:-} " in
	*" --write "* | *" --http-only "* | *" --bootstrap "*) ;;
	*)
		info "render nginx sites with: ./bin/start.sh --env $ENV domains --write"
		return 0
		;;
	esac

	if [[ ! -f ops/nginx/site.conf.template ]]; then
		err "ops/nginx/site.conf.template missing"
		return 1
	fi

	local dir="ops/nginx/sites" cert_name cert_dir http_only=0
	cert_name="$(env_value SSL_CERT_NAME "$domain")"
	[[ -n "$cert_name" ]] || cert_name="$domain"
	cert_dir="$(cert_dir_for "$cert_name")"
	case " ${TARGETS:-} " in
	*" --http-only "* | *" --bootstrap "*) http_only=1 ;;
	esac
	rm -rf "$dir"
	mkdir -p "$dir"

	render_site() {
		local host="$1" channel="$2" out="$3"
		sed \
			-e "s|__HOST__|${host}|g" \
			-e "s|__CHANNEL__|${channel}|g" \
			-e "s|__WEB_PORT__|${web_port}|g" \
			-e "s|__API_PORT__|${api_port}|g" \
			-e "s|__CERT_NAME__|${cert_name}|g" \
			-e "s|__CERT_DIR__|${cert_dir}|g" \
			ops/nginx/site.conf.template >"$out"
		if [[ $http_only -eq 1 ]]; then
			sed -i '/bootstrap: tls-start/,/bootstrap: tls-end/d' "$out"
		fi
	}

	render_site "$domain" "-" "$dir/00-apex.conf"
	render_site "www.${domain}" "-" "$dir/01-www.conf"
	while IFS= read -r slug; do
		render_site "${slug}.${domain}" "$slug" "$dir/10-${slug}.conf"
	done <<<"$slugs"

	if [[ $http_only -eq 1 ]]; then
		ok "wrote $(find "$dir" -name '*.conf' | wc -l | tr -d ' ') HTTP-only host blocks to $dir (bootstrap for certificate issuance)"
		cat <<EOF

Next on the production host (phase 1 - get port 80 answering):
  sudo mkdir -p /var/www/certbot
  sudo sh -c 'printf "include $ROOT_DIR/ops/nginx/sites/*.conf;\n" > /etc/nginx/sites-enabled/system-news.conf'
  sudo nginx -t && sudo systemctl reload nginx
  curl -fsS -o /dev/null -w '%{http_code}\n' "http://${domain}/.well-known/acme-challenge/probe" || true

Then issue the certificate (phase 2):
  ./bin/start.sh --env $ENV certs --run      # add -y to skip the confirmation
  ./bin/start.sh --env $ENV domains --write  # full config with TLS
  sudo nginx -t && sudo systemctl reload nginx

EOF
		return 0
	fi
	ok "wrote $(find "$dir" -name '*.conf' | wc -l | tr -d ' ') site files to $dir (cert: ${cert_name} at ${cert_dir})"
	cat <<EOF

Next on the production host:
  sudo sh -c 'printf "include $ROOT_DIR/ops/nginx/sites/*.conf;\n" > /etc/nginx/sites-enabled/system-news.conf'
  sudo nginx -t && sudo systemctl reload nginx

EOF
}

cert_dir_for() {
	local name="$1" dir
	dir="$(env_value SSL_CERT_DIR "/etc/letsencrypt/live/${name}")"
	[[ -n "$dir" ]] || dir="/etc/letsencrypt/live/${name}"
	printf '%s' "$dir"
}

# The apex, www, and one host per channel - every name a certificate must carry.
cert_hosts() {
	local domain="$1"
	printf '%s\n' "$domain" "www.${domain}"
	channel_slugs | sed "s|\$|.${domain}|"
}

days_until() {
	local when="$1" secs
	[[ -n "$when" ]] || {
		printf 'unknown'
		return
	}
	secs="$(date -d "$when" +%s 2>/dev/null || true)"
	[[ -n "$secs" ]] || {
		printf 'unknown'
		return
	}
	printf '%s' $(((secs - $(date +%s)) / 86400))
}

host_covered() {
	local host="$1" sans="$2" san suffix
	while IFS= read -r san; do
		[[ -n "$san" ]] || continue
		[[ "$san" == "$host" ]] && return 0
		if [[ "$san" == "*."* ]]; then
			suffix="${san#\*}"
			if [[ "$host" == *"$suffix" && "${host%"$suffix"}" != *.* ]]; then
				return 0
			fi
		fi
	done <<<"$sans"
	return 1
}

certs_print() {
	local domain="$1" cert_name="$2" cert_dir="$3" hosts="$4" host
	info "certificate name: ${cert_name} (SSL_CERT_NAME, defaulting to the domain)"
	info "certificate path: ${cert_dir}"
	echo
	echo "Phase 1 - let the ACME challenge answer on port 80 (nginx cannot load a"
	echo "443 block whose certificate does not exist yet):"
	echo "  ./bin/start.sh --env $ENV domains --write --http-only"
	echo "  sudo mkdir -p /var/www/certbot"
	echo "  sudo sh -c 'printf \"include $ROOT_DIR/ops/nginx/sites/*.conf;\\n\" > /etc/nginx/sites-enabled/system-news.conf'"
	echo "  sudo nginx -t && sudo systemctl reload nginx"
	echo
	echo "Phase 2 - issue one certificate for ${domain}, www and every channel:"
	echo "  sudo certbot certonly --webroot -w /var/www/certbot \\"
	while IFS= read -r host; do
		[[ -n "$host" ]] || continue
		echo "      -d ${host} \\"
	done <<<"$hosts"
	echo "      --cert-name ${cert_name}"
	echo
	echo "  # or let this script do it, staging dry run first:"
	echo "  sudo ./bin/start.sh --env $ENV certs --run"
	echo
	echo "Phase 3 - full config with TLS, then reload:"
	echo "  ./bin/start.sh --env $ENV domains --write"
	echo "  sudo nginx -t && sudo systemctl reload nginx"
	echo "  ./bin/start.sh --env $ENV certs --check"
	echo
	echo "Renewal (certbot's systemd timer runs this; the hook reloads nginx):"
	echo "  sudo certbot renew --deploy-hook 'systemctl reload nginx'"
	echo
	echo "Wildcard alternative - only if channel hosts change often, or port 80 is"
	echo "not reachable from the internet. It needs DNS-01, so certbot needs your DNS"
	echo "provider's plugin and an API token, and it covers \"*.${domain}\" but not"
	echo "the apex, hence both names:"
	echo "  sudo certbot certonly --dns-<provider> --dns-<provider>-credentials /root/.secrets/${domain}.ini \\"
	echo "      -d ${domain} -d '*.${domain}' --cert-name ${cert_name}"
	echo "  # SSL_CERT_NAME / SSL_CERT_DIR need no change: the wildcard lands in the same directory."
}

certs_check() {
	local domain="$1" cert_name="$2" cert_dir="$3" hosts="$4"
	local full="${cert_dir}/fullchain.pem" sans expiry days host missing=0
	if [[ ! -r "$full" ]]; then
		err "no readable certificate at ${full}"
		info "if it exists, this check needs root: sudo ./bin/start.sh --env $ENV certs --check"
		info "if it does not, issue it: ./bin/start.sh --env $ENV certs --run"
		return 1
	fi

	# One name per line: the SAN block is the line after its header, comma
	# separated, each entry prefixed with `DNS:`.
	sans="$(openssl x509 -in "$full" -noout -text 2>/dev/null |
		sed -n '/Subject Alternative Name/{n;p;}' | tr ',' '\n' |
		sed 's/^[[:space:]]*DNS://; s/^[[:space:]]*//; s/[[:space:]]*$//' |
		sed '/^$/d' | sort -u)"
	expiry="$(openssl x509 -in "$full" -noout -enddate 2>/dev/null | cut -d= -f2)"
	days="$(days_until "$expiry")"

	info "certificate ${cert_name} at ${cert_dir}"
	printf '  expires %s (%s days)\n' "${expiry:-unknown}" "$days"
	printf '  names: %s\n' "$(tr '\n' ' ' <<<"$sans")"
	echo
	while IFS= read -r host; do
		[[ -n "$host" ]] || continue
		if host_covered "$host" "$sans"; then
			printf '  \033[32mcovered\033[0m %s\n' "$host"
		else
			printf '  \033[31mMISSING\033[0m %s\n' "$host"
			missing=$((missing + 1))
		fi
	done <<<"$hosts"

	echo
	if [[ "$days" != unknown && "$days" -lt 0 ]]; then
		err "the certificate has expired - renew before reloading nginx"
		return 1
	fi
	if [[ "$days" != unknown && "$days" -lt 14 ]]; then
		warn "the certificate expires in ${days} days - check the renewal timer"
	fi
	if [[ $missing -gt 0 ]]; then
		err "${missing} host(s) are not on this certificate - reissue with --expand or a wildcard"
		return 1
	fi
	ok "certificate covers every host"
}

certs_run() {
	local domain="$1" cert_name="$2" cert_dir="$3" hosts="$4" dry_only=0
	local email args=() host
	email="$(env_value ACME_EMAIL "$(env_value CONTACT_TO news@${domain})")"

	case " ${TARGETS:-} " in
	*" --dry-run "*) dry_only=1 ;;
	esac

	if ! command -v certbot >/dev/null 2>&1; then
		err "certbot is not installed - apt-get install certbot"
		return 1
	fi
	if [[ "$(id -u)" -ne 0 ]]; then
		err "certbot needs root: sudo ./bin/start.sh --env $ENV certs --run"
		return 1
	fi

	mkdir -p /var/www/certbot
	while IFS= read -r host; do
		[[ -n "$host" ]] || continue
		args+=(-d "$host")
	done <<<"$hosts"

	info "names: ${args[*]}"
	info "account email: ${email}"
	info "certificate: ${cert_name} at ${cert_dir}"

	if [[ $ASSUME_YES -ne 1 ]]; then
		warn "this registers an ACME account and requests a certificate from Let's Encrypt"
		read -r -p "type issue-${domain} to continue: " answer
		[[ "$answer" == "issue-${domain}" ]] || {
			info "aborted"
			return 0
		}
	fi

	info "staging dry run first - a typo here costs nothing"
	if ! certbot certonly --webroot -w /var/www/certbot --cert-name "$cert_name" \
		"${args[@]}" --dry-run --non-interactive --agree-tos -m "$email"; then
		err "dry run failed - fix DNS, port 80 or the webroot, then re-run"
		info "phase 1 first: ./bin/start.sh --env $ENV domains --write --http-only"
		return 1
	fi

	if [[ $dry_only -eq 1 ]]; then
		ok "dry run passed; run without --dry-run to issue for real"
		return 0
	fi

	info "issuing for real"
	if ! certbot certonly --webroot -w /var/www/certbot --cert-name "$cert_name" \
		"${args[@]}" --non-interactive --agree-tos -m "$email"; then
		err "issuance failed"
		return 1
	fi

	ok "certificate issued at ${cert_dir}"
	info "now: ./bin/start.sh --env $ENV domains --write  (full config with TLS)"
	info "then: sudo nginx -t && sudo systemctl reload nginx && ./bin/start.sh --env $ENV certs --check"
}

cmd_certs() {
	require_compose
	local domain cert_name cert_dir hosts
	domain="$(require_domain)" || return 1
	cert_name="$(env_value SSL_CERT_NAME "$domain")"
	[[ -n "$cert_name" ]] || cert_name="$domain"
	cert_dir="$(cert_dir_for "$cert_name")"
	hosts="$(cert_hosts "$domain")"

	case " ${TARGETS:-} " in
	*" --check "*) certs_check "$domain" "$cert_name" "$cert_dir" "$hosts" ;;
	*" --run "*) certs_run "$domain" "$cert_name" "$cert_dir" "$hosts" ;;
	*) certs_print "$domain" "$cert_name" "$cert_dir" "$hosts" ;;
	esac
}

# Verifies the routing contract through real HTTP requests, using the Host
# header the edge proxy sets, so dev and prd are checked the same way.
cmd_hosts() {
	require_compose
	local domain web_port api_port base
	domain="$(channel_domain)"
	if [[ -z "$domain" ]]; then
		warn "path mode (SN_CHANNEL_DOMAIN unset) - host checks skipped"
		return 0
	fi
	web_port="$(env_value WEB_PORT 3000)"
	api_port="$(env_value API_PORT 8080)"
	base="http://localhost:${web_port}"
	local slug host failures=0
	slug="$(channel_slugs | head -1)"
	[[ -n "$slug" ]] || {
		err "no channels to check"
		return 1
	}
	host="${slug}.${domain}"

	expect() {
		local label="$1" expected="$2" got="$3"
		if [[ "$got" == *"$expected"* ]]; then
			printf '  \033[32mpass\033[0m %s\n' "$label"
		else
			printf '  \033[31mFAIL\033[0m %s -> %s\n' "$label" "$got"
			failures=$((failures + 1))
		fi
	}

	info "host routing checks (channel: ${slug})"

	local apex_root apex_body apex_services
	apex_root="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${domain}:${web_port}" "${base}/")"
	expect "apex / renders the lobby" "200" "$apex_root"

	apex_body="$(curl -s -H "Host: ${domain}:${web_port}" "${base}/" || true)"
	expect "the lobby lists every desk" "$(channel_slugs | wc -l | tr -d ' ') desk plates" \
		"$(printf '%s' "$apex_body" | grep -o 'class="lb-plate"' | wc -l | tr -d ' ') desk plates"
	expect "the lobby carries the brand" "HeraldFox" "$apex_body"

	apex_services="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${domain}:${web_port}" "${base}/services")"
	expect "apex /services renders" "200" "$apex_services"

	local channel_root
	channel_root="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${host}:${web_port}" "${base}/")"
	expect "channel / renders" "200" "$channel_root"

	local about
	about="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${host}:${web_port}" "${base}/about")"
	expect "channel /about renders" "200" "$about"

	local spanish
	spanish="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${host}:${web_port}" "${base}/es")"
	expect "channel /es renders" "200" "$spanish"

	local legacy
	legacy="$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -H "Host: ${host}:${web_port}" "${base}/${slug}/about")"
	expect "legacy /${slug}/about redirects to /about" "308 http://${host}:${web_port}/about" "$legacy"

	local admin
	admin="$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -H "Host: ${host}:${web_port}" "${base}/admin")"
	expect "channel /admin redirects to the apex" "308 http://${domain}:${web_port}/admin" "$admin"

	local feed
	feed="$(curl -s -H "Host: ${host}:${web_port}" "${base}/feed.xml" || true)"
	expect "channel /feed.xml is host-scoped" "<link>http://${host}:${web_port}</link>" "$feed"

	local sitemap
	sitemap="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${host}:${web_port}" "${base}/sitemap.xml")"
	expect "channel /sitemap.xml renders" "200" "$sitemap"

	local prefixed
	prefixed="$(curl -s -H "Host: ${host}:${web_port}" "${base}/" | grep -c "href=\"/${slug}" || true)"
	expect "channel pages emit no /${slug} prefixed links" "0" "$prefixed"

	local canonical
	canonical="$(curl -s -H "Host: ${host}:${web_port}" "${base}/about" | grep -o "rel=\"canonical\" href=\"[^\"]*\"" | head -1)"
	expect "canonical points at the channel host" "http://${host}:${web_port}/about" "$canonical"

	local api_health
	api_health="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:${api_port}/v1/health")"
	expect "api health" "200" "$api_health"

	echo
	if [[ $failures -eq 0 ]]; then
		ok "host routing: all checks passed"
		return 0
	fi
	err "host routing: ${failures} check(s) failed"
	return 1
}

# --- production readiness --------------------------------------------------

cmd_preflight() {
	require_compose
	local failures=0 warnings=0

	check_value() {
		local level="$1" label="$2" value="$3" hint="$4"
		if [[ -n "$value" ]]; then
			printf '  \033[32mpass\033[0m %s\n' "$label"
			return 0
		fi
		if [[ "$level" == "fail" ]]; then
			printf '  \033[31mFAIL\033[0m %s\n       %s\n' "$label" "$hint"
			failures=$((failures + 1))
		else
			printf '  \033[33mwarn\033[0m %s\n       %s\n' "$label" "$hint"
			warnings=$((warnings + 1))
		fi
	}

	local app_env secret pg_password redis_password admin_hash admin_password base_url domain channel cert db_url redis_url smtp_lane smtp_host smtp_sender
	app_env="$(env_value APP_ENV "$ENV")"
	secret="$(env_value SECRET_KEY "")"
	pg_password="$(env_value POSTGRES_PASSWORD "")"
	admin_hash="$(env_value ADMIN_PASSWORD_HASH "")"
	admin_password="$(env_value ADMIN_PASSWORD "")"
	base_url="$(env_value APP_BASE_URL "")"
	domain="$(env_value APP_DOMAIN "")"
	channel="$(channel_domain)"
	cert="$(env_value SSL_CERT_NAME "")"
	redis_password="$(env_value REDIS_PASSWORD "")"
	db_url="$(env_value DATABASE_URL "")"
	redis_url="$(env_value REDIS_URL "")"

	info "preflight: $ENV ($ENV_FILE)"

	if [[ "$app_env" == "$ENV" ]]; then
		printf '  \033[32mpass\033[0m APP_ENV matches the environment\n'
	else
		printf '  \033[31mFAIL\033[0m APP_ENV is '%s', expected '%s'\n' "$app_env" "$ENV"
		failures=$((failures + 1))
	fi

	if [[ ${#secret} -ge 32 && "$secret" != change-me* ]]; then
		printf '  \033[32mpass\033[0m SECRET_KEY is set (>=32 chars)\n'
	else
		printf '  \033[31mFAIL\033[0m SECRET_KEY is missing, short or still the placeholder\n'
		failures=$((failures + 1))
	fi

	if [[ ${#pg_password} -ge 16 && "$pg_password" != change-me* ]]; then
		printf '  \033[32mpass\033[0m POSTGRES_PASSWORD is not the placeholder (>=16 chars)\n'
	elif [[ "$ENV" == "prd" ]]; then
		printf '  \033[31mFAIL\033[0m POSTGRES_PASSWORD is missing, short or still the placeholder\n'
		failures=$((failures + 1))
	else
		printf '  \033[33mwarn\033[0m POSTGRES_PASSWORD is the placeholder (fine for dev, never for prd)\n'
		warnings=$((warnings + 1))
	fi

	if [[ -n "$pg_password" && -n "$db_url" ]]; then
		if [[ "$db_url" != *"$pg_password"* ]]; then
			printf '  \033[31mFAIL\033[0m DATABASE_URL does not use POSTGRES_PASSWORD\n'
			failures=$((failures + 1))
		else
			printf '  \033[32mpass\033[0m DATABASE_URL matches POSTGRES_PASSWORD\n'
		fi
	fi

	if [[ "$ENV" == "prd" ]]; then
		if [[ -n "$redis_password" && "$redis_password" != redis ]]; then
			printf '  \033[32mpass\033[0m REDIS_PASSWORD is set\n'
			if [[ -n "$redis_url" && "$redis_url" != *":${redis_password}@"* ]]; then
				printf '  \033[31mFAIL\033[0m REDIS_URL does not use REDIS_PASSWORD\n'
				failures=$((failures + 1))
			else
				printf '  \033[32mpass\033[0m REDIS_URL matches REDIS_PASSWORD\n'
			fi
		else
			printf '  \033[31mFAIL\033[0m REDIS_PASSWORD is the default\n'
			failures=$((failures + 1))
		fi
	fi

	if [[ -n "$admin_hash" || -n "$admin_password" ]]; then
		printf '  \033[32mpass\033[0m admin credential present\n'
	else
		printf '  \033[31mFAIL\033[0m neither ADMIN_PASSWORD_HASH nor ADMIN_PASSWORD is set\n'
		failures=$((failures + 1))
	fi

	if [[ "$ENV" == "prd" ]]; then
		if [[ "$base_url" == https://* && "$base_url" == *"$domain"* ]]; then
			printf '  \033[32mpass\033[0m APP_BASE_URL is https and on APP_DOMAIN\n'
		else
			printf '  \033[31mFAIL\033[0m APP_BASE_URL must be https://%s (is: %s)\n' "$domain" "$base_url"
			failures=$((failures + 1))
		fi
	fi

	check_value warn "AI_API_KEY for ingestion summaries" "$(env_value AI_API_KEY "")" \
		"without it the worker stores items without summaries"
	smtp_lane="$(env_value SMTP_TRANSPORT "")"
	case "$smtp_lane" in
	gateway)
		smtp_host="$(env_value SMTP_GATEWAY_HOST "")"
		smtp_sender="$(env_value SMTP_FROM "")"
		;;
	direct)
		smtp_host="$(env_value SMTP_DIRECT_HOST "")"
		smtp_sender="$(env_value SMTP_FROM "")"
		;;
	*)
		smtp_host="$(env_value SMTP_HOST "")"
		smtp_sender="$(env_value SMTP_FROM "")"
		[[ -n "$smtp_sender" ]] || smtp_sender="$(env_value SMTP_USER "")"
		;;
	esac
	if [[ -n "$smtp_host" && -n "$smtp_sender" ]]; then
		printf '  \033[32mpass\033[0m email transport: %s -> %s\n' "${smtp_lane:-flat}" "$smtp_host"
	else
		printf '  \033[33mwarn\033[0m email transport %s incomplete (host=%s sender=%s)\n' \
			"${smtp_lane:-flat}" "${smtp_host:-none}" "${smtp_sender:-none}"
		printf '       leads are stored but nobody is notified\n'
		warnings=$((warnings + 1))
	fi
	if [[ "$ENV" == "prd" ]]; then
		check_value warn "SSL_CERT_NAME for the nginx sites" "$cert" \
			"set SSL_CERT_NAME to the certbot certificate hosting every channel host"
	fi

	if [[ -n "$channel" ]]; then
		printf '  \033[32mpass\033[0m channel subdomains enabled on %s\n' "$channel"
		local missing=0 slug
		while IFS= read -r slug; do
			if [[ -f "ops/nginx/sites/10-${slug}.conf" ]]; then continue; fi
			missing=$((missing + 1))
			printf '       missing ops/nginx/sites/10-%s.conf\n' "$slug"
		done <<<"$(channel_slugs)"
		if [[ $missing -eq 0 ]]; then
			printf '  \033[32mpass\033[0m nginx site files rendered for every channel\n'
		else
			printf '  \033[33mwarn\033[0m %d channel(s) have no nginx site file - run: ./bin/start.sh --env %s domains --write\n' "$missing" "$ENV"
			warnings=$((warnings + 1))
		fi
	else
		printf '  \033[33mwarn\033[0m channel subdomains disabled (path URLs only)\n'
		warnings=$((warnings + 1))
	fi

	local port owner project
	project="$(compose_project)"
	for port in "$(env_value WEB_PORT 3000)" "$(env_value API_PORT 8080)"; do
		owner="$(docker ps --filter "publish=${port}" --format '{{.Names}}' 2>/dev/null | head -1)"
		if [[ -z "$owner" ]]; then
			printf '  \033[32mpass\033[0m port %s is free\n' "$port"
		elif [[ "$owner" == "${project}"* ]]; then
			printf '  \033[32mpass\033[0m port %s is held by this stack (%s)\n' "$port" "$owner"
		else
			printf '  \033[33mwarn\033[0m port %s is held by %s\n' "$port" "$owner"
			warnings=$((warnings + 1))
		fi
	done

	if [[ -n "$channel" ]] && command -v getent >/dev/null 2>&1; then
		local resolved
		resolved="$(getent ahosts "$channel" 2>/dev/null | awk 'NR==1{print $1}')"
		if [[ -n "$resolved" ]]; then
			printf '  \033[32mpass\033[0m DNS resolves %s -> %s\n' "$channel" "$resolved"
		else
			printf '  \033[33mwarn\033[0m DNS does not resolve %s yet - add the A/AAAA records\n' "$channel"
			warnings=$((warnings + 1))
		fi
	fi

	echo
	if [[ $failures -gt 0 ]]; then
		err "preflight: ${failures} blocking issue(s), ${warnings} warning(s)"
		return 1
	fi
	ok "preflight: no blocking issues (${warnings} warning(s))"
}

# --- backup / restore ------------------------------------------------------

compose_project() {
	env_value COMPOSE_PROJECT_NAME "system-news-${ENV}"
}

volume_exists() {
	docker volume inspect "$1" >/dev/null 2>&1
}

psql_value() {
	compose exec -T postgres psql -U "$(env_value POSTGRES_USER news)" \
		-d "$(env_value POSTGRES_DB news)" -tAc "$1" 2>/dev/null | tr -d '\r'
}

# A bundle is everything needed to rebuild this stack somewhere else: the
# database as portable SQL, the deployment config, the environment file with
# the secrets, the media tree, the edge config, and a manifest that records
# what produced it. Volumes are not archived: a Postgres data directory is not
# portable across image versions, a pg_dump is.
cmd_backup() {
	require_compose
	mkdir -p backups
	local stamp name tmp dir file project git_sha git_branch git_dirty
	stamp="$(date -u +%Y%m%d-%H%M%S)"
	name="news-${ENV}-bundle-${stamp}"
	file="$ROOT_DIR/backups/${name}.tar.gz"
	project="$(compose_project)"
	tmp="$(mktemp -d)"
	dir="$tmp/$name"
	mkdir -p "$dir"/{config,env,media,ops}

	info "bringing postgres up for the dump"
	compose up -d postgres >/dev/null 2>&1 || true
	if ! wait_postgres 45; then
		err "postgres is not ready - backup aborted"
		rm -rf "$tmp"
		return 1
	fi

	info "dumping database (portable SQL)"
	if ! compose exec -T postgres sh -c \
		'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges' \
		2>"$tmp/pg_dump.err" | gzip -9 >"$dir/db.sql.gz"; then
		err "pg_dump failed:"
		tail -5 "$tmp/pg_dump.err" >&2
		rm -rf "$tmp"
		return 1
	fi
	if ! gzip -t "$dir/db.sql.gz" 2>/dev/null || [[ ! -s "$dir/db.sql.gz" ]]; then
		err "the database dump is empty or corrupt"
		rm -rf "$tmp"
		return 1
	fi

	info "collecting config, media and the edge definition"
	cp -a apps/api/config/. "$dir/config/"
	find "$dir/config" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	cp -a apps/web/public/. "$dir/media/" 2>/dev/null || true
	cp -a ops/nginx/. "$dir/ops/nginx/" 2>/dev/null || true
	cp -a "$ENV_FILE" "$dir/env/${ENV_FILE}"
	chmod 600 "$dir/env/${ENV_FILE}"

	git_sha="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
	git_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
	git_dirty=false
	[[ -n "$(git status --porcelain 2>/dev/null)" ]] && git_dirty=true

	local channels articles sources leads migration slugs_json
	channels="$(psql_value 'select count(*) from industries')"
	articles="$(psql_value 'select count(*) from articles')"
	sources="$(psql_value 'select count(*) from sources')"
	leads="$(psql_value 'select count(*) from leads')"
	migration="$(psql_value 'select coalesce(max(filename), $$none$$) from schema_migrations')"
	slugs_json="$(psql_value "select coalesce(json_agg(slug order by slug)::text, '[]') from industries")"
	[[ -n "$slugs_json" ]] || slugs_json="[]"

	cat >"$dir/manifest.json" <<EOF
{
  "format": 2,
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "source": {
    "env": "${ENV}",
    "compose_project": "${project}",
    "compose_file": "${COMPOSE_FILE}",
    "app_env": "$(env_value APP_ENV "$ENV")",
    "app_domain": "$(env_value APP_DOMAIN "")",
    "channel_domain": "$(channel_domain)",
    "default_industry": "$(default_slug)"
  },
  "git": { "sha": "${git_sha}", "branch": "${git_branch}", "dirty": ${git_dirty} },
  "database": {
    "dump": "db.sql.gz",
    "migration": "${migration}",
    "channels": ${channels:-0},
    "articles": ${articles:-0},
    "sources": ${sources:-0},
    "leads": ${leads:-0},
    "channel_slugs": ${slugs_json}
  },
  "members": ["db.sql.gz", "config/", "env/${ENV_FILE}", "media/", "ops/nginx/"],
  "restore": "gunzip -c db.sql.gz | psql; config/media/ops are staged, not applied, unless --all"
}
EOF

	info "writing checksums"
	(
		cd "$dir"
		find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum >SHA256SUMS
	)

	tar czf "$file" -C "$tmp" "$name"
	rm -rf "$tmp"
	chmod 600 "$file"
	ok "bundle written: $file ($(du -h "$file" | cut -f1))"
	info "channels ${channels:-?} · articles ${articles:-?} · sources ${sources:-?} · leads ${leads:-?} · migration ${migration:-?}"
	warn "the bundle contains secrets (env/${ENV_FILE}) - treat it like a credential"
	info "restore on the target with: ./bin/start.sh --env prd restore"
}

restore_bundle() {
	local archive="$1" apply_all="$2"
	local tmp="$3" base
	base="$(basename "$archive" .tar.gz)"
	info "extracting $base"
	tar xzf "$archive" -C "$tmp"
	local dir="$tmp/$base"
	if [[ ! -d "$dir" ]]; then
		# tolerate bundles that stored the directory with a different name
		dir="$(find "$tmp" -maxdepth 1 -mindepth 1 -type d | head -1)"
	fi
	if [[ ! -f "$dir/db.sql.gz" ]]; then
		err "bundle has no db.sql.gz"
		return 1
	fi

	info "verifying checksums"
	if ! (cd "$dir" && sha256sum -c --quiet SHA256SUMS 2>/dev/null); then
		err "checksum mismatch in $base - refusing to restore"
		return 1
	fi

	if [[ -f "$dir/manifest.json" ]]; then
		info "manifest: $(tr -d '\n' <"$dir/manifest.json" | sed -n 's/.*"migration": "\([^"]*\)".*/migration \1/p')"
	fi

	info "restoring the database (this replaces the current $ENV schema)"
	if ! gunzip -c "$dir/db.sql.gz" | compose exec -T postgres \
		psql -U "$(env_value POSTGRES_USER news)" -d "$(env_value POSTGRES_DB news)" \
		-v ON_ERROR_STOP=1 -q >/dev/null; then
		err "database restore failed"
		return 1
	fi

	local staged="backups/restored/$base"
	mkdir -p "$staged"
	[[ -d "$dir/config" ]] && cp -a "$dir/config" "$staged/config"
	[[ -d "$dir/media" ]] && cp -a "$dir/media" "$staged/media"
	[[ -d "$dir/ops" ]] && cp -a "$dir/ops" "$staged/ops"
	[[ -d "$dir/env" ]] && cp -a "$dir/env" "$staged/env"
	[[ -f "$dir/manifest.json" ]] && cp -a "$dir/manifest.json" "$staged/manifest.json"
	info "config, media, edge and env staged in $staged"

	if [[ "$apply_all" == "1" ]]; then
		[[ -d "$dir/config" ]] && cp -a "$dir/config/." apps/api/config/
		[[ -d "$dir/media" ]] && cp -a "$dir/media/." apps/web/public/
		[[ -d "$dir/ops/nginx" ]] && cp -a "$dir/ops/nginx/." ops/nginx/
		ok "config, media and nginx sites applied from the bundle"
	fi

	info "running migrations (the bundle may predate this checkout)"
	compose exec -T api python -m news_api.platform.migrations || warn "migrations failed - check ./bin/start.sh --env $ENV logs api"
	compose up -d >/dev/null 2>&1 || true
	wait_health 45 >/dev/null 2>&1 || true
	ok "restored $base"
}

restore_volumes() {
	local archive="$1"
	local project base members vol mounts=() name
	project="$(compose_project)"
	base="$(basename "$archive")"
	members="$(docker run --rm -v "$ROOT_DIR/backups:/backup" alpine:3.20 \
		tar tzf "/backup/$base" | sed 's#^\./##' | cut -d/ -f1 | sort -u | grep -E '^(pgdata|redisdata|caddy_data|caddy_config)$' || true)"
	if [[ -z "$members" ]]; then
		err "archive does not contain a recognized stack volume"
		return 1
	fi
	info "stopping api/worker/postgres/redis before restore"
	compose stop api worker postgres redis >/dev/null 2>&1 || true
	while IFS= read -r vol; do
		[[ -n "$vol" ]] || continue
		name="${project}_${vol}"
		docker volume create "$name" >/dev/null
		mounts+=("-v" "${name}:/volumes/${vol}")
	done <<<"$members"
	docker run --rm "${mounts[@]}" -v "$ROOT_DIR/backups:/backup" \
		-e "ARCHIVE=$base" alpine:3.20 sh -c '
			for dir in /volumes/*; do
				mkdir -p "$dir"
				find "$dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
			done
			tar xzf "/backup/$ARCHIVE" -C /volumes
		'
	compose up -d >/dev/null 2>&1 || true
	wait_health 45 >/dev/null 2>&1 || true
	ok "restored $archive"
}

cmd_restore() {
	require_compose
	local apply_all=0 apply_answer=""
	[[ "${TARGETS:-}" == *"--all"* ]] && apply_all=1

	local files=()
	# Bundles carry the environment they were taken from in their name: a
	# dev bundle restored on the production host is the normal migration path.
	while IFS= read -r f; do files+=("$f"); done < <(
		ls -1t backups/news-*-bundle-*.tar.gz backups/news-"${ENV}"-volumes-*.tar.gz 2>/dev/null || true
	)
	if [[ ${#files[@]} -eq 0 ]]; then
		err "no backups for $ENV in backups/"
		return 1
	fi

	local i=1 f
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

	if [[ $apply_all -eq 0 && -t 0 && "$(basename "$chosen")" == *-bundle-* ]]; then
		read -r -p "apply config, media and nginx sites from the bundle too? [y/N] " apply_answer
		[[ "$apply_answer" == "y" || "$apply_answer" == "Y" ]] && apply_all=1
	fi

	if [[ $ASSUME_YES -ne 1 ]]; then
		warn "this replaces the current $ENV database"
		read -r -p "type restore-${ENV} to confirm: " answer
		[[ "$answer" == "restore-${ENV}" ]] || {
			info "aborted"
			return 0
		}
	fi

	if [[ "$(basename "$chosen")" == *-bundle-* ]]; then
		compose up -d postgres >/dev/null 2>&1 || true
		wait_postgres 45 || {
			err "postgres is not ready"
			return 1
		}
		local tmp
		tmp="$(mktemp -d)"
		restore_bundle "$chosen" "$apply_all" "$tmp"
		local rc=$?
		rm -rf "$tmp"
		return $rc
	fi
	restore_volumes "$chosen"
}

cmd_destroy() {
	require_compose
	warn "this deletes the $ENV containers AND volumes (database, redis)"
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
	local domain
	domain="$(channel_domain || true)"
	if [[ -n "$domain" ]]; then
		printf 'channels:    \033[36m*.%s\033[0m\n' "$domain"
	else
		printf 'channels:    \033[33mpath mode (/%s...)\033[0m\n' "$(default_slug)"
	fi
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
10) backup    portable bundle (db + config + env + media)
11) restore   bundle (db; optional config/media/nginx)
12) domains   channel hosts + nginx sites
13) preflight production readiness checks
14) hosts     verify channel subdomain routing
15) certs     print the certbot command
16) init-env  create .env.<env> from .env.example
17) destroy   stop + delete volumes (typed confirm)
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
		12) SERVICE=""; cmd_domains ;;
		13) cmd_preflight ;;
		14) cmd_hosts ;;
		15) cmd_certs ;;
		16) init_env ;;
		17) cmd_destroy ;;
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
	--all | --write | --print | --http-only | --bootstrap | --check | --run | --dry-run)
		TARGETS="${TARGETS:-} $1"
		SERVICE="$1"
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
	menu | up | down | restart | status | logs | shell | test | migrate | refresh | industry | domains | certs | hosts | preflight | backup | restore | init-env | destroy)
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
industry) cmd_industry ;;
domains) cmd_domains ;;
certs) cmd_certs ;;
hosts) cmd_hosts ;;
preflight) cmd_preflight ;;
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
