FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure log directory exists
RUN mkdir -p /app/logs

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "30", "--access-logfile", "-", "app:app"]
