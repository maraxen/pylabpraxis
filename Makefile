.PHONY: docs lint format test db-test db-test-down check clear-pyc

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

test:
	uv run pytest

db-test:
	docker compose -f docker-compose.test.yml up -d

db-test-down:
	docker compose -f docker-compose.test.yml down

clear-pyc:
	find . -name "*.pyc" | xargs rm
	find . -name "*__pycache__" | xargs rm -r
