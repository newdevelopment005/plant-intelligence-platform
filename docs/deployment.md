# Deployment Guide

Complete guide for deploying the Plant Intelligence Platform.

## Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.12+ (for local dev)
- Node.js 20+ (for local dev)
- PostgreSQL 16+ (if running locally)

## Quick Deploy (Docker)

```bash
# 1. Clone and configure
git clone https://github.com/your-org/plant-intelligence-platform.git
cd plant-intelligence-platform
cp .env.example .env
# Edit .env with production values

# 2. Start all services
docker compose up -d

# 3. Verify
docker compose ps
curl http://localhost:8000/health
```

## Production Deploy

Use the production override file for hardened settings:

```bash
# Build and start with production config
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Or use Make
make docker-prod
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Application secret key |
| `JWT_SECRET_KEY` | Yes | - | JWT signing key |
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `NEO4J_PASSWORD` | No | `neo4j_password` | Neo4j password |
| `REDIS_PASSWORD` | No | - | Redis password |
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000/api/v1` | API URL for frontend |
| `NEXTAUTH_URL` | No | `http://localhost:3000` | Auth callback URL |

### Generate Secure Keys

```bash
# Generate a random hex key
openssl rand -hex 32

# Use for SECRET_KEY, JWT_SECRET_KEY
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| `web` | 3000 | Next.js frontend |
| `api` | 8000 | FastAPI backend |
| `ai-service` | 8001 | AI microservice |
| `nginx` | 80, 443 | Reverse proxy |
| `postgres` | 5432 | PostgreSQL database |
| `neo4j` | 7474, 7687 | Graph database |
| `qdrant` | 6333, 6334 | Vector database |
| `redis` | 6379 | Cache/queue |

## Database Management

### Migrations

```bash
# Apply migrations
make migrate

# Create new migration
make migrate-create MSG="add new table"

# Rollback
make migrate-down
```

### Backup & Restore

```bash
# Backup all databases
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh ./backups/20260802_120000
```

## CI/CD

### GitHub Actions

- **ci.yml**: Runs on PRs and pushes to `main`
  - Linting (Ruff, MyPy, ESLint)
  - Unit tests with coverage
  - Docker build verification

- **deploy.yml**: Runs on push to `main`
  - Frontend deploy to Vercel
  - Backend deploy (configure for your infrastructure)

### Custom Deployment

```bash
# Build images
make docker-build

# Tag for registry
docker tag pip-api:latest registry.example.com/pip-api:latest
docker push registry.example.com/pip-api:latest
```

## Monitoring

### Health Checks

```bash
# Manual check
make health-check

# API health endpoint
curl http://localhost:8000/health

# AI service health
curl http://localhost:8001/health
```

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f ai-service

# Tail last 100 lines
docker compose logs --tail 100 api
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is ready
docker compose exec postgres pg_isready -U pip

# Reset database (WARNING: destroys data)
docker compose down -v
docker compose up -d postgres
make migrate
make seed
```

### AI Service Slow Startup

The AI service downloads embedding models on first start. Pre-cache:

```bash
docker compose up -d ai-service
# Wait for model download
docker compose logs -f ai-service
```

### Memory Issues

Production resource limits (in `docker-compose.prod.yml`):
- API: 2GB RAM, 2 CPU
- AI Service: 4GB RAM, 4 CPU
- PostgreSQL: 2GB RAM, 2 CPU

Adjust in production override if needed.

## SSL/TLS

1. Place certificates in `infrastructure/nginx/ssl/`
2. Update `infrastructure/nginx/nginx.conf` for HTTPS
3. Uncomment port 443 in docker-compose.yml

```bash
# Self-signed cert (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout infrastructure/nginx/ssl/key.pem \
    -out infrastructure/nginx/ssl/cert.pem
```

## Scaling

```bash
# Scale API workers
docker compose up -d --scale api=3

# Scale Celery workers
docker compose up -d --scale celery-worker=4
```

Note: Use a load balancer (nginx is configured) when scaling horizontally.
