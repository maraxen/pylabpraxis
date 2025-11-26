#!/bin/bash
set -eux

# Check if the test_db container is running
if [ -z "$(sudo docker ps -q -f "name=test_db")" ]; then
    echo "Test database container is not running. Starting it..."
    sudo docker-compose -f docker-compose.test.yml up -d
else
    echo "Test database container is already running."
fi

# Wait for the database to be ready
echo "Waiting for database to be ready..."
until sudo docker exec test_db pg_isready -U test_user -d test_db; do
  echo "Database not ready yet..."
  sleep 2
done

echo "Database is ready. Running tests..."
uv run pytest "$@"
