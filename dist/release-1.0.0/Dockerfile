# Multi-stage Dockerfile for Streamlit portfolio app
# Stage 1: build deps layer
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System packages (add others if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency specs first for better layer caching
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose Streamlit default port
EXPOSE 8501

# Environment defaults (override with -e or --env-file)
ENV APP_ENV=production \
    ENABLE_MICRO_PROVIDERS=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PYTHONPATH=/app

# Persist data (DB, cache) by mounting a volume from host (-v ...:/app/data)
VOLUME ["/app/data"]

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
