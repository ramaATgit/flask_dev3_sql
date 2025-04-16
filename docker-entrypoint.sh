#!/bin/bash
set -e

# Wait for database to be ready - with better error handling
echo "Waiting for database to be ready..."
RETRIES=10

# Use pg_isready if available, otherwise use a Python script
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

# Initialize the database and add seed data
echo "Initializing database..."
python -c "
from main import app, db
import os
with app.app_context():
    if os.environ.get('DATABASE_URL'):
        db.create_all()
        from main import seed_database
        try:
            seed_database()
            print('Database initialized successfully')
        except Exception as e:
            print(f'Note: Seed data may already exist. Error: {e}')
"

# Start Gunicorn with main.py
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --reload main:app