FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

EXPOSE 8000

# Railway injects $PORT; fall back to 8000 for local/Docker Compose use
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
