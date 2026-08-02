# Plant Intelligence Platform

[![CI](https://github.com/newdevelopment005/plant-intelligence-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/newdevelopment005/plant-intelligence-platform/actions/workflows/ci.yml)
[![Deploy](https://github.com/newdevelopment005/plant-intelligence-platform/actions/workflows/deploy.yml/badge.svg)](https://github.com/newdevelopment005/plant-intelligence-platform/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Enterprise-grade AI-powered scientific research platform for plant science.

## Live Demo

- **Frontend**: [pip-platform.vercel.app](https://pip-platform.vercel.app)
- **API Docs**: [api.pip-platform.org/docs](https://api.pip-platform.org/docs)
- **AI Service**: [pip-ai-service.hf.space](https://pip-ai-service.hf.space)

## Architecture

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.12, SQLAlchemy, Alembic
- **AI Service**: LangGraph, LangChain, Sentence Transformers
- **Databases**: PostgreSQL, Neo4j, Qdrant, Redis
- **Deployment**: Vercel (frontend), Docker (backend), Hugging Face Spaces (AI)

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16+

### Development Setup

```bash
# Clone the repository
git clone https://github.com/newdevelopment005/plant-intelligence-platform.git
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

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

**Frontend (Vercel)**
```bash
cd apps/web
vercel --prod
```

**AI Service (Hugging Face Spaces)**
```bash
cd apps/ai-service
huggingface-cli upload newdevelopment005/pip-ai-service . --repo-type space
```

**Backend (Docker)**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

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

## AI Capabilities

| Feature | Description |
|---------|-------------|
| Research Chat | Scientific Q&A with literature retrieval |
| Gene Recommendations | Evidence-based candidate gene suggestions |
| Experiment Design | Rigorous experimental protocol generation |
| Literature Search | PubMed-powered paper discovery |
| Paper Summarization | Automated literature synthesis |
| Image Analysis | Disease detection, phenotype measurement |
| Knowledge Graph | Entity relationships and inference |
| Statistical Guidance | Appropriate test recommendations |

## Security

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Rate limiting (100 req/min general, 30 req/min AI)
- Security headers (XSS, CSRF, clickjacking protection)
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/newdevelopment005/plant-intelligence-platform/issues)
- Security: [SECURITY.md](SECURITY.md)
