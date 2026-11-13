#!/bin/sh
# Apply database migrations before starting the API when a database is configured.
set -e

if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

exec "$@"
