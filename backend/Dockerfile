FROM python:3.11-slim

WORKDIR /app

# System deps for asyncpg + geoip2 compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for GeoIP DB and log files
RUN mkdir -p /app/geoip /cowrie-logs

EXPOSE 8000

# Use 1 worker for WebSocket broadcast consistency
# For production scale: use a message broker (Redis Pub/Sub) instead
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
