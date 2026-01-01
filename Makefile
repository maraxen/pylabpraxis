.PHONY: docs clean-docs lint format check test test-fast test-parallel test-parallel-fast test-unit test-integration test-slow test-cov test-cov-parallel test-durations test-lf test-monitor db-test db-test-down db-test-down-clean dev-up dev-down dev-ephemeral dev-ephemeral-down dev-down-clean docker-prune docker-prune-all docker-stats clear-pyc frontend frontend-dev frontend-browser test-db test-scheduler test-db-custom

docs:
	uv run sphinx-build -b html docs docs/build/ -j 1 -W

clean-docs:
	rm -rf docs/build
	rm -rf docs/_autosummary

lint:
	uv run ruff check .

format:
	uv run ruff check . --fix
	uv run ruff format .

check: lint
	uv run pyright

# Test commands - see docs/TESTING.md for more information

test:
	@echo "Running all tests..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest

test-fast:
	@echo "Running fast tests only (skipping slow tests)..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest -m "not slow"

test-parallel:
	@echo "Running tests in parallel across all CPU cores..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest -n auto

test-parallel-fast:
	@echo "Running fast tests in parallel..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest -n auto -m "not slow"

test-unit:
	@echo "Running unit tests only..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest -m unit

test-integration:
	@echo "Running integration tests..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest -m integration

test-slow:
	@echo "Running slow tests only..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest -m slow

test-cov:
	@echo "Running tests with coverage report..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest --cov=praxis --cov-report=html --cov-report=term-missing

test-cov-parallel:
	@echo "Running tests in parallel with coverage..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest -n auto --cov=praxis --cov-report=html --cov-report=term-missing

test-durations:
	@echo "Finding the 20 slowest tests..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest --durations=20

test-lf:
	@echo "Running tests that failed last time..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest --lf

test-monitor:
	@echo "Running tests with performance monitoring..."
	PYTHONDONTWRITEBYTECODE=1 uv run pytest --monitor

db-test:
	docker compose -f docker-compose.test.yml up -d

db-test-down:
	docker compose -f docker-compose.test.yml down --remove-orphans

# Development services (full stack with persistent volumes)
dev-up:
	docker compose up -d

dev-down:
	docker compose down --remove-orphans

# Ephemeral development - uses tmpfs, no disk storage, auto-cleanup
dev-ephemeral:
	@echo "Starting ephemeral dev stack (data in RAM, auto-deleted on stop)..."
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-ephemeral-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans

# Clean shutdown - removes volumes (DELETES ALL DATA)
dev-down-clean:
	docker compose down -v --remove-orphans
	@echo "Volumes removed. All development data has been deleted."

db-test-down-clean:
	docker compose -f docker-compose.test.yml down -v --remove-orphans

# Docker cleanup commands
docker-prune:
	@echo "Removing unused Docker resources..."
	docker system prune -f
	@echo "Done. Run 'make docker-prune-all' to also remove unused volumes."

docker-prune-all:
	@echo "WARNING: This will remove ALL unused Docker resources including volumes!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker system prune -af --volumes
	@echo "Done."

docker-stats:
	@echo "=== Docker Disk Usage ==="
	docker system df
	@echo ""
	@echo "=== Volumes ==="
	docker volume ls
	@echo ""
	@echo "=== Running Containers ==="
	docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Size}}"

clear-pyc:
	find . -name "*.pyc" | xargs rm -f 2>/dev/null || true
	find . -name "*__pycache__" | xargs rm -rf 2>/dev/null || true

# Frontend development
frontend:
	@echo "Starting Angular frontend..."
	cd praxis/web-client && npm start

frontend-dev:
	@echo "Starting frontend with ephemeral Docker (auto-cleanup on exit)..."
	./scripts/dev-frontend.sh

frontend-browser:
	@echo "Starting frontend in browser-only mode (no backend required)..."
	cd praxis/web-client && npm run start:browser

# Tests requiring database (uses ephemeral Docker, auto-cleanup)
test-db:
	@echo "Running all tests with ephemeral database..."
	./scripts/test-with-db.sh

test-scheduler:
	@echo "Running scheduler and reservation tests..."
	./scripts/test-with-db.sh \
		tests/core/test_scheduler.py \
		tests/services/test_scheduler_service.py \
		tests/api/test_scheduler_api.py \
		tests/models/test_orm/test_asset_reservation_orm.py \
		-v

test-db-custom:
	@echo "Usage: ./scripts/test-with-db.sh <pytest args>"
	@echo "Example: ./scripts/test-with-db.sh tests/services/ -v -k scheduler"
