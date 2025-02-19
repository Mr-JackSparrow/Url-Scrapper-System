# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure scripts are executable
RUN chmod +x /app/scripts/start.sh

# Expose the application port (match this with your service configuration)
ENV PORT=8000
EXPOSE 8000

# Set PYTHONPATH to ensure module imports work
ENV PYTHONPATH=/app

# Run the application using a process manager
CMD ["/bin/sh", "/app/scripts/start.sh"]
