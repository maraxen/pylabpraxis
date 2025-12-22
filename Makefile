.PHONY: docs clean-docs lint format check test test-fast test-parallel test-parallel-fast test-unit test-integration test-slow test-cov test-cov-parallel test-durations test-lf test-monitor db-test db-test-down clear-pyc

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
	docker compose -f docker-compose.test.yml down

clear-pyc:
	find . -name "*.pyc" | xargs rm
	find . -name "*__pycache__" | xargs rm -r
