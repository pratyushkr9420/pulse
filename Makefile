.PHONY: dev dev-frontend dev-backend db-migrate db-seed db-reset ingest test test-unit test-int test-e2e test-llm coverage lint lint-fix type-check docker-build docker-up docker-down clean clean-docker

# =============================================================================
# DEVELOPMENT
# =============================================================================

dev:
	docker-compose -f docker/docker-compose.yml up -d
	@echo "Services started. Frontend: http://localhost:3000, Backend: http://localhost:8000"

dev-frontend:
	cd packages/frontend && npm run dev

dev-backend:
	cd packages/backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# =============================================================================
# DATABASE
# =============================================================================

db-migrate:
	cd packages/backend && uv run alembic upgrade head

db-seed:
	cd packages/backend && uv run python scripts/seed_db.py

db-reset:
	cd packages/backend && uv run alembic downgrade base && uv run alembic upgrade head

# =============================================================================
# DATA INGESTION
# =============================================================================

ingest:
	cd packages/backend && uv run python scripts/ingest_data.py

# =============================================================================
# TESTING
# =============================================================================

test: test-unit test-int

test-unit:
	cd packages/frontend && npm run test:unit -- --run
	cd packages/backend && uv run pytest tests/unit -v

test-int:
	cd packages/backend && uv run pytest tests/integration -v

test-e2e:
	cd packages/frontend && npm run test:e2e
	cd packages/backend && uv run pytest tests/e2e -v

test-llm:
	cd packages/backend && uv run pytest tests/llm_evaluation -v

coverage:
	cd packages/frontend && npm run test:unit -- --coverage
	cd packages/backend && uv run pytest tests/unit --cov=src --cov-report=html

# =============================================================================
# LINTING & TYPE CHECKING
# =============================================================================

lint:
	cd packages/frontend && npm run lint
	cd packages/backend && uv run ruff check src

lint-fix:
	cd packages/frontend && npm run lint -- --fix
	cd packages/backend && uv run ruff check src --fix

type-check:
	cd packages/frontend && npx tsc --noEmit
	cd packages/backend && uv run mypy src

# =============================================================================
# DOCKER
# =============================================================================

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

# =============================================================================
# CLEANUP
# =============================================================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true

clean-docker:
	docker-compose -f docker/docker-compose.yml down -v
