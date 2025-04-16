# Use official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=main.py
ENV FLASK_DEBUG=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-local.txt .
RUN pip install --no-cache-dir -r requirements-local.txt

# Copy application code
COPY . .

# Create the SQLite database directory
RUN mkdir -p instance

# Recommended for SQLite in Docker
RUN chmod a+w /app/instance

EXPOSE 5000

# Note: The actual startup command is in docker-compose.yml
