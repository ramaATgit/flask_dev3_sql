#!/bin/bash
set -e

# Bank Account Management System - Docker Run Script
# This script is a fallback for Docker deployments

echo "====================================================="
echo "     Bank Account Management System Docker Run"
echo "====================================================="

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
RETRIES=10

# Use PSQL_COMMAND if pg_isready is not available
if command -v pg_isready >/dev/null 2>&1; then
  # Use pg_isready if available
  until pg_isready -h db -U postgres || [ $RETRIES -eq 0 ]; do
    echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
    sleep 3
  done
else
  # Fallback to a simple connection test if pg_isready is not available
  until python -c "
import os
import sys
import psycopg2
try:
    conn = psycopg2.connect(
        host='db',
        user='postgres',
        password='postgres',
        database='bank_management'
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" || [ $RETRIES -eq 0 ]; do
    echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
    sleep 3
  done
fi

if [ $RETRIES -eq 0 ]; then
  echo "Error: Could not connect to the database. Exiting..."
  exit 1
fi

echo "Database is ready!"

# Initialize the database if needed
echo "Initializing the database..."
python docker-init.py

# Start the application
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --reload main:app

echo "====================================================="