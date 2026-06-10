# Stage 1: Build
FROM python:3.12-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Install dependencies into a specific directory to copy later
RUN pip install --no-cache-dir --prefix=/install .

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Ensure storage directories exist and are owned by appuser
RUN mkdir -p storage/original storage/final && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Script to run migrations and then start the app
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
