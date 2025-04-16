#!/bin/bash

# Bank Account Management System - Docker Reset Script
# This script helps stop, clean up, and restart the Docker containers

# Don't exit immediately on error, we'll handle errors as they occur
set +e

echo "====================================================="
echo "     Bank Account Management System Docker Reset"
echo "====================================================="

# Check for Docker requirements
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in your PATH"
    echo "Please install Docker Desktop or Docker Engine first"
    exit 1
fi

# Make docker-entrypoint.sh executable
echo "Making docker-entrypoint.sh executable..."
chmod +x docker-entrypoint.sh
chmod +x docker-run.sh

# Stop any running containers
echo "Stopping any running containers..."
docker compose down

# Remove all volumes to get a fresh start
echo "Removing Docker volumes to get a fresh start..."
VOLUMES=$(docker volume ls -q | grep -E 'bankdatamanager|bank_management' 2>/dev/null)
if [ -n "$VOLUMES" ]; then
    docker volume rm $VOLUMES
else
    echo "No relevant volumes found to remove"
fi

# Rebuild the Docker containers
echo "Rebuilding Docker containers..."
docker compose build --no-cache

if [ $? -ne 0 ]; then
    echo "Error: Failed to build Docker containers"
    echo "Check your Dockerfile and Docker configuration"
    exit 1
fi

# Start the containers
echo "Starting the application..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "Error: Failed to start Docker containers"
    echo "Try running 'docker compose logs' to see what went wrong"
    exit 1
fi

# Wait a moment for services to start
echo "Waiting for services to start..."
sleep 5

# Check if containers are running
CONTAINERS=$(docker compose ps --services | wc -l)
if [ "$CONTAINERS" -lt 2 ]; then
    echo "Warning: Not all containers are running."
    echo "Check logs with: docker compose logs"
    echo "You might need to manually make docker-entrypoint.sh executable in the container with:"
    echo "docker compose exec web chmod +x /app/docker-entrypoint.sh"
fi

echo "====================================================="
echo "Reset complete! Application should be running."
echo "====================================================="
echo "The application is available at: http://localhost:5000"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
echo "====================================================="
echo ""
echo "Note: If you encounter database connection issues,"
echo "the containers may still be initializing. Wait a moment"
echo "and try refreshing the page."
echo "====================================================="