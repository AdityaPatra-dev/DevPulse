# Stage 1: Build dependencies
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# Stage 2: Minimal runtime image
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Install curl for container HEALTHCHECK
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy pre-built virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root system group and user
RUN groupadd -g 10001 devpulse && \
    useradd -u 10001 -g devpulse -s /bin/bash -m appuser

# Copy application files with proper ownership
COPY --chown=appuser:devpulse app/ ./app

# Drop root privileges
USER appuser

# Standard OCI Image Annotations & Metadata
LABEL org.opencontainers.image.title="DevPulse Application Service" \
      org.opencontainers.image.description="Cloud-native service health and incident tracking platform with Prometheus observability" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="DevPulse" \
      org.opencontainers.image.authors="Aditya Patra" \
      org.opencontainers.image.source="https://github.com/AdityaPatra-dev/DevPulse" \
      org.opencontainers.image.licenses="MIT"

# Expose internal HTTP port
EXPOSE 8000

# Docker Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

# Start FastAPI application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
