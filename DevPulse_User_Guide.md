# DevPulse — Complete User & Build Guide

## 1. Project Overview

**Project:** DevPulse — Cloud Incident & Service Status Tracker  
**Track:** Track B — Watch It  
**Goal:** Build a small database-backed web application and carry it through Linux administration, Docker, Docker Compose, AWS EC2, GitHub Actions, GHCR, Prometheus, Grafana, cAdvisor, and node_exporter.

The application is intentionally small. The infrastructure, deployment, observability, security, documentation, and troubleshooting are the important parts.

### Final technology stack

- Fedora Linux — host machine
- KVM / Virtual Machine Manager (virt-manager) — local hypervisor
- Ubuntu Live Server 26 — local VM
- Python + FastAPI — application
- PostgreSQL — database
- Nginx — third Compose service
- Docker Engine + Docker Compose
- Prometheus — metrics collection
- Grafana — dashboards and visualization
- cAdvisor — container metrics
- node_exporter — host metrics
- AWS EC2 t3.micro — cloud deployment
- GitHub + GitHub Actions — source control and CI
- GHCR — container registry
- Optional: Terraform, continuous deployment, Makefile

---

# 2. Assignment Constraints

Before starting, keep these constraints visible.

## Mandatory

- Solo project.
- Exactly one track.
- Track B must be declared by Day 1.
- Public GitHub repository.
- Minimum 15 meaningful commits.
- Commits spread across at least 6 different days.
- No credentials, `.env`, private keys, or AWS keys in Git history.
- Application must be written by you; do not clone and containerize a tutorial repository.
- Application must be an HTTP server.
- At least two routes must read/write database data.
- Real database container; SQLite is not acceptable.
- Database-backed `/healthz` or `/health`.
- Configuration through environment variables.
- Minimal frontend is enough.
- Docker image under 250 MB.
- Multi-stage Dockerfile.
- Pinned base-image tag.
- Non-root final container user.
- Docker `HEALTHCHECK`.
- Three-service minimum Compose stack.
- Named PostgreSQL volume.
- Custom bridge network.
- Service-name database communication.
- `.env.example` committed; `.env` ignored.
- `depends_on` with a database health condition.
- Restart policies.
- AWS budget before launching resources.
- AWS root MFA.
- IAM user for daily work.
- One `t3.micro`.
- `ap-south-1` (Mumbai).
- SSH restricted to your own public IP `/32`.
- GitHub Actions on push to `main`.
- GHCR image with both `latest` and commit-SHA tags.
- At least one check before Docker build.
- Broken and successful CI runs demonstrated.
- Track B observability requirements.
- Final teardown evidence.

---

# 3. Project Architecture

The final system should conceptually look like:

```text
                           INTERNET
                               |
                               v
                         AWS EC2 t3.micro
                               |
                         Security Group
                               |
                    +----------+----------+
                    |                     |
                   SSH                   HTTP
                    |                     |
                    |                  Nginx
                    |                     |
                    |                  FastAPI
                    |                     |
                    |                 PostgreSQL
                    |                     |
                    |                 Named Volume
                    |
              administration


             OBSERVABILITY STACK

 FastAPI /metrics --------+
                          |
 cAdvisor ----------------+--> Prometheus --> Grafana
                          |
 node_exporter ------------+

 GitHub
    |
    v
GitHub Actions
    |
    +--> test/lint
    |
    +--> Docker build
    |
    +--> GHCR
```

---

# 4. Day 1 — Create the Repository and Application

## 4.1 Create the GitHub repository

Suggested repository name:

```text
devpulse-cloud-devops
```

Clone it:

```bash
git clone https://github.com/<YOUR_USERNAME>/devpulse-cloud-devops.git
cd devpulse-cloud-devops
```

Create the initial structure:

```bash
mkdir -p app/routes app/static scripts monitoring/prometheus
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p docs/screenshots
mkdir -p .github/workflows
```

Create:

```text
README.md
.gitignore
.env.example
```

---

## 4.2 Declare Track B in README

Put this near the top:

```text
Track: B — Watch It
Project: DevPulse — Cloud Incident & Service Status Tracker
```

---

# 5. Build the Minimal Application

The application should remain small.

## Required entities

### Service

Suggested fields:

```text
id
name
url
created_at
```

### Incident

Suggested fields:

```text
id
service_id
title
severity
status
created_at
resolved_at
```

---

# 6. Minimum API

Implement at least:

```text
GET  /services
POST /services

GET  /incidents
POST /incidents

PATCH /incidents/{id}

GET /healthz
GET /metrics
```

The first four routes satisfy the database read/write requirement.

---

# 7. Frontend

A single plain HTML page is enough.

It can provide:

- service list
- incident list
- create service form
- create incident form
- incident status update
- basic severity display

Do not spend days making it beautiful.

The assignment explicitly says a minimal frontend is acceptable.

---

# 8. Local Application Test

Before Docker:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy psycopg[binary] pydantic-settings prometheus-client
```

Run the application:

```bash
uvicorn app.main:app --reload
```

Test:

```bash
curl http://127.0.0.1:8000/healthz
```

Open:

```text
http://127.0.0.1:8000
```

---

# 9. Commit Strategy

Do not create one giant commit.

Example:

```text
feat: initialize DevPulse project
feat: add service database model
feat: add incident database model
feat: add service API
feat: add incident API
feat: add health endpoint
feat: add minimal frontend
```

Keep meaningful commits throughout the 10 days.

Target approximately 20 commits rather than barely reaching 15.

---

# 10. Day 2 — Set Up KVM and Virtual Machine Manager on Fedora

Install and configure KVM, QEMU, libvirt, and Virtual Machine Manager (`virt-manager`) on Fedora:

```bash
sudo dnf install -y @virtualization virt-manager
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt $USER
```

Verify:

```bash
virsh list --all
virt-manager --version
```

Check hardware virtualization:

```bash
lscpu | grep -i virtualization
```

You should see AMD-V/SVM or VT-x/VMX virtualization support.

If virtualization is unavailable, check BIOS/UEFI.

---

# 11. Set Up Ubuntu Live Server 26 in KVM / virt-manager

Use:

```text
Ubuntu Live Server 26
```

Do not install Ubuntu Desktop.

Create a VM in Virtual Machine Manager (`virt-manager`) with:

```text
CPU: 2 vCPU
RAM: 4 GB
Disk: 25 GB
```

Networking:
Use the Default NAT Network (`virbr0` / NAT network), or configure Host-to-Guest port forwarding for SSH if needed.

---

# 12. Create a VM Snapshot

Immediately after the clean Ubuntu installation:

```text
Virtual Machine Manager (virt-manager)
→ Open VM console
→ Manage VM Snapshots (or via CLI: virsh snapshot-create-as --domain <vm-name> --name clean-ubuntu-base --description "Clean base snapshot")
→ Take Snapshot
```

Name it:

```text
clean-ubuntu-base
```

This protects you if you lock yourself out during SSH hardening.

---

# 13. Day 2–3 — Configure Ubuntu

Update packages:

```bash
sudo apt update
sudo apt upgrade
```

Install basic tools:

```bash
sudo apt install -y \
  curl \
  wget \
  git \
  vim \
  nano \
  net-tools \
  dnsutils \
  traceroute \
  ufw \
  openssh-server
```

Check IP:

```bash
ip a
```

Check SSH:

```bash
systemctl status ssh
```

---

# 14. Configure Static IP

Use Netplan.

First inspect interfaces:

```bash
ip a
```

Find the interface name.

Inspect current Netplan:

```bash
ls /etc/netplan/
```

Edit the appropriate YAML file.

Before applying changes, understand:

- interface name
- IP address
- gateway
- DNS server
- network mode

Apply:

```bash
sudo netplan try
```

Then:

```bash
sudo netplan apply
```

Verify:

```bash
ip a
ip route
```

Reboot and confirm the address survives:

```bash
sudo reboot
```

---

# 15. SSH Key Authentication

On Fedora host:

```bash
ssh-keygen -t ed25519
```

Copy the public key into the VM.

Test key login before disabling passwords:

```bash
ssh -p 2222 <user>@localhost
```

Only after key login works, edit:

```text
/etc/ssh/sshd_config
```

Set:

```text
PasswordAuthentication no
PermitRootLogin no
```

Change SSH to:

```text
Port 2222
```

Restart:

```bash
sudo systemctl restart ssh
```

Test again.

Do not close your working SSH session until the new connection is confirmed.

---

# 16. UFW Firewall

Enable:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

Allow SSH:

```bash
sudo ufw allow 2222/tcp
```

Later allow only the application port actually required.

Enable:

```bash
sudo ufw enable
```

Check:

```bash
sudo ufw status verbose
```

You need evidence for the report and video.

---

# 17. Users and Permissions

Create a deployment user:

```bash
sudo adduser deploy
```

Create a project group:

```bash
sudo groupadd devpulse
```

Add the required users:

```bash
sudo usermod -aG devpulse <your-user>
sudo usermod -aG devpulse deploy
```

Create:

```bash
sudo mkdir -p /opt/devpulse
```

Set sensible ownership:

```bash
sudo chown -R <your-user>:devpulse /opt/devpulse
sudo chmod -R 2775 /opt/devpulse
```

Inspect:

```bash
ls -ld /opt/devpulse
```

Understand every character in the permission string before putting it in the report.

---

# 18. systemd Service

Create your own service.

Example concept:

```text
/etc/systemd/system/devpulse-maintenance.service
```

The service should:

- execute your own script
- use `Restart=always`
- be enabled at boot

After creating:

```bash
sudo systemctl daemon-reload
sudo systemctl enable devpulse-maintenance
sudo systemctl start devpulse-maintenance
```

Check:

```bash
systemctl status devpulse-maintenance
```

Kill the process and demonstrate that systemd restarts it.

---

# 19. Cron Job

Create a cron job that records disk usage every five minutes.

Example:

```bash
crontab -e
```

Use a command that writes a timestamp and disk usage to a log.

Verify the log later.

---

# 20. Networking Evidence

Capture:

```bash
ip a
```

```bash
ss -tulpn
```

```bash
ping -c 4 8.8.8.8
```

```bash
traceroute 8.8.8.8
```

```bash
dig example.com
```

In your report explain:

- what a port is
- private IP vs public IP
- what happened during DNS lookup
- what your VM network mode does

---

# 21. Day 4 — Docker Engine

Install Docker Engine using the official Docker Ubuntu repository.

Do not use Docker Desktop for the Ubuntu VM.

Verify:

```bash
docker --version
docker compose version
```

Add your user to the Docker group:

```bash
sudo usermod -aG docker $USER
```

Log out/in or restart the session.

Test:

```bash
docker run hello-world
```

Understand why membership of the Docker group is effectively equivalent to powerful/root-level host access.

---

# 22. Dockerfile

Create a multi-stage Dockerfile.

Required concepts:

```text
builder stage
     ↓
dependency/build artifacts
     ↓
slim runtime stage
     ↓
non-root user
```

Requirements:

- pinned base image tag
- multi-stage build
- non-root user
- healthcheck
- no unnecessary packages
- `.dockerignore`

Build:

```bash
docker build -t devpulse:local .
```

Check size:

```bash
docker images
```

Requirement:

```text
< 250 MB
```

Run:

```bash
docker run --rm -p 8000:8000 devpulse:local
```

Check:

```bash
curl http://localhost:8000/healthz
```

Check the container user:

```bash
docker exec <container> whoami
```

It must not print:

```text
root
```

---

# 23. .dockerignore

At minimum:

```text
.git
.env
.venv
venv
__pycache__
*.pyc
docs/screenshots
```

Do not accidentally send your Git history or secrets into the Docker build context.

---

# 24. Day 5 — Docker Compose

Create:

```text
docker-compose.yml
```

Initial required services:

```text
app
postgres
nginx
```

Then add Track B:

```text
prometheus
grafana
cadvisor
node-exporter
```

---

# 25. PostgreSQL Persistence

Create a named volume:

```text
postgres_data
```

PostgreSQL must store its data there.

Test persistence:

```bash
docker compose up -d
```

Create some application data.

Then:

```bash
docker compose down
```

Start again:

```bash
docker compose up -d
```

Confirm your data still exists.

Understand the difference:

```bash
docker compose down
```

versus:

```bash
docker compose down -v
```

The latter removes named volumes.

---

# 26. Compose Network

Create a custom bridge network.

Your app should connect to PostgreSQL using:

```text
postgres
```

not:

```text
localhost
```

The database hostname is the Compose service name.

---

# 27. Database Healthcheck

Add a PostgreSQL healthcheck.

Then configure the application to depend on the database health condition.

The objective is:

```text
PostgreSQL container starts
       ↓
PostgreSQL becomes ready
       ↓
healthcheck becomes healthy
       ↓
application starts
```

A running container does not automatically mean the database is accepting connections.

---

# 28. Environment Variables

Use:

```text
.env
```

locally/server-side.

Commit:

```text
.env.example
```

with dummy values.

`.gitignore` must contain:

```text
.env
*.pem
```

Never commit credentials.

---

# 29. Restart Policies

Each Compose service should have an appropriate restart policy.

Test that services recover from failure.

---

# 30. Day 6 — AWS Setup

Use:

```text
Region: ap-south-1
Instance: t3.micro
OS: Ubuntu Server 24.04 LTS
```

Before EC2:

1. Choose the AWS Free plan if applicable to your account.
2. Configure root MFA.
3. Create billing budget.
4. Configure email alerts.
5. Create IAM user for daily work.

Take screenshots.

---

# 31. AWS Budget

Create a budget before launching EC2.

Use a small threshold appropriate for the assignment.

The brief specifically requires a zero-spend or $5 budget with alerts at:

```text
50%
80%
100%
```

Capture the screenshot.

---

# 32. EC2 Security Group

SSH:

```text
TCP 22
Source: YOUR_PUBLIC_IP/32
```

Do not use:

```text
0.0.0.0/0
```

Application ports should only include ports actually needed.

---

# 33. EC2 Key

Create a new EC2 key pair.

Store the `.pem` securely.

On Fedora:

```bash
chmod 400 <key>.pem
```

Never commit it.

---

# 34. AWS CLI

Configure the AWS CLI on the appropriate machine.

Verify identity:

```bash
aws sts get-caller-identity
```

The output should show the identity you expect.

---

# 35. Day 7 — Deploy to EC2

SSH:

```bash
ssh -i <key>.pem ubuntu@<EC2_PUBLIC_IP>
```

Install Docker Engine and Compose.

Clone:

```bash
git clone https://github.com/<YOUR_USERNAME>/devpulse-cloud-devops.git
```

Create `.env` directly on EC2.

Do not place `.env` in Git.

Start:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

---

# 36. Test Public Access

Use a device/network that is not your local LAN.

For example, phone mobile data.

Open:

```text
http://<EC2_PUBLIC_IP>
```

Verify the application loads.

This proves that the application is actually reachable over the public internet.

---

# 37. Record a Local vs EC2 Difference

You need at least one real difference.

Possible examples:

- EC2 has only 1 GB RAM.
- Security group affects external access.
- Build behavior differs because of memory.
- Images may be cached locally.
- Architecture/platform may differ.
- Swap may be needed.

Do not invent one.

Record what actually happens.

---

# 38. Day 8 — GitHub Actions

Create:

```text
.github/workflows/ci.yml
```

Trigger:

```text
push:
  branches:
    - main
```

Pipeline:

```text
Push
 ↓
Checkout
 ↓
Lint/Test
 ↓
Docker Build
 ↓
GHCR Login
 ↓
Push latest
 ↓
Push commit-SHA tag
```

The Docker build must not happen if the check fails.

---

# 39. GHCR

Image naming:

```text
ghcr.io/<github-username>/devpulse
```

Tags:

```text
latest
<commit-sha>
```

The SHA tag gives you an immutable reference to the image produced by a specific commit.

Add the workflow status badge to README.

---

# 40. Broken CI Test

Intentionally introduce a harmless code failure.

Push.

Capture the red GitHub Actions run.

Fix it.

Push again.

Capture the green run.

Restore the repository to a correct state.

---

# 41. Day 9 — Track B

Track B requires:

```text
Prometheus
Grafana
cAdvisor
node_exporter
```

Add them to Compose.

---

# 42. Instrument FastAPI

Expose:

```text
/metrics
```

Implement:

### Counter

Requests per route.

Concept:

```text
HTTP request
   ↓
counter increases
```

### Histogram

Request duration.

Concept:

```text
request
   ↓
measure duration
   ↓
record observation
```

These metrics allow Prometheus to answer questions about traffic, errors and latency.

---

# 43. Prometheus Configuration

Configure Prometheus to scrape:

```text
FastAPI
cAdvisor
node_exporter
```

Remember:

Inside Compose, use service names.

Do not use `localhost` to refer to another container.

---

# 44. Grafana

Configure Grafana to use Prometheus as a datasource.

Change the Grafana admin password through an environment variable.

Do not leave the default password.

---

# 45. Dashboard

Create four required panels:

1. Request rate
2. Error rate
3. p95 request latency
4. Container CPU + memory

Export/provision the dashboard as JSON so it can be recreated without manually clicking through the UI.

---

# 46. Alert

Create one alert.

Recommended:

```text
Application down for more than 1 minute
```

Alternative:

```text
Error rate > 5%
```

Test it.

---

# 47. Chaos Demonstration

Start everything:

```bash
docker compose up -d
```

Open Grafana.

Then:

```bash
docker stop <app-container>
```

Show:

```text
metrics change
       ↓
Prometheus detects problem
       ↓
Grafana alert fires
```

Start it:

```bash
docker start <app-container>
```

Show recovery.

This is a major Track B demonstration.

---

# 48. Day 10 — README

README must include:

1. Project name
2. Your name
3. Roll number
4. Track
5. Application description
6. Architecture diagram
7. Tech stack
8. Exact local setup
9. Environment variable table
10. Live URL while active
11. Teardown date
12. CI status badge

---

# 49. Architecture Diagram

Show:

```text
Browser
  ↓
Internet
  ↓
AWS Security Group
  ↓
EC2
  ↓
Nginx
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
Named Volume
```

Also show:

```text
FastAPI → Prometheus
cAdvisor → Prometheus
node_exporter → Prometheus
Prometheus → Grafana
```

Label important ports.

---

# 50. Evidence Collection

Keep screenshots for:

### Stage 1
- VM configuration
- Ubuntu Server
- snapshot
- SSH

### Stage 2
- static IP
- SSH key login
- UFW
- systemd
- cron
- networking commands
- reboot survival

### Stage 3
- Dockerfile
- image size
- non-root `whoami`
- healthcheck

### Stage 4
- `docker compose ps`
- volume
- persistence test
- network
- environment setup

### Stage 5
- budget
- MFA
- IAM
- EC2
- security group
- AWS CLI identity

### Stage 6
- EC2 containers
- public application
- mobile-data test

### Stage 7
- GitHub Actions green
- GitHub Actions red
- GHCR image
- README badge

### Track B
- Prometheus targets
- Grafana dashboard
- alert firing
- recovery
- cAdvisor
- node_exporter

---

# 51. Report — Breakage Log

Every time something breaks, record:

```text
Date:
Stage:
Symptom:
What I initially assumed:
What actually happened:
Commands/tests used:
Root cause:
Fix:
What I learned:
```

Do not erase the history of problems.

The assignment explicitly values the debugging process.

---

# 52. Demo Video

Target:

```text
5–10 minutes
1080p
your voice
large terminal font
```

Show:

1. SSH into local VM using key.
2. `systemctl status` of your service.
3. `ufw status`.
4. `docker compose ps` on EC2.
5. Live application.
6. GitHub Actions successful run.
7. GHCR image.
8. Track B dashboard.
9. Alert firing.
10. Recovery.
11. Closing 60 seconds explaining one real failure.

---

# 53. Final Security Check

Before submission:

```bash
git status
```

Inspect:

```bash
git log --all --stat
```

Search for accidental secrets.

Run a secret scanner such as:

```text
gitleaks
```

Check that Git history does not contain:

```text
.env
*.pem
AWS access keys
passwords
tokens
private keys
```

A credential in Git history can cause a significant deduction even if later deleted.

---

# 54. Teardown

Record the demo first.

Then:

```bash
docker compose down -v
```

Terminate EC2.

Check:

- EC2 instances
- EBS volumes
- Elastic IPs
- snapshots
- AMIs
- security groups
- key pairs
- other regions
- Cost Explorer
- AWS budget

For Track B, no S3/SSM cleanup is required unless you separately created those resources.

Capture:

```text
EC2 dashboard showing zero running instances
```

Keep your GitHub repository and local VM.

---

# 55. Optional Bonuses

Only attempt after the core project is complete.

## Bonus 1 — Continuous Deployment

GitHub Actions:

```text
push
 ↓
build
 ↓
GHCR
 ↓
SSH to EC2
 ↓
pull new image
 ↓
restart stack
 ↓
health check
```

## Bonus 2 — Terraform

Define:

- EC2
- security group
- required infrastructure

as code.

## Bonus 3 — Staging

Create a second Compose environment.

## Bonus 4 — Makefile

Useful commands:

```text
make up
make down
make logs
make test
make build
make clean
```

---

# 56. Final Submission Checklist

```text
[ ] Track B declared
[ ] Application works
[ ] 15+ meaningful commits
[ ] 6+ commit days
[ ] No secrets in Git history
[ ] Ubuntu VM
[ ] Snapshot
[ ] Static IP
[ ] SSH keys
[ ] SSH hardened
[ ] UFW
[ ] Users/groups
[ ] Permissions
[ ] systemd
[ ] cron
[ ] networking evidence
[ ] Docker Engine
[ ] multi-stage Dockerfile
[ ] pinned image
[ ] non-root user
[ ] HEALTHCHECK
[ ] image <250 MB
[ ] Compose
[ ] 3+ required services
[ ] PostgreSQL volume
[ ] persistence proven
[ ] custom network
[ ] service-name networking
[ ] .env.example
[ ] depends_on health condition
[ ] restart policies
[ ] AWS budget
[ ] MFA
[ ] IAM
[ ] t3.micro
[ ] ap-south-1
[ ] SSH /32
[ ] AWS CLI identity
[ ] public application
[ ] GitHub Actions
[ ] GHCR
[ ] latest tag
[ ] SHA tag
[ ] check before build
[ ] red CI run
[ ] green CI run
[ ] Prometheus
[ ] Grafana
[ ] cAdvisor
[ ] node_exporter
[ ] custom counter
[ ] histogram
[ ] four dashboard panels
[ ] alert
[ ] chaos demo
[ ] architecture diagram
[ ] README complete
[ ] screenshots
[ ] report
[ ] demo video
[ ] teardown
```
