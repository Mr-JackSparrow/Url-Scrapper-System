# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install Bash
RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PORT=8000
ENV PYTHONPATH=/app

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application (including start.sh at the root level)
COPY . .

# Make start.sh executable and verify
RUN chmod +x /app/start.sh && \
    ls -l /app

# Expose the application port
EXPOSE $PORT

# Run the application using start.sh with Bash
CMD ["/bin/bash", "/app/start.sh"]