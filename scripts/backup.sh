#!/usr/bin/env bash
set -euo pipefail

# =============================================
# Plant Intelligence Platform - Database Backup
# =============================================
# Usage: ./scripts/backup.sh [output_dir]
#
# Backs up PostgreSQL, Neo4j, Qdrant, and Redis.
# Output: timestamped directories under output_dir (default: ./backups)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${1:-$PROJECT_DIR/backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$OUTPUT_DIR/$TIMESTAMP"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[BACKUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
fi

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-pip}"
POSTGRES_DB="${POSTGRES_DB:-pip}"

NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4j_password}"

mkdir -p "$BACKUP_DIR"

# ---------------------------------------------
# PostgreSQL
# ---------------------------------------------
log "Backing up PostgreSQL..."
if command -v pg_dump &> /dev/null; then
    pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
        -Fc --no-owner --no-privileges \
        -f "$BACKUP_DIR/postgres.dump" 2>/dev/null || warn "pg_dump failed (using docker fallback)"
fi

# Docker fallback
if ! command -v pg_dump &> /dev/null || [ $? -ne 0 ]; then
    docker compose -f "$PROJECT_DIR/docker-compose.yml" exec -T postgres \
        pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-privileges \
        > "$BACKUP_DIR/postgres.dump" 2>/dev/null || warn "PostgreSQL backup failed"
fi

if [ -f "$BACKUP_DIR/postgres.dump" ]; then
    log "  PostgreSQL: $(du -h "$BACKUP_DIR/postgres.dump" | cut -f1)"
else
    warn "  PostgreSQL backup not created"
fi

# ---------------------------------------------
# Neo4j (cypher export)
# ---------------------------------------------
log "Backing up Neo4j..."
NEO4J_CONTAINER=$(docker compose -f "$PROJECT_DIR/docker-compose.yml" ps -q neo4j 2>/dev/null || echo "")
if [ -n "$NEO4J_CONTAINER" ]; then
    docker exec "$NEO4J_CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" \
        "CALL apoc.export.cypher.all('/tmp/neo4j-export.cypher')" 2>/dev/null \
        && docker cp "$NEO4J_CONTAINER":/tmp/neo4j-export.cypher "$BACKUP_DIR/neo4j.cypher" 2>/dev/null \
        || warn "  Neo4j export failed (no APOC plugin?)"
fi

if [ -f "$BACKUP_DIR/neo4j.cypher" ]; then
    log "  Neo4j: $(du -h "$BACKUP_DIR/neo4j.cypher" | cut -f1)"
else
    warn "  Neo4j backup not created (APOC not available)"
fi

# ---------------------------------------------
# Qdrant
# ---------------------------------------------
log "Backing up Qdrant..."
QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
if curl -sf "$QDRANT_URL/collections" > /dev/null 2>&1; then
    curl -s "$QDRANT_URL/collections" | python3 -m json.tool > "$BACKUP_DIR/qdrant_collections.json" 2>/dev/null || true
    log "  Qdrant: collection list exported"
else
    warn "  Qdrant not reachable"
fi

# ---------------------------------------------
# Redis
# ---------------------------------------------
log "Backing up Redis..."
REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
if command -v redis-cli &> /dev/null; then
    redis-cli -u "$REDIS_URL" BGSAVE 2>/dev/null || true
    sleep 2
    docker compose -f "$PROJECT_DIR/docker-compose.yml" exec -T redis \
        redis-cli BGSAVE > /dev/null 2>&1 || true
fi

# ---------------------------------------------
# Summary
# ---------------------------------------------
echo ""
log "============================================="
log "Backup complete: $BACKUP_DIR"
log "============================================="
echo ""
ls -la "$BACKUP_DIR"
echo ""
log "To restore: ./scripts/restore.sh $BACKUP_DIR"
