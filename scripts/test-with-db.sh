#!/bin/bash
# Run tests that require PostgreSQL using ephemeral Docker stack
# Usage: ./scripts/test-with-db.sh [pytest args...]
# Example: ./scripts/test-with-db.sh tests/core/test_scheduler.py -v

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[test-db]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[test-db]${NC} $1"; }
log_error() { echo -e "${RED}[test-db]${NC} $1"; }

# Check if Docker daemon is running, start if needed
ensure_docker_running() {
    if docker info > /dev/null 2>&1; then
        log_info "Docker daemon is running."
        return 0
    fi

    log_warn "Docker daemon is not running."

    # macOS: Try to start Docker Desktop
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -d "/Applications/Docker.app" ]; then
            log_info "Starting Docker Desktop..."
            open -a Docker

            # Wait for Docker to be ready (up to 60 seconds)
            log_info "Waiting for Docker to start (this may take a moment)..."
            for i in {1..60}; do
                if docker info > /dev/null 2>&1; then
                    log_info "Docker is ready!"
                    return 0
                fi
                echo -n "."
                sleep 1
            done
            echo ""
            log_error "Docker failed to start within 60 seconds."
            log_error "Please start Docker Desktop manually and try again."
            exit 1
        else
            log_error "Docker Desktop not found at /Applications/Docker.app"
            log_error "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
            exit 1
        fi
    # Linux: Try to start docker service
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Attempting to start Docker service..."
        if command -v systemctl > /dev/null 2>&1; then
            sudo systemctl start docker || {
                log_error "Failed to start Docker. Try: sudo systemctl start docker"
                exit 1
            }
            sleep 2
            if docker info > /dev/null 2>&1; then
                log_info "Docker is ready!"
                return 0
            fi
        else
            log_error "Please start Docker daemon manually: sudo dockerd"
            exit 1
        fi
    else
        log_error "Unsupported OS. Please start Docker manually."
        exit 1
    fi
}

# Compose file for test services (just PostgreSQL + Redis)
COMPOSE_FILE="docker-compose.test-services.yml"

# Cleanup function
cleanup() {
    echo ""
    log_info "Cleaning up Docker containers..."
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
    log_info "Done."
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Ensure Docker is running
ensure_docker_running

# Start test services (PostgreSQL + Redis only)
log_info "Starting test services (PostgreSQL + Redis)..."
docker compose -f "$COMPOSE_FILE" up -d

# Wait for PostgreSQL to be ready
log_info "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker compose -f "$COMPOSE_FILE" exec -T praxis-db pg_isready -U praxis -d praxis_db > /dev/null 2>&1; then
        log_info "PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "PostgreSQL failed to become ready in time"
        exit 1
    fi
    echo -n "."
    sleep 1
done

# Wait for Redis
log_info "Waiting for Redis to be ready..."
for i in {1..15}; do
    if docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_info "Redis is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        log_warn "Redis not responding (tests may still work)"
        break
    fi
    echo -n "."
    sleep 1
done

# Set environment variables for tests
export DATABASE_URL="postgresql+asyncpg://praxis:praxis@localhost:5433/praxis_db"
export REDIS_URL="redis://localhost:6379/0"
export TEST_DATABASE_URL="$DATABASE_URL"

# Run pytest with provided arguments (or default to scheduler tests)
if [ $# -eq 0 ]; then
    log_info "Running scheduler and reservation tests..."
    PYTHONDONTWRITEBYTECODE=1 uv run pytest \
        tests/core/test_scheduler.py \
        tests/services/test_scheduler_service.py \
        tests/api/test_scheduler_api.py \
        tests/models/test_orm/test_asset_reservation_orm.py \
        -v --tb=short
else
    log_info "Running: pytest $@"
    PYTHONDONTWRITEBYTECODE=1 uv run pytest "$@"
fi
