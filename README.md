# Plant Intelligence Platform

[![CI](https://github.com/your-org/plant-intelligence-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/plant-intelligence-platform/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Enterprise-grade AI-powered scientific research platform for plant science.

## Architecture

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python 3.12, SQLAlchemy, Alembic
- **AI Service**: LangGraph, LangChain, Sentence Transformers
- **Databases**: PostgreSQL, Neo4j, Qdrant, Redis
- **Deployment**: Docker, GitHub Actions, Vercel

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16+

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/plant-intelligence-platform.git
cd plant-intelligence-platform

# Copy environment variables
cp .env.example .env

# Start databases
docker-compose up -d postgres neo4j qdrant redis

# Install API dependencies
cd apps/api
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start API service
uvicorn app.main:app --reload --port 8000

# In another terminal - start AI service
cd apps/ai-service
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8001

# In another terminal - start frontend
cd apps/web
npm install
npm run dev
```

### Using Make

```bash
make help           # Show all available commands
make docker-up      # Start all services with Docker
make test           # Run all tests
make lint           # Run all linters
make migrate        # Run database migrations
```

## Project Structure

```
plant-intelligence-platform/
├── apps/
│   ├── web/                 # Next.js frontend
│   ├── api/                 # FastAPI backend
│   └── ai-service/          # AI microservice
├── packages/                # Shared packages
├── infrastructure/          # Nginx, Terraform, etc.
├── database/                # SQL schemas, seeds
├── tests/                   # Shared test utilities
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── .github/                 # CI/CD workflows
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Modules

| Phase | Module | Status |
|-------|--------|--------|
| 1 | Architecture & Repository Setup | Completed |
| 2 | Authentication & Authorization | Completed |
| 3 | Project Management | Completed |
| 4 | Germplasm Repository | Completed |
| 5 | Phenotyping | Completed |
| 6 | Genomics | Completed |
| 7 | Molecular Biology | Completed |
| 8 | Literature AI | Completed |
| 9 | Knowledge Graph | Completed |
| 10 | AI Research Assistant | Completed |
| 11 | Bioinformatics | Completed |
| 12 | Image Analysis | Completed |
| 13 | Reporting | Completed |
| 14 | Deployment | Completed |
| 15 | Testing | Completed |
| 16 | Documentation | Completed |
| 17 | Production Hardening | Completed |
| 18 | Final QA & Release | Completed |

## API Documentation

Once the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific module tests
cd apps/api && pytest tests/unit/test_auth.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.
