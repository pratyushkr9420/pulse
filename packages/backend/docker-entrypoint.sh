#!/bin/bash
set -e

echo "Starting Pulse Backend..."

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    echo "Waiting for $service_name to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo "✓ $service_name is ready"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "ERROR: $service_name failed to become ready after $max_attempts attempts"
    return 1
}

# Wait for required services
wait_for_service "${POSTGRES_HOST:-postgres}" "${POSTGRES_PORT:-5432}" "PostgreSQL"
wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"
wait_for_service "${QDRANT_HOST:-qdrant}" "${QDRANT_PORT:-6333}" "Qdrant"

# Function to verify migration success
verify_migrations() {
    echo "Verifying database schema..."
    uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys
import os

async def verify():
    try:
        db_url = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://stocknews:stocknews@localhost:5432/stocknews')
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            # Check for required tables
            result = await conn.execute(text(\"SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'chat_history')\"))
            tables = [row[0] for row in result]

            if len(tables) != 2:
                print(f'ERROR: Expected 2 tables (users, chat_history), found {len(tables)}: {tables}', file=sys.stderr)
                sys.exit(1)

            # Check alembic_version table has entry
            result = await conn.execute(text(\"SELECT version_num FROM alembic_version\"))
            versions = [row[0] for row in result]

            if len(versions) == 0:
                print('ERROR: alembic_version table is empty - migration state inconsistent', file=sys.stderr)
                sys.exit(1)

            print(f'✓ Database schema verified: users and chat_history tables exist')
            print(f'✓ Migration version: {versions[0]}')
        await engine.dispose()
    except Exception as e:
        print(f'ERROR: Database verification failed: {e}', file=sys.stderr)
        sys.exit(1)

asyncio.run(verify())
" || {
    echo "ERROR: Migration verification failed - refusing to start server with incomplete database schema"
    exit 1
}
}

# Run database migrations
echo "Running database migrations..."
if ! uv run alembic upgrade head; then
    echo "ERROR: Database migration failed - check database connection and migration files"
    exit 1
fi

# Verify migrations created expected tables
verify_migrations

# Automatic conditional data ingestion
echo "Checking if data ingestion is needed..."
uv run python scripts/check_and_ingest.py || {
    echo "WARNING: Automated data ingestion encountered an issue"
    echo "The server will start, but you may need to manually run: uv run python scripts/ingest_data.py"
}

# Start the application
echo "Starting uvicorn server..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
