# Development Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Git

## Getting Started

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/plant-intelligence-platform.git
cd plant-intelligence-platform
cp .env.example .env
```

### 2. Start Infrastructure

```bash
docker-compose up -d postgres neo4j qdrant redis
```

### 3. Setup API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### 4. Setup AI Service

```bash
cd apps/ai-service
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8001
```

### 5. Setup Frontend

```bash
cd apps/web
npm install
npm run dev
```

## Development Workflow

### Creating a New Module

1. Create directory structure under `apps/api/app/modules/{name}/`:
   ```
   {name}/
   ├── domain/
   │   ├── models.py
   │   ├── use_cases.py
   │   └── interfaces.py
   ├── infrastructure/
   │   └── repositories.py
   ├── api/
   │   ├── router.py
   │   └── schemas.py
   └── tasks.py
   ```

2. Add router to `app/main.py`
3. Create Alembic migration
4. Add tests

### Running Tests

```bash
# All tests
make test

# Specific module
cd apps/api && pytest tests/unit/test_auth.py -v

# With coverage
make test-cov
```

### Code Quality

```bash
# Lint
make lint

# Format
make format
```

## Database Migrations

```bash
# Create migration
cd apps/api
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `NEO4J_URI`: Neo4j bolt URI
- `QDRANT_URL`: Qdrant HTTP URL
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key
- `JWT_SECRET_KEY`: Secret for JWT signing
