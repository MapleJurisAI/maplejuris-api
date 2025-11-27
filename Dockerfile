# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

# Copy application code
COPY . .

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8080

# Run the application
# Cloud Run sets PORT environment variable
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}