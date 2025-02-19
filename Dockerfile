# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PORT=8000
ENV PYTHONPATH=/app

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure the scripts directory exists and set permissions
RUN mkdir -p /app/scripts && \
    chmod +x /app/scripts/start.sh && \
    ls -l /app/scripts

# Expose the application port
EXPOSE $PORT

# Run the application using a process manager
CMD ["/bin/sh", "/app/scripts/start.sh"]