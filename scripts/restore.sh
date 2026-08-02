#!/usr/bin/env bash
set -euo pipefail

# =============================================
# Plant Intelligence Platform - Database Restore
# =============================================
# Usage: ./scripts/restore.sh <backup_dir>
#
# Restores PostgreSQL and Neo4j from a backup directory
# created by backup.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[RESTORE]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

if [ -z "${1:-}" ]; then
    error "Usage: $0 <backup_dir>"
fi

BACKUP_DIR="$1"
[ -d "$BACKUP_DIR" ] || error "Backup directory not found: $BACKUP_DIR"

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
fi

POSTGRES_USER="${POSTGRES_USER:-pip}"
POSTGRES_DB="${POSTGRES_DB:-pip}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4j_password}"

log "Restoring from: $BACKUP_DIR"
echo ""

# ---------------------------------------------
# PostgreSQL
# ---------------------------------------------
if [ -f "$BACKUP_DIR/postgres.dump" ]; then
    log "Restoring PostgreSQL..."
    read -p "This will DROP and recreate the '$POSTGRES_DB' database. Continue? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres \
            psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $POSTGRES_DB;" 2>/dev/null || true
        docker compose -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres \
            psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB;" 2>/dev/null || true
        docker compose -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres \
            pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges --clean \
            < "$BACKUP_DIR/postgres.dump" 2>/dev/null || warn "pg_restore had warnings (usually OK)"
        log "  PostgreSQL restored"
    else
        warn "  PostgreSQL restore skipped"
    fi
else
    warn "No PostgreSQL dump found in $BACKUP_DIR"
fi

# ---------------------------------------------
# Neo4j
# ---------------------------------------------
if [ -f "$BACKUP_DIR/neo4j.cypher" ]; then
    log "Restoring Neo4j..."
    read -p "This will overwrite all Neo4j data. Continue? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        NEO4J_CONTAINER=$(docker compose -f "$PROJECT_DIR/docker-compose.yml" ps -q neo4j 2>/dev/null || echo "")
        if [ -n "$NEO4J_CONTAINER" ]; then
            docker cp "$BACKUP_DIR/neo4j.cypher" "$NEO4J_CONTAINER":/tmp/neo4j-restore.cypher
            docker exec "$NEO4J_CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" \
                -f /tmp/neo4j-restore.cypher 2>/dev/null || warn "  Neo4j restore had warnings"
            log "  Neo4j restored"
        else
            warn "  Neo4j container not running"
        fi
    else
        warn "  Neo4j restore skipped"
    fi
else
    warn "No Neo4j export found in $BACKUP_DIR"
fi

echo ""
log "Restore complete."
log "Run 'make migrate' to ensure schema is up to date."
