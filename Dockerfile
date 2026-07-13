FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first for layer caching
COPY pyproject.toml requirements.txt ./

# Install the package in editable mode (exposes the `fedscrape` CLI)
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

RUN mkdir -p scrape download

EXPOSE 8000

# Railway injects $PORT; fall back to 8000 for local/Docker Compose use
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
