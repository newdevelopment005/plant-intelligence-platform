#!/usr/bin/env bash
set -euo pipefail

# =============================================
# Plant Intelligence Platform - Database Migration
# =============================================
# Usage: ./scripts/migrate.sh [command]
#
# Commands:
#   up       - Apply all pending migrations (default)
#   down     - Rollback last migration
#   status   - Show migration status
#   create   - Create new migration (requires MSG env var)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
API_DIR="$PROJECT_DIR/apps/api"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[MIGRATE]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

COMMAND="${1:-up}"

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
fi

cd "$API_DIR"

case "$COMMAND" in
    up)
        log "Applying database migrations..."
        alembic upgrade head
        log "Migrations applied successfully."
        ;;
    down)
        log "Rolling back last migration..."
        alembic downgrade -1
        log "Rollback complete."
        ;;
    status)
        log "Migration status:"
        alembic history --verbose
        ;;
    create)
        if [ -z "${MSG:-}" ]; then
            error "Usage: MSG='description' $0 create"
        fi
        log "Creating migration: $MSG"
        alembic revision --autogenerate -m "$MSG"
        log "Migration created. Review and edit the generated file before applying."
        ;;
    *)
        error "Unknown command: $COMMAND (use: up, down, status, create)"
        ;;
esac
