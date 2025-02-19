# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for better performance & logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    C_FORCE_ROOT=1  
    
# Allow Celery to run as root

# Set working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Ensure log file exists and is writable
RUN touch /app/supervisord.log && chmod 666 /app/supervisord.log

# Ensure correct permissions for the entire /app directory
RUN chown -R root:root /app && chmod -R 777 /app

# Install system dependencies and Python dependencies
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (Assuming you use requirements.txt)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Supervisor configuration file (Ensure you have a valid supervisord.conf)
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Expose necessary ports (Adjust based on your app)
EXPOSE 8000

# Start Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
