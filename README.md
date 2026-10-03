# DevPulse — Cloud Incident & Service Status Tracker

![CI/CD Pipeline](https://github.com/AdityaPatra-dev/DevPulse/actions/workflows/ci.yml/badge.svg)
![Track](https://img.shields.io/badge/Track-B%20(Watch%20It)-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Author:** Aditya Patra  
**Roll Number:** [YOUR_ROLL_NUMBER]  
**Track:** Track B — Watch It  
**Live URL:** `http://<EC2_PUBLIC_IP>` *(Active during evaluation)*  
**Scheduled Teardown Date:** [TEARDOWN_DATE, e.g. Oct 15, 2026]  

---

## 1. Project Overview

**DevPulse** is a lightweight, cloud-native status and incident management tracking platform. It allows engineering teams to register monitored services, log operational incidents, update outage statuses, and track system health.

Built with **FastAPI**, **PostgreSQL**, and **Nginx**, DevPulse implements full end-to-end **Track B Observability** through **Prometheus**, **Grafana**, **cAdvisor**, and **node_exporter**, featuring custom application-level metrics, real-time dashboards, and automated alert triggering.

---

## 2. Architecture Diagram

```text
                                  INTERNET
                                      |
                                      v
                             AWS EC2 (t3.micro)
                                      |
                         Security Group (SSH: /32, HTTP: 80)
                                      |
                      +---------------+---------------+
                      |                               |
                   SSH (22)                        HTTP (80)
                      |                               |
                 Admin Access                   Nginx Reverse Proxy
                                                      |
                                                   FastAPI
                                                      |
                                             PostgreSQL (Port 5432)
                                                      |
                                            devpulse_postgres_data
                                                (Named Volume)

             =================== OBSERVABILITY STACK ===================

   +--------------------------+
   | FastAPI App (/metrics)   |--------+
   | - Counter: requests      |        |
   | - Histogram: latency     |        |
   +--------------------------+        |
   +--------------------------+        v
   | cAdvisor (Port 8080)     |---> Prometheus (Port 9090) ---> Grafana (Port 3000)
   | - Container CPU/RAM      |        ^                          - Request Rate
   +--------------------------+        |                          - Error Rate
   +--------------------------+        |                          - p95 Latency
   | node_exporter (Port 9100)|--------+                          - Container CPU/RAM
   | - Host CPU, RAM, Disk    |                                   - Outage Alert Rule
   +--------------------------+
```

---

## 3. Technology Stack

- **Application:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn
- **Database:** PostgreSQL 16 (Alpine) with named persistent volume
- **Reverse Proxy:** Nginx 1.25 (Alpine)
- **Containerization:** Docker (Multi-stage build, non-root user `<250MB`), Docker Compose v2
- **Observability (Track B):**
  - Prometheus v2.51.0 (Scrapes FastAPI, cAdvisor, and node_exporter)
  - Grafana 10.4.1 (Provisioned datasource and dashboard)
  - cAdvisor v0.49.1 (Container resource utilization metrics)
  - node_exporter v1.7.0 (Host hardware & OS metrics)
- **Local Hypervisor & OS:** KVM / Virtual Machine Manager (`virt-manager`), Ubuntu Live Server 26
- **Host OS:** Fedora Linux
- **Cloud Infrastructure:** AWS EC2 `t3.micro` (`ap-south-1` Mumbai)
- **CI/CD & Registry:** GitHub Actions & GitHub Container Registry (GHCR)

---

## 4. Environment Variables

DevPulse is configured through environment variables. A template is provided in [`.env.example`](file:///.env.example).

| Variable | Description | Default / Example Value |
| :--- | :--- | :--- |
| `APP_NAME` | Name of the application | `DevPulse` |
| `ENVIRONMENT` | Runtime environment (`development`, `production`) | `production` |
| `LOG_LEVEL` | Application logging verbosity | `INFO` |
| `POSTGRES_USER` | PostgreSQL superuser username | `devpulse` |
| `POSTGRES_PASSWORD` | PostgreSQL superuser password | `devpulse_password` |
| `POSTGRES_DB` | Database schema name | `devpulse_db` |
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql+psycopg://devpulse:devpulse_password@postgres:5432/devpulse_db` |
| `GRAFANA_ADMIN_USER`| Administrator username for Grafana | `admin` |
| `GRAFANA_ADMIN_PASSWORD` | Administrator password for Grafana | `devpulse_admin` |

> [!WARNING]
> Never commit `.env` or AWS private keys (`*.pem`) to the Git repository.

---

## 5. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Web UI Dashboard |
| `GET` | `/healthz` | Database-backed health check (`SELECT 1`) |
| `GET` | `/services` | List all monitored services |
| `POST` | `/services` | Register a new monitored service |
| `GET` | `/incidents` | List incidents (filter by `status` or `service_id`) |
| `POST` | `/incidents` | Report a new incident for a service |
| `PATCH` | `/incidents/{id}` | Update incident status (`investigating`, `identified`, `monitoring`, `resolved`) |
| `GET` | `/metrics` | Prometheus metrics endpoint (Counter & Histogram) |

---

## 6. Local Setup & Execution

### Prerequisites
- Docker Engine & Docker Compose installed
- Git

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/AdityaPatra-dev/DevPulse.git
cd DevPulse

# 2. Configure environment
cp .env.example .env

# 3. Launch the full stack (App, DB, Nginx, Prometheus, Grafana, cAdvisor, node_exporter)
docker compose up -d

# 4. Check running containers
docker compose ps
```

### Access URLs
- **Web Application:** [http://localhost](http://localhost) (Nginx reverse proxy on port 80)
- **Direct FastAPI / Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/healthz](http://localhost:8000/healthz)
- **Prometheus UI:** [http://localhost:9090](http://localhost:9090)
- **Grafana Dashboard:** [http://localhost:3000](http://localhost:3000) (`admin` / `devpulse_admin`)
- **cAdvisor:** [http://localhost:8080](http://localhost:8080)
- **node_exporter:** [http://localhost:9100/metrics](http://localhost:9100/metrics)

---

## 7. Track B Observability Demonstration

1. **Dashboard:** Access Grafana at `http://<IP>:3000` to view the 4 required panels:
   - Request Rate (req/sec by route and status)
   - Error Rate (%)
   - p95 Request Latency (seconds)
   - Container CPU & Memory Utilization
2. **Alert Verification:** An alert rule is configured to detect application downtime (`up{job="devpulse-app"} == 0` for 1m).
3. **Chaos Demonstration:**
   ```bash
   # Stop application to trigger alert
   docker stop devpulse_app

   # Observe Prometheus target down and Grafana alert firing
   # Restart application
   docker start devpulse_app
   ```
