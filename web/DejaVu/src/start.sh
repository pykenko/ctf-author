#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTANCER_DIR="$SCRIPT_DIR/instancer"
ADMIN_TOKEN_FILE="$INSTANCER_DIR/.admin-token"

# Stop the old direct challenge deployment if this template was run before.
PUBLIC_PORT="${PUBLIC_PORT:-1}" COMPOSE_PROJECT_NAME=dejavu docker compose down -v --remove-orphans >/dev/null 2>&1 || true

if [ -z "${INSTANCER_ADMIN_TOKEN:-}" ]; then
    if [ ! -f "$ADMIN_TOKEN_FILE" ]; then
        {
            cat /proc/sys/kernel/random/uuid
            cat /proc/sys/kernel/random/uuid
        } | tr -d '\n-' > "$ADMIN_TOKEN_FILE"
        chmod 600 "$ADMIN_TOKEN_FILE"
    fi
    export INSTANCER_ADMIN_TOKEN="$(cat "$ADMIN_TOKEN_FILE")"
fi

export CTFD_BASE_URL="${CTFD_BASE_URL:-http://103.185.52.173/}"
export INSTANCE_HOST="${INSTANCE_HOST:-103.152.242.110}"
export PUBLIC_SCHEME="${PUBLIC_SCHEME:-http}"
export INSTANCER_BIND="${INSTANCER_BIND:-0.0.0.0}"
export INSTANCER_HOST="${INSTANCER_HOST:-0.0.0.0}"
export INSTANCER_PORT="${INSTANCER_PORT:-9000}"
export DEJAVU_STATE_DIR="${DEJAVU_STATE_DIR:-$INSTANCER_DIR/state}"
export INSTANCE_TTL_SECONDS="${INSTANCE_TTL_SECONDS:-1200}"
export MAX_INSTANCE_TTL_SECONDS="${MAX_INSTANCE_TTL_SECONDS:-1200}"
export CLEANUP_INTERVAL_SECONDS="${CLEANUP_INTERVAL_SECONDS:-60}"
export REQUIRE_TEAM="${REQUIRE_TEAM:-1}"

cd "$SCRIPT_DIR"
COMPOSE_PROJECT_NAME=dejavu-instancer docker compose -f instancer-compose.yml up --build --force-recreate -d

echo "DejaVu instancer bound on ${INSTANCER_BIND}:${INSTANCER_PORT}"
echo "Admin token saved at $ADMIN_TOKEN_FILE"
