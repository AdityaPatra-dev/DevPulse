# DevPulse — Cloud-Native Service & Incident Tracker

[![Docker Image Size](https://img.shields.io/docker/image-size/adityapatra/devpulse/latest?color=blue&label=image%20size)](https://hub.docker.com/r/adityapatra/devpulse)
[![Docker Pulls](https://img.shields.io/docker/pulls/adityapatra/devpulse?color=brightgreen)](https://hub.docker.com/r/adityapatra/devpulse)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

**DevPulse** is a lightweight, cloud-native microservice health monitoring and incident management engine built with **FastAPI**, **PostgreSQL**, and **Prometheus**. It provides real-time service tracking, automated database health verification, and native metrics instrumentation.

---

## Supported Tags & Architectures

| Tag | Dockerfile Link | Base OS | Architecture | Compressed Size |
| :--- | :--- | :--- | :--- | :--- |
| `latest` | [Dockerfile](https://github.com/AdityaPatra-dev/DevPulse/blob/main/Dockerfile) | Debian Bookworm Slim | `linux/amd64` | ~78 MB |
| `v1.0.0` | [Dockerfile](https://github.com/AdityaPatra-dev/DevPulse/blob/main/Dockerfile) | Debian Bookworm Slim | `linux/amd64` | ~78 MB |

*Note: `adityapatra/devpulse:latest` and `adityapatra/devpulse-app:latest` point to the identical verified production build.*

---

## Key Highlights & Architecture

- **Multi-Stage Build:** Clean separation between build-time compilation dependencies (`build-essential`) and runtime environment.
- **Security Hardened:** Runs under dedicated unprivileged non-root user `appuser` (`UID 10001`, `GID 10001`).
- **Minimal Attack Surface:** Slim Debian Bookworm runtime image with size < 250 MB.
- **Built-in Native Healthcheck:** Pre-configured Docker healthcheck probing `/healthz` every 15 seconds.
- **Observability Ready:** Ships with Prometheus instrumentation middleware tracking request latencies, status codes, and active connections.

---

## Quick Start

### 1. Standalone Container

Run DevPulse connected to an external PostgreSQL instance:

```bash
docker run -d \
  --name devpulse \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=postgresql+psycopg://devpulse:devpulse_password@db.example.com:5432/devpulse_db \
  adityapatra/devpulse:latest
```

Verify status:
```bash
docker inspect --format='{{json .State.Health.Status}}' devpulse
# Output: "healthy"
```

---

### 2. Docker Compose (Recommended Production Stack)

Deploy DevPulse alongside PostgreSQL, Nginx reverse proxy, Prometheus, and Grafana:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: devpulse_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: devpulse
      POSTGRES_PASSWORD: devpulse_password
      POSTGRES_DB: devpulse_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devpulse -d devpulse_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    image: adityapatra/devpulse:latest
    container_name: devpulse_app
    restart: unless-stopped
    environment:
      ENVIRONMENT: production
      DATABASE_URL: postgresql+psycopg://devpulse:devpulse_password@postgres:5432/devpulse_db
      APP_HOST: 0.0.0.0
      APP_PORT: 8000
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

Start the stack:
```bash
docker compose up -d
```

---

## Configuration Reference

All settings can be configured via environment variables or a `.env` file mounted into the container:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `DevPulse` | Application display name |
| `ENVIRONMENT` | `production` | Deployment mode (`development`, `staging`, `production`) |
| `APP_HOST` | `0.0.0.0` | Bind address for Uvicorn ASGI server |
| `APP_PORT` | `8000` | Bind port for Uvicorn ASGI server |
| `DATABASE_URL` | *(Required)* | Full SQLAlchemy connection string (`postgresql+psycopg://...`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## API Endpoints

Once running, access the following endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Web Dashboard user interface |
| `/healthz` | `GET` | Container & DB healthcheck probe (returns HTTP 200/503) |
| `/metrics` | `GET` | Prometheus scrapable time-series metrics |
| `/docs` | `GET` | Interactive Swagger OpenAPI documentation |
| `/services` | `GET` / `POST` | Manage monitored services |
| `/incidents`| `GET` / `POST` | Log and update service incident tickets |

---

## Security & Compliance Posture

1. **Non-Root Execution:** Container drops root privileges and executes as `appuser` (`10001:10001`).
2. **Zero Injected Secrets:** Image contains no hardcoded passwords, private keys, or API tokens.
3. **Multi-Stage Sanitization:** Compilers and build tooling are stripped from the final runtime container.
4. **OCI Compliant:** Annotations and metadata conform to Open Container Initiative (OCI) image specifications.

---

## Source & Issue Tracking

- **Repository:** [https://github.com/AdityaPatra-dev/DevPulse](https://github.com/AdityaPatra-dev/DevPulse)
- **Author:** Aditya Patra
- **License:** MIT License
