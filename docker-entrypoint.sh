#!/bin/bash
set -e

echo "======================================"
echo "Octopus API - Starting Up"
echo "======================================"

# Wait a moment for any database connections to settle
sleep 2

# Run database migrations using uv
echo "Running database migrations..."
/app/.venv/bin/alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migration failed!"
    exit 1
fi

echo "======================================"
echo "Starting FastAPI application..."
echo "======================================"

# Start the application
exec /app/.venv/bin/fastapi run app/main.py --host 0.0.0.0 --port 80
