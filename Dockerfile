# Use an official Python image as the base
FROM python:3.11-slim AS base

# Set environment variables for better performance & logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    C_FORCE_ROOT=1

# Allow Celery to run as root (Comment placed outside ENV)

# Set a working directory
WORKDIR /app

# Install system dependencies for pip and security
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy and install dependencies separately (improves build caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Expose the port (Render assigns a PORT dynamically)
EXPOSE 8000

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start Supervisor to run multiple processes
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
