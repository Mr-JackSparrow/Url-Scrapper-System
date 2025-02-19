#!/bin/bash
set -e

# Start Celery worker
echo "Starting Celery worker..."
celery -A src.core.celerySetup.celeryApp worker --loglevel=info &
CELERY_PID=$!

# Start FastAPI using uvicorn
echo "Starting FastAPI application..."
uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} &
UVICORN_PID=$!

# Trap SIGTERM and SIGINT to gracefully stop processes
trap "echo 'Stopping processes...'; kill $CELERY_PID $UVICORN_PID; wait $CELERY_PID $UVICORN_PID" SIGTERM SIGINT

# Wait for both processes to finish
wait $CELERY_PID $UVICORN_PID