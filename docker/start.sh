#!/bin/bash
# MindMend Application Startup Script

set -e

echo "Starting MindMend Application..."

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h ${DATABASE_HOST:-localhost} -p ${DATABASE_PORT:-5432} -U ${DATABASE_USER:-mindmend_user}; do
    echo "Database is unavailable - sleeping"
    sleep 1
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
cd /app
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Start Redis if not already running
redis-server --daemonize yes --bind 0.0.0.0

# Create log directories
mkdir -p /var/log/mindmend

# Start Gunicorn with proper configuration
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers ${WORKERS:-2} \
    --worker-class sync \
    --max-requests ${MAX_REQUESTS:-10000} \
    --max-requests-jitter 100 \
    --timeout ${TIMEOUT:-120} \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --capture-output \
    --enable-stdio-inheritance \
    "app:app"