# DEPLOYMENT.md

## Plant Intelligence Platform - Production Deployment Guide

### Overview

| Service | Platform | URL Pattern |
|---------|----------|-------------|
| Frontend | Vercel | `https://pip-platform.vercel.app` |
| API Backend | Docker / Cloud | `https://api.pip-platform.org` |
| AI Service | Hugging Face Spaces | `https://pip-ai-service.hf.space` |
| PostgreSQL | Supabase / AWS RDS | Managed |
| Neo4j | Neo4j Aura | Managed |
| Redis | Upstash / AWS ElastiCache | Managed |
| Qdrant | Qdrant Cloud | Managed |

---

## 1. Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (https://vercel.com)
- GitHub repository connected

### Steps

1. **Connect repository to Vercel**
   - Go to https://vercel.com/new
   - Import `newdevelopment005/plant-intelligence-platform`
   - Set root directory to `apps/web`
   - Framework: Next.js (auto-detected)

2. **Configure environment variables**
   ```
   NEXT_PUBLIC_API_URL=https://api.pip-platform.org/api/v1
   NEXT_PUBLIC_AI_URL=https://ai.pip-platform.org/api/v1
   ```

3. **Deploy**
   - Automatic on every push to `master`
   - Manual: `cd apps/web && vercel --prod`

4. **Custom domain** (optional)
   - Add domain in Vercel dashboard
   - Update DNS records as instructed

### CLI Commands
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy preview
vercel

# Deploy production
vercel --prod
```

---

## 2. AI Service Deployment (Hugging Face Spaces)

### Prerequisites
- Hugging Face account (https://huggingface.co)
- HF Token with write access

### Steps

1. **Create a new Space**
   - Go to https://huggingface.co/new-space
   - Name: `pip-ai-service`
   - SDK: Docker
   - Hardware: CPU Basic (free) or GPU (for inference)

2. **Configure secrets** in Space Settings
   ```
   OPENAI_API_KEY=sk-...
   NEO4J_URI=bolt://...
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=...
   REDIS_URL=redis://...
   QDRANT_URL=http://...
   ```

3. **Deploy via GitHub Actions**
   - Add `HF_TOKEN` to repository secrets
   - Add `HF_USERNAME` to repository secrets
   - Push a tag: `git tag v1.0.0 && git push --tags`

4. **Manual deployment**
   ```bash
   cd apps/ai-service
   huggingface-cli login
   huggingface-cli upload YOUR_USERNAME/pip-ai-service . --repo-type space
   ```

### Space Configuration
- The `app.py` file serves as the entry point
- `requirements.txt` lists all dependencies
- `README.md` contains Space metadata

---

## 3. Backend Deployment (Docker)

### Prerequisites
- Docker and Docker Compose installed
- Server with ports 80, 443, 5432, 6379, 7474, 7687, 6333 open

### Quick Start

```bash
# Clone repository
git clone https://github.com/newdevelopment005/plant-intelligence-platform.git
cd plant-intelligence-platform

# Copy environment file
cp .env.production .env

# Edit with real values
nano .env

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Verify
docker-compose ps
curl http://localhost:8000/health
```

### Production Docker Compose
```bash
# Build and start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# View logs
docker-compose logs -f api
docker-compose logs -f ai-service

# Stop
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Cloud Deployment Options

#### AWS ECS
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag images
docker tag pip-api:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/pip-api:latest
docker tag pip-ai-service:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/pip-ai-service:latest

# Push
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/pip-api:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/pip-ai-service:latest
```

#### Google Cloud Run
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/pip-api ./apps/api
gcloud builds submit --tag gcr.io/PROJECT-ID/pip-ai-service ./apps/ai-service

# Deploy
gcloud run deploy pip-api --image gcr.io/PROJECT-ID/pip-api --platform managed
gcloud run deploy pip-ai-service --image gcr.io/PROJECT-ID/pip-ai-service --platform managed
```

---

## 4. Database Setup

### PostgreSQL
```bash
# Create database
docker-compose exec postgres psql -U pip -c "CREATE DATABASE pip;"

# Run migrations
cd apps/api
alembic upgrade head
```

### Neo4j
```bash
# Access Neo4j browser
open http://localhost:7474

# Default credentials: neo4j / neo4j_password
# Change password in production
```

### Qdrant
```bash
# Access Qdrant dashboard
open http://localhost:6333/dashboard
```

---

## 5. SSL/TLS Setup (Nginx)

### Using Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.pip-platform.org

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx Configuration
See `infrastructure/nginx/nginx.conf` for the full configuration.

---

## 6. Monitoring

### Health Endpoints
- API: `GET /health`
- AI Service: `GET /health`
- Frontend: `GET /api/health`

### Logs
```bash
# Docker logs
docker-compose logs -f --tail=100 api
docker-compose logs -f --tail=100 ai-service

# Structured JSON logs
docker-compose logs api | jq .
```

---

## 7. Backup & Restore

### Database Backup
```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U pip pip > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec postgres psql -U pip pip < backup_20260802.sql
```

### Automated Backups
```bash
# Cron job for daily backups
0 2 * * * cd /opt/pip && bash scripts/backup.sh
```

---

## 8. Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `SECRET_KEY` | Application secret | - |
| `JWT_SECRET_KEY` | JWT signing key | - |
| `DATABASE_URL` | PostgreSQL connection | - |
| `REDIS_URL` | Redis connection | - |
| `NEO4J_URI` | Neo4j bolt URL | - |
| `QDRANT_URL` | Qdrant HTTP URL | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `CORS_ORIGINS` | Allowed origins | `["http://localhost:3000"]` |

---

## 9. Troubleshooting

### Common Issues

**Migration fails**
```bash
# Check database connection
docker-compose exec api python -c "from app.database import engine; print(engine.url)"
```

**AI service OOM**
```bash
# Reduce model size or use GPU
# Edit config.py: EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

**CORS errors**
```bash
# Verify CORS_ORIGINS includes frontend URL
# Check Nginx config for proxy headers
```

---

## 10. Security Checklist

- [ ] All default passwords changed
- [ ] SECRET_KEY and JWT_SECRET_KEY are random 32+ char strings
- [ ] CORS_ORIGINS only includes trusted domains
- [ ] DEBUG=false in production
- [ ] SSL/TLS enabled for all endpoints
- [ ] Database ports not exposed to public internet
- [ ] Redis password set
- [ ] Neo4j password changed
- [ ] Environment variables not in code repository
- [ ] Regular dependency updates scheduled
