# Praxis Development Commands

# Generate the browser-mode SQLite database using pre-discovered backends and protocols
generate-db:
	uv run --with pylibftdi scripts/generate_browser_db.py

# Run frontend tests
test:
	bunx vitest

# Run tests for changed files
test-changed:
	bunx vitest --changed

# Run linter
lint:
	bun run lint

# Build production bundle
build:
	bun run build

