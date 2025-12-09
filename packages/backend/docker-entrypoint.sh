#!/bin/bash
set -e

echo "Starting Pulse Backend..."

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
