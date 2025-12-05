# Base image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY Pipfile Pipfile.lock ./

# Install pipenv and dependencies
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy

# Copy code
COPY . .

# Expose port (Cloud Run uses PORT)
EXPOSE 8080

# Correct CMD: use exec form and environment variable
# Use PORT environment variable
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT
