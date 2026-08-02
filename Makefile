.PHONY: help install dev stop clean test lint format migrate seed docker-build docker-up docker-down

# Default target
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================
# Development
# =============================================

install: ## Install all dependencies
	cd apps/api && pip install -e ".[dev]"
	cd apps/ai-service && pip install -e ".[dev]"
	cd apps/web && npm install

dev: ## Start all services in development mode
	docker-compose up -d postgres neo4j qdrant redis
	@echo "Waiting for databases to be ready..."
	@sleep 5
	cd apps/api && alembic upgrade head
	@echo "Starting API service..."
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting AI service..."
	cd apps/ai-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
	@echo "Starting web frontend..."
	cd apps/web && npm run dev
	@echo "All services started!"

stop: ## Stop all running services
	-pkill -f "uvicorn app.main:app"
	docker-compose stop

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	cd apps/web && rm -rf .next out node_modules/.cache

# =============================================
# Testing
# =============================================

test: ## Run all tests
	cd apps/api && pytest tests/ -v --tb=short
	cd apps/ai-service && pytest tests/ -v --tb=short
	cd apps/web && npm test

test-api: ## Run API tests only
	cd apps/api && pytest tests/ -v --tb=short

test-unit: ## Run unit tests only
	cd apps/api && pytest tests/unit/ -v --tb=short

test-integration: ## Run integration tests only
	cd apps/api && pytest tests/integration/ -v --tb=short

test-e2e: ## Run end-to-end tests only
	cd apps/api && pytest tests/e2e/ -v --tb=short

test-ai: ## Run AI service tests only
	cd apps/ai-service && pytest tests/ -v --tb=short

test-web: ## Run frontend tests only
	cd apps/web && npm test

test-cov: ## Run tests with coverage
	cd apps/api && pytest tests/ -v --cov=app --cov-report=html --cov-report=term --cov-fail-under=70
	cd apps/ai-service && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# =============================================
# Linting & Formatting
# =============================================

lint: ## Run all linters
	cd apps/api && ruff check . && mypy app/
	cd apps/ai-service && ruff check . && mypy app/
	cd apps/web && npm run lint

format: ## Format all code
	cd apps/api && ruff format . && ruff check --fix .
	cd apps/ai-service && ruff format . && ruff check --fix .
	cd apps/web && npm run format

# =============================================
# Database
# =============================================

migrate: ## Run database migrations
	cd apps/api && alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	cd apps/api && alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	cd apps/api && alembic downgrade -1

seed: ## Seed the database
	cd apps/api && python -m app.database.seed

# =============================================
# Docker
# =============================================

docker-build: ## Build all Docker images
	docker-compose build

docker-up: ## Start all services with Docker
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-prod: ## Start all services in production mode
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

docker-prod-down: ## Stop production services
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-ps: ## Show running containers
	docker-compose ps

# =============================================
# Frontend
# =============================================

web-install: ## Install frontend dependencies
	cd apps/web && npm install

web-build: ## Build frontend for production
	cd apps/web && npm run build

web-dev: ## Start frontend dev server
	cd apps/web && npm run dev

# =============================================
# Utilities
# =============================================

backup: ## Backup all databases
	@bash scripts/backup.sh

restore: ## Restore databases from backup (usage: make restore DIR=./backups/20260802_120000)
	@bash scripts/restore.sh $(DIR)

shell-api: ## Open Python shell in API context
	cd apps/api && python -c "from app.main import app; print('API app loaded successfully')"

health-check: ## Check all services health
	@echo "Checking API..."
	@curl -s http://localhost:8000/health || echo "API: NOT RUNNING"
	@echo ""
	@echo "Checking AI Service..."
	@curl -s http://localhost:8001/health || echo "AI Service: NOT RUNNING"
	@echo ""
	@echo "Checking Frontend..."
	@curl -s http://localhost:3000 || echo "Frontend: NOT RUNNING"

generate-types: ## Generate TypeScript types from API schemas
	cd apps/api && python -m app.scripts.generate_types > ../web/lib/types/api.ts
