#!/bin/sh

# Start Celery worker
celery -A src.worker worker --loglevel=info &

# Start FastAPI using uvicorn
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
