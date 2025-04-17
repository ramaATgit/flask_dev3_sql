FROM python:3.9-slim

WORKDIR /app

# Install system deps (SQLite is included)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Ensure the instance folder exists
RUN mkdir -p /app/instance

EXPOSE 5000

# Production (Gunicorn) or Development (Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
