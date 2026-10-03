# DevPulse — Cloud & DevOps Concepts Study Guide

This document explains the important concepts behind the project before you apply them. The goal is not to memorize commands. You should be able to explain what each component does, why it exists, how it communicates with the others, and what can go wrong.

---

# 1. The Big Picture

DevPulse is a small application used to learn the infrastructure surrounding a production-style service.

Think of the system as layers:

```text
APPLICATION
FastAPI
   ↓
DATABASE
PostgreSQL
   ↓
CONTAINERIZATION
Docker
   ↓
ORCHESTRATION
Docker Compose
   ↓
LINUX
Ubuntu Server
   ↓
CLOUD
AWS EC2
   ↓
CI
GitHub Actions
   ↓
REGISTRY
GHCR
   ↓
OBSERVABILITY
Prometheus + Grafana + exporters
```

Each layer solves a different problem.

---

# 2. Fedora Host vs Ubuntu VM

Your Fedora system is the **host**.

KVM and Virtual Machine Manager (`virt-manager`) create a **virtual machine**.

Ubuntu Server runs inside that VM and becomes your Linux server.

```text
Fedora
  |
  +-- KVM / virt-manager
          |
          +-- Ubuntu Server (Guest)
                  |
                  +-- Docker
                        |
                        +-- Containers
```

## Why use a VM?

It gives you a disposable server environment without replacing Fedora.

You can intentionally:

- configure SSH
- break networking
- configure firewalls
- install Docker
- create users
- test systemd
- test cron

without making your Fedora installation the assignment target.

---

# 3. Virtualization

Virtualization allows one physical machine to run another operating system in an isolated virtual environment.

Important terms:

### Host

Your real Fedora computer.

### Guest

Ubuntu running inside KVM / virt-manager.

### Hypervisor

Software that manages virtual machines.

Here:

```text
KVM / QEMU / libvirt = hypervisor & virtualization stack
virt-manager = management GUI / virsh = management CLI
```

### vCPU

A virtual CPU allocated to the guest.

### Virtual disk

A file on your Fedora system (usually qcow2 or raw) representing the VM's disk.

---

# 4. NAT vs Bridged Networking

## NAT

The VM accesses the internet through the host.

```text
VM
 ↓
KVM / virbr0 NAT
 ↓
Fedora
 ↓
Internet
```

The VM is not directly exposed to your physical network.

To access a VM service from Fedora, you can connect directly to the VM's private IP on `virbr0` or configure port forwarding.

Example:

```text
Fedora host
    ↓
KVM virbr0 / NAT
    ↓
Ubuntu :22
```

## Bridged

The VM appears more like another machine on your LAN.

```text
Router
 ├── Fedora
 └── Ubuntu VM
```

For this project, NAT + port forwarding is a practical choice on Fedora, provided you can explain it.

---

# 5. Linux Server

A server is simply a computer providing services to other computers.

Ubuntu Server has no desktop environment in this project.

You interact through:

```text
terminal
SSH
systemd
configuration files
```

Important directories:

```text
/etc        configuration
/var/log    logs
/home       user home directories
/opt        optional application software
/usr/bin    installed executable programs
```

---

# 6. IP Address

An IP address identifies a network interface on a network.

Example:

```text
192.168.1.50
```

This is a private IP.

Private IP ranges include:

```text
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

A public IP is routable over the public internet.

Your EC2 instance receives a public address so external devices can reach the application.

---

# 7. Port

A port identifies a network service on a machine.

Think:

```text
IP = building address
Port = specific door
```

Examples:

```text
22    SSH
80    HTTP
443   HTTPS
5432  PostgreSQL
```

A process listens on a port.

Use:

```bash
ss -tulpn
```

to inspect listening sockets.

---

# 8. DNS

DNS translates names into IP addresses.

Conceptually:

```text
example.com
     ↓
DNS query
     ↓
IP address
```

`dig` lets you inspect DNS.

Important idea:

DNS does not transport your HTTP application data. It helps your system discover the address to connect to.

---

# 9. SSH

SSH provides secure remote shell access.

Basic architecture:

```text
Your Fedora
     |
     | SSH
     v
Ubuntu Server
```

SSH commonly uses TCP port 22.

For this project you move SSH to another port such as:

```text
2222
```

---

# 10. SSH Keys

An SSH key pair contains:

```text
private key
public key
```

The private key stays with you.

The public key goes to the server.

Conceptually:

```text
Fedora
private key
     |
     | authentication
     v
Ubuntu
public key
```

Never publish the private key.

---

# 11. UFW

UFW is a firewall management interface for Linux.

The project wants:

```text
incoming = deny by default
outgoing = allow by default
```

Then explicitly allow required ports.

Example concept:

```text
Internet
   |
   +-- SSH allowed
   |
   +-- app port allowed
   |
   +-- everything else blocked
```

A firewall controls network access. It does not replace SSH authentication or application security.

---

# 12. systemd

`systemd` is the service manager used by Ubuntu.

It can:

- start services
- stop services
- restart services
- enable services at boot
- collect service status

Important commands:

```bash
systemctl status
systemctl start
systemctl stop
systemctl restart
systemctl enable
```

## Restart=always

This means systemd should restart the service after it exits.

This is different from a Docker restart policy.

systemd manages Linux services.

Docker Compose manages containers.

---

# 13. Cron

Cron runs commands according to a schedule.

Example:

```text
every 5 minutes
```

It is useful for simple scheduled maintenance jobs.

Cron is different from systemd:

```text
systemd → service lifecycle
cron    → scheduled tasks
```

---

# 14. Processes

A process is a running instance of a program.

Example:

```text
FastAPI process
PostgreSQL process
Prometheus process
```

Useful commands:

```bash
ps
top
htop
kill
```

Understanding processes helps when debugging services and containers.

---

# 15. Docker

Docker packages an application and its dependencies into a container image.

Without Docker:

```text
application
+
Python version
+
libraries
+
system packages
+
configuration
```

can behave differently on different machines.

Docker tries to make the runtime environment reproducible.

---

# 16. Image vs Container

This distinction is extremely important.

## Image

A packaged, mostly immutable template.

Example:

```text
devpulse:1.0
```

## Container

A running instance of an image.

```text
Image
  ↓
Container
```

You can create multiple containers from the same image.

---

# 17. Dockerfile

A Dockerfile describes how to build an image.

Typical flow:

```text
FROM
COPY
RUN
ENV
USER
EXPOSE
HEALTHCHECK
CMD
```

The Dockerfile is a build recipe.

---

# 18. Multi-stage Docker Build

A multi-stage build uses separate stages.

Example:

```text
Builder
  |
  | dependencies/build artifacts
  v
Runtime
```

The runtime stage does not need everything used during building.

Benefits:

- smaller image
- fewer unnecessary packages
- reduced attack surface
- cleaner production container

The assignment requires this.

---

# 19. Why Pin the Base Image

Avoid:

```dockerfile
FROM python:latest
```

because `latest` can change.

A pinned version gives a more reproducible build.

Concept:

```text
today:
latest → version A

later:
latest → version B
```

A pinned tag reduces unexpected changes.

---

# 20. Non-root Container

By default, some containers run processes as root.

The project requires a non-root user.

Why?

If an attacker compromises the application, limiting privileges reduces the potential impact.

Concept:

```text
container
   |
   +-- appuser
        ↓
     FastAPI
```

not:

```text
container
   |
   +-- root
        ↓
     FastAPI
```

---

# 21. Docker HEALTHCHECK

A healthcheck tells Docker how to test whether the application is responding correctly.

Important distinction:

```text
container running
```

does not necessarily mean:

```text
application healthy
```

For DevPulse:

```text
/healthz
```

should check database connectivity.

---

# 22. `.dockerignore`

`.dockerignore` controls what gets sent to Docker during the build.

You do not want:

```text
.git
.env
.venv
```

inside the build context.

Benefits:

- smaller build context
- faster builds
- prevents accidental secret exposure
- avoids copying unnecessary files

---

# 23. Docker Compose

Docker Compose defines multiple related containers as one application stack.

Instead of manually starting:

```text
PostgreSQL
FastAPI
Nginx
Prometheus
Grafana
...
```

you can use:

```bash
docker compose up -d
```

Compose describes:

- services
- networks
- volumes
- environment variables
- dependencies
- restart policies

---

# 24. Service Names in Compose

Suppose Compose has:

```text
app
postgres
```

The app can connect to:

```text
postgres:5432
```

Why?

Docker Compose provides internal DNS for the Compose network.

Important:

Inside the FastAPI container:

```text
localhost
```

means:

```text
the FastAPI container itself
```

It does NOT mean PostgreSQL.

This is one of the most important Docker networking concepts in the project.

---

# 25. Docker Network

Containers need networking to communicate.

A custom bridge network allows:

```text
Nginx
  ↓
FastAPI
  ↓
PostgreSQL
```

without exposing PostgreSQL publicly.

Only the services that need to communicate should do so.

---

# 26. Docker Volume

Containers are disposable.

If PostgreSQL stores data only inside the container filesystem, removing the container can remove the data.

A named volume provides persistent storage.

```text
PostgreSQL container
        |
        v
  postgres_data
        |
        v
Persistent data
```

Important:

```bash
docker compose down
```

normally preserves named volumes.

But:

```bash
docker compose down -v
```

removes them.

---

# 27. Environment Variables

Configuration should not be hardcoded.

Bad:

```text
DATABASE_PASSWORD = "mypassword"
```

Better:

```text
DATABASE_PASSWORD=${DATABASE_PASSWORD}
```

The `.env` file supplies local configuration.

Commit:

```text
.env.example
```

but ignore:

```text
.env
```

---

# 28. PostgreSQL

PostgreSQL is a relational database.

Core concepts:

```text
Database
  ↓
Tables
  ↓
Rows
  ↓
Columns
```

Example:

```text
services
--------------------------------
id | name | url
```

and:

```text
incidents
--------------------------------
id | service_id | title | status
```

The `service_id` creates a relationship between incidents and services.

---

# 29. API

API means Application Programming Interface.

An HTTP API exposes operations through URLs and HTTP methods.

Examples:

```text
GET
POST
PATCH
DELETE
```

For DevPulse:

```text
GET /services
POST /services
GET /incidents
POST /incidents
PATCH /incidents/{id}
```

---

# 30. HTTP Status Codes

Important ones:

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error
```

Your API should use meaningful status codes.

---

# 31. FastAPI

FastAPI is a Python web framework.

It handles:

- HTTP routing
- request parsing
- response generation
- validation
- API documentation

Typical flow:

```text
Browser
   ↓
HTTP request
   ↓
FastAPI route
   ↓
database operation
   ↓
HTTP response
```

---

# 32. Nginx

Nginx is a web server and reverse proxy.

A reverse proxy sits in front of an application.

```text
Client
  ↓
Nginx
  ↓
FastAPI
```

Instead of exposing the FastAPI container directly, Nginx receives the request and forwards it.

For this project Nginx is primarily the third required application service.

---

# 33. Reverse Proxy

A reverse proxy receives requests on behalf of backend services.

Possible responsibilities:

- routing
- TLS termination
- headers
- load balancing
- access control
- caching

In Track A, reverse proxying and HTTPS are the central task.

In Track B, Nginx is useful as part of the application stack but observability is the main track requirement.

---

# 34. AWS EC2

EC2 provides virtual servers in AWS.

Think:

```text
Your laptop VM
       ≈
cloud VM
```

but the cloud VM exists in AWS infrastructure.

You manage:

- operating system
- packages
- Docker
- firewall/security group
- application

---

# 35. EC2 Instance Type

The assignment specifies:

```text
t3.micro
```

Important concept:

An instance type determines available resources and pricing characteristics.

The project intentionally uses a very small instance.

This means you should avoid unnecessary workloads.

---

# 36. Security Group

A security group is a virtual firewall around an EC2 instance.

For example:

```text
SSH
TCP 22
Source YOUR_IP/32
```

and application traffic:

```text
HTTP
TCP 80
```

A security group rule controls whether traffic can reach the instance.

This is separate from UFW.

You can have:

```text
Internet
   ↓
AWS Security Group
   ↓
EC2
   ↓
UFW
   ↓
Docker
   ↓
Application
```

All layers can affect connectivity.

---

# 37. AWS Region

A region is a geographic AWS area containing AWS infrastructure.

The assignment chooses:

```text
ap-south-1
Mumbai
```

Keep the project resources in one region so that you do not lose track of resources.

---

# 38. IAM

IAM means Identity and Access Management.

It controls:

```text
Who can do what
to which AWS resources
```

Important concepts:

- users
- groups
- roles
- policies
- permissions

The assignment requires root MFA and an IAM user for daily work.

---

# 39. Root User vs IAM User

The AWS root user has extremely powerful permissions.

Use root primarily for account-level actions such as setting up root MFA.

For daily operations, use the IAM identity requested by the assignment.

Never put root credentials or access keys in Git.

---

# 40. AWS Budget

A budget helps detect unexpected spending.

Important distinction:

```text
Budget ≠ hard spending limit
```

It provides alerts based on configured thresholds.

The assignment requires alerts at:

```text
50%
80%
100%
```

---

# 41. Public IP

EC2 needs a reachable public address for your application demo.

Concept:

```text
Phone on mobile data
       ↓
Internet
       ↓
EC2 public IP
       ↓
Security Group
       ↓
Application
```

This is why the project cannot be tested only from your local Fedora machine.

---

# 42. AWS CLI

AWS CLI allows command-line interaction with AWS.

Example:

```bash
aws sts get-caller-identity
```

This asks AWS:

> Which identity am I currently authenticated as?

It is a useful sanity check.

---

# 43. Git

Git tracks changes to your project.

Important concepts:

```text
working tree
staging area
commit
branch
remote
```

Typical flow:

```text
edit
 ↓
git add
 ↓
git commit
 ↓
git push
```

A commit is a snapshot of changes.

---

# 44. GitHub

GitHub hosts your Git repository.

For this project GitHub is also the starting point for CI.

```text
Developer
   ↓
git push
   ↓
GitHub
   ↓
GitHub Actions
```

---

# 45. GitHub Actions

GitHub Actions is CI/CD automation.

CI means Continuous Integration.

The project's workflow should:

```text
push
 ↓
checkout
 ↓
test/lint
 ↓
build Docker image
 ↓
push image to GHCR
```

The important principle:

```text
if test fails
    ↓
stop
```

Do not build/publish a broken image.

---

# 46. GHCR

GHCR means GitHub Container Registry.

It stores Docker/OCI images associated with GitHub.

Example:

```text
ghcr.io/username/devpulse
```

Your workflow publishes:

```text
latest
```

and:

```text
commit SHA
```

---

# 47. Why SHA Image Tags Matter

Suppose:

```text
latest → image A
```

Later:

```text
latest → image B
```

You cannot tell from `latest` alone exactly which commit produced it.

A SHA tag gives you:

```text
commit abc123 → image abc123
```

This improves traceability and reproducibility.

---

# 48. CI vs CD

## CI

Build/test/validate code automatically.

```text
push
 ↓
test
 ↓
build
 ↓
publish
```

## CD

Automatically deploy the result.

```text
push
 ↓
build
 ↓
GHCR
 ↓
EC2
 ↓
pull
 ↓
restart
```

The assignment makes CD optional.

Finish CI first.

---

# 49. Prometheus

Prometheus is a **metrics monitoring and time-series database system**.

The core idea:

```text
targets expose metrics
          ↓
      Prometheus
          ↓
   stores time series
          ↓
      PromQL queries
```

It commonly uses a **pull/scrape model**.

Prometheus periodically requests a metrics endpoint.

For DevPulse:

```text
FastAPI /metrics
      ↓
Prometheus
```

---

# 50. What Is a Metric?

A metric is a numerical measurement about a system.

Examples:

```text
number of HTTP requests
CPU usage
memory usage
request duration
number of errors
```

A time-series metric has values associated with time.

Conceptually:

```text
10:00 → 100 requests
10:01 → 135 requests
10:02 → 180 requests
```

---

# 51. Prometheus Time Series

A metric can have labels.

Concept:

```text
http_requests_total
```

with labels such as:

```text
method="GET"
route="/services"
status="200"
```

This allows Prometheus to distinguish different dimensions.

Be careful with labels: uncontrolled/high-cardinality labels can create huge numbers of time series.

Do not use things like arbitrary user IDs as labels unless you have a strong reason.

---

# 52. Prometheus Counter

A counter represents a value that generally increases.

Example:

```text
http_requests_total
```

Concept:

```text
100
101
102
103
...
```

If the application restarts, the counter may reset.

PromQL functions such as `rate()` are designed to work with counters.

For DevPulse:

```text
requests per route
```

is a good counter.

---

# 53. Prometheus Gauge

A gauge can move up and down.

Examples:

```text
CPU usage
memory usage
active connections
```

Concept:

```text
40
55
48
70
35
```

Unlike a counter, it is not expected to only increase.

---

# 54. Prometheus Histogram

A histogram records observations into buckets.

Request duration is a classic example.

Instead of only saying:

```text
average = 200 ms
```

you can understand the distribution of request durations.

This helps calculate percentiles such as:

```text
p95
p99
```

The assignment specifically requires a histogram for request duration.

---

# 55. p95 Latency

p95 means approximately:

> 95% of observed requests are at or below this latency, while the slowest approximately 5% are above it.

Why it matters:

Average latency can hide slow requests.

Example:

```text
Most requests: 50 ms
Some requests: 2 seconds
```

The average might not communicate the tail behavior clearly.

p95 helps show tail latency.

---

# 56. PromQL

PromQL is Prometheus Query Language.

It lets you query metrics.

Conceptual examples:

```text
request rate
error rate
CPU usage
memory usage
latency
```

A useful PromQL query often combines:

- metric
- labels
- aggregation
- time windows
- rate calculations

Do not memorize queries blindly. Understand what each part is selecting and calculating.

---

# 57. Prometheus Scraping

A scrape is when Prometheus requests metrics from a target.

Example:

```text
Prometheus
   |
   | HTTP GET
   v
FastAPI /metrics
```

Prometheus then stores the returned samples.

If the target cannot be reached, the target can become:

```text
DOWN
```

---

# 58. cAdvisor

cAdvisor means **Container Advisor**.

It exposes container-level resource information.

Useful measurements include:

- container CPU
- container memory
- network activity
- filesystem information

Architecture:

```text
Docker containers
      ↓
   cAdvisor
      ↓
  Prometheus
      ↓
    Grafana
```

This lets you see what your containers are consuming.

---

# 59. node_exporter

node_exporter exposes Linux host metrics for Prometheus.

It can provide information about:

- CPU
- memory
- disk
- filesystem
- network
- load

Architecture:

```text
Ubuntu VM / EC2
      ↓
node_exporter
      ↓
Prometheus
```

Important distinction:

```text
node_exporter → host
cAdvisor      → containers
FastAPI       → application
```

---

# 60. Grafana

Grafana is primarily a visualization and dashboarding platform.

It reads data from sources such as Prometheus and displays it as:

- graphs
- gauges
- tables
- alerts
- dashboards

Architecture:

```text
FastAPI
   ↓
Prometheus
   ↓
Grafana
```

Grafana does not replace Prometheus.

Think:

```text
Prometheus = collects/stores/query metrics
Grafana    = visualizes them
```

---

# 61. Grafana Datasource

A datasource tells Grafana where its data comes from.

For DevPulse:

```text
Grafana
   ↓
Prometheus
```

You configure the Prometheus URL as the datasource.

---

# 62. Grafana Dashboard

A dashboard is a collection of visual panels.

Your four required panels:

```text
Request rate
Error rate
p95 latency
Container CPU + memory
```

A dashboard turns raw metrics into a human-readable operational view.

---

# 63. Dashboard as Code

The assignment wants the dashboard configuration stored in Git.

Instead of:

```text
manually click everything
```

you want:

```text
Git repository
   ↓
dashboard JSON
   ↓
Grafana provisioning
   ↓
dashboard recreated
```

This is an important DevOps principle:

> infrastructure and operational configuration should be reproducible.

---

# 64. Alerting

Monitoring answers:

> What is happening?

Alerting answers:

> When should I be notified?

Example:

```text
Application down for > 1 minute
```

Concept:

```text
healthy
  ↓
failure
  ↓
condition becomes true
  ↓
alert fires
```

When the condition becomes false again:

```text
alert resolves
```

---

# 65. Observability

Observability is broader than simply monitoring.

A common model uses:

```text
Metrics
Logs
Traces
```

For this project, you mainly implement:

```text
Metrics
```

Prometheus + Grafana provide the metrics side.

Your breakage log and container/application logs help with troubleshooting.

---

# 66. Monitoring vs Observability

### Monitoring

Usually focuses on known conditions:

```text
CPU > 90%
app down
error rate > 5%
```

### Observability

Focuses on understanding internal system behavior from external outputs.

A system with good observability helps you answer:

> Why is this happening?

For this assignment, you are building a small but useful observability layer.

---

# 67. Chaos Demonstration

Chaos does not mean randomly destroying everything.

Here you intentionally create one controlled failure:

```bash
docker stop <app-container>
```

Then observe:

```text
application unavailable
      ↓
Prometheus notices
      ↓
Grafana reflects condition
      ↓
alert fires
```

Then restore:

```bash
docker start <app-container>
```

and observe recovery.

The important lesson is:

> A monitoring system is only useful if it detects real failures.

---

# 68. Health Check vs Metrics

These are different.

## Health endpoint

```text
/healthz
```

answers:

> Is the application healthy enough to serve traffic?

## Metrics endpoint

```text
/metrics
```

answers:

> What is the application doing and how is it behaving?

You need both.

---

# 69. Application Health vs Container Health

A container can be running while the application is broken.

Example:

```text
container = running
FastAPI = crashed
```

or:

```text
FastAPI = running
PostgreSQL = unavailable
```

Therefore:

```text
HEALTHCHECK
```

should test meaningful application health.

For DevPulse, database reachability is part of `/healthz`.

---

# 70. Logs

Logs record events.

Examples:

```text
application started
database connection failed
request received
exception occurred
```

Metrics tell you **how much/how often**.

Logs can tell you **what happened**.

A useful debugging workflow is:

```text
Metric shows problem
      ↓
Inspect logs
      ↓
Reproduce
      ↓
Find root cause
```

---

# 71. Reverse Proxy Headers

When a proxy sits in front of an application, the application may otherwise see the proxy's internal IP.

Headers such as:

```text
X-Forwarded-For
X-Forwarded-Proto
```

can communicate information about the original request.

This is particularly important in Track A, but understanding it is useful when using Nginx.

---

# 72. Git Secrets

Never commit:

```text
.env
.pem
private keys
AWS secret access keys
passwords
tokens
```

Deleting a secret later is not enough because Git history can preserve it.

Use:

```text
.gitignore
```

and a secret scanner such as:

```text
gitleaks
```

---

# 73. gitleaks

gitleaks scans Git repositories for patterns that look like secrets.

The important concept is:

```text
current files
+
Git history
```

You want to ensure credentials never entered the repository history.

---

# 74. AWS Security Group vs UFW

These are two different firewall layers.

```text
Internet
   ↓
AWS Security Group
   ↓
EC2 network interface
   ↓
UFW
   ↓
Docker networking
   ↓
Container
```

If the AWS security group blocks port 80, changing UFW will not fix it.

If AWS allows port 80 but UFW blocks it, the application still won't be reachable.

This layered model is extremely useful during debugging.

---

# 75. Docker Port Publishing

Suppose:

```text
container port = 8000
host port = 8080
```

Then:

```text
host:8080
    ↓
container:8000
```

The two numbers do not have to be the same.

For example:

```text
-p 8080:8000
```

means:

```text
HOST:CONTAINER
```

Understanding this is essential for Docker networking.

---

# 76. Database Port

PostgreSQL normally listens on:

```text
5432
```

Inside Compose, the application can use:

```text
postgres:5432
```

You generally do not need to expose PostgreSQL to the public internet.

This is a good security principle:

> Only expose services that external clients actually need.

---

# 77. Persistent Data

There are three different things to distinguish:

```text
container
image
volume
```

### Image

Application template.

### Container

Running instance.

### Volume

Persistent data.

So:

```text
PostgreSQL image
       ↓
PostgreSQL container
       ↓
PostgreSQL volume
```

Deleting the container does not necessarily delete the volume.

---

# 78. Dependency Health

`depends_on` with a health condition is useful because:

```text
Postgres container started
```

does not necessarily mean:

```text
Postgres ready for connections
```

A healthcheck lets Compose distinguish these states.

---

# 79. EC2 Memory Constraint

The assignment uses a 1 GB EC2 instance.

This matters.

Your application stack contains:

```text
FastAPI
PostgreSQL
Nginx
Prometheus
Grafana
cAdvisor
node_exporter
```

These consume memory.

If the EC2 build becomes unstable, possible causes include:

- insufficient memory
- Docker build memory consumption
- Grafana/Prometheus overhead
- too many concurrent processes

The assignment specifically warns that a 1 GB instance is not much memory.

This is why building the image in GitHub Actions and pulling it from GHCR is useful.

---

# 80. CI Build vs EC2 Build

A good architecture is:

```text
GitHub Actions
      ↓
build image
      ↓
GHCR
      ↓
EC2 pulls image
```

instead of making the small EC2 machine perform every expensive build.

This also gives you:

```text
reproducible image
+
versioned artifact
+
faster deployment
```

---

# 81. Immutable Image Idea

Instead of thinking:

```text
EC2 builds whatever is currently in source
```

think:

```text
Git commit
    ↓
CI
    ↓
image SHA
    ↓
registry
    ↓
EC2
```

This creates traceability:

```text
application version
      ↕
Git commit
      ↕
Docker image
      ↕
deployment
```

This is a valuable DevOps concept.

---

# 82. Continuous Deployment

Optional bonus.

CI:

```text
build + test + publish
```

CD:

```text
deploy
```

A possible flow:

```text
git push
   ↓
GitHub Actions
   ↓
test
   ↓
build
   ↓
GHCR
   ↓
SSH EC2
   ↓
pull image
   ↓
docker compose up -d
   ↓
health check
```

The deployment script should fail if the health check fails.

---

# 83. Terraform

Terraform is Infrastructure as Code.

Instead of clicking:

```text
EC2 console
→ launch
→ security group
→ instance
```

you describe infrastructure in code.

Concept:

```text
Terraform configuration
          ↓
Terraform
          ↓
AWS resources
```

Benefits:

- reproducibility
- version control
- reviewable infrastructure
- automation

For this assignment it is a bonus, not a reason to delay the core project.

---

# 84. Makefile

A Makefile can provide convenient project commands.

Example:

```text
make up
make down
make logs
make test
make build
```

This is useful because common operational actions become standardized.

It is optional bonus functionality.

---

# 85. Troubleshooting Mental Model

When something doesn't work, do not immediately change random settings.

Follow the path:

```text
Client
 ↓
DNS?
 ↓
Internet?
 ↓
AWS Security Group?
 ↓
EC2?
 ↓
UFW?
 ↓
Docker port?
 ↓
Nginx?
 ↓
FastAPI?
 ↓
Database?
```

For monitoring:

```text
Application
 ↓
/metrics
 ↓
Prometheus target
 ↓
Prometheus query
 ↓
Grafana datasource
 ↓
Dashboard
 ↓
Alert
```

Debug one layer at a time.

---

# 86. Common Failure: SSH

Symptom:

```text
ssh connection refused
```

Check:

```text
Is VM running?
 ↓
Correct IP?
 ↓
Correct port?
 ↓
Port forwarding?
 ↓
sshd running?
 ↓
UFW?
 ↓
SSH key?
```

Do not immediately reinstall Ubuntu.

---

# 87. Common Failure: App Cannot Reach PostgreSQL

Likely mistake:

```text
DATABASE_HOST=localhost
```

inside the app container.

Correct Compose concept:

```text
DATABASE_HOST=postgres
```

because `postgres` is the service name.

---

# 88. Common Failure: Database Data Disappears

Check:

```text
Is there a named volume?
```

Then check whether you ran:

```bash
docker compose down -v
```

The `-v` flag removes volumes.

---

# 89. Common Failure: Works Locally but Not EC2

Check in this order:

```text
container running?
 ↓
docker compose ps
 ↓
application logs
 ↓
container port
 ↓
EC2 security group
 ↓
UFW
 ↓
public IP
```

Do not assume the application is broken.

Networking is often the problem.

---

# 90. Common Failure: Prometheus Target Down

Check:

```text
Prometheus target address
 ↓
service name
 ↓
port
 ↓
/metrics endpoint
 ↓
Compose network
```

Common mistake:

```text
localhost
```

when Prometheus needs to contact another container.

---

# 91. Common Failure: Grafana Has No Data

Check:

```text
Prometheus running?
 ↓
Prometheus target UP?
 ↓
PromQL query works?
 ↓
Grafana datasource correct?
 ↓
Dashboard query correct?
```

Debug from the source outward.

---

# 92. Common Failure: Alert Does Not Fire

Check:

```text
metric exists?
 ↓
PromQL expression returns expected value?
 ↓
alert rule loaded?
 ↓
evaluation interval?
 ↓
for duration?
 ↓
Grafana/Prometheus alert state?
```

Do not change five things at once.

---

# 93. Important Commands to Understand

## Linux

```bash
ip a
ip route
ss -tulpn
systemctl status <service>
journalctl -u <service>
sudo ufw status
df -h
free -h
ps aux
```

## Docker

```bash
docker ps
docker images
docker logs <container>
docker exec -it <container> sh
docker inspect <container>
docker network ls
docker volume ls
```

## Compose

```bash
docker compose up -d
docker compose down
docker compose ps
docker compose logs
docker compose logs -f
docker compose config
docker compose down -v
```

## Git

```bash
git status
git add
git commit
git log
git branch
git push
```

## AWS

```bash
aws sts get-caller-identity
```

---

# 94. Concepts You Should Be Able to Explain in the Viva

Before submitting, make sure you can answer:

### Linux

- What is a process?
- What is systemd?
- What is cron?
- What does UFW do?
- Why disable root SSH?
- Why use SSH keys?
- What is a private IP?
- What is a public IP?
- What is a port?
- What happens during DNS lookup?

### Docker

- Image vs container?
- Dockerfile vs Compose?
- Why multi-stage builds?
- Why non-root?
- Why `.dockerignore`?
- What is a healthcheck?
- What is a named volume?
- What is a bridge network?
- Why does `localhost` mean something different inside a container?

### AWS

- What is EC2?
- What is a security group?
- Security group vs UFW?
- Why restrict SSH to `/32`?
- What is IAM?
- Why root MFA?
- Why use an IAM identity?
- What is an AWS region?
- Why configure a budget?

### CI/CD

- What is CI?
- What is CD?
- Why use GHCR?
- Why tag with commit SHA?
- Why should tests run before Docker build?
- Why is automated deployment useful?

### Prometheus

- What is a metric?
- What is a time series?
- What is scraping?
- Pull vs push?
- Counter vs gauge?
- What is a histogram?
- What is p95?
- What is PromQL?
- What is a label?
- What is high cardinality?

### Grafana

- What does Grafana do?
- What is a datasource?
- Why use Prometheus as datasource?
- What is a dashboard?
- Why provision dashboards as code?

### Observability

- Metrics vs logs?
- What does cAdvisor measure?
- What does node_exporter measure?
- What does application instrumentation measure?
- How does an alert work?
- What happens when you kill the application?

---

# 95. The Most Important Mental Model

Do not memorize the project as a list of tools.

Understand the request path.

## User request

```text
Browser
   ↓
Internet
   ↓
AWS public IP
   ↓
Security Group
   ↓
EC2
   ↓
UFW
   ↓
Docker port
   ↓
Nginx
   ↓
FastAPI
   ↓
PostgreSQL
```

## Monitoring path

```text
FastAPI
   ↓
/metrics
   ↓
Prometheus
   ↓
PromQL
   ↓
Grafana
```

## Container monitoring

```text
Containers
   ↓
cAdvisor
   ↓
Prometheus
   ↓
Grafana
```

## Host monitoring

```text
Ubuntu/EC2
   ↓
node_exporter
   ↓
Prometheus
   ↓
Grafana
```

## Deployment path

```text
Developer
   ↓
Git
   ↓
GitHub
   ↓
GitHub Actions
   ↓
Docker image
   ↓
GHCR
   ↓
EC2
   ↓
Docker Compose
   ↓
Application
```

If you understand these four paths, you understand most of the project.

---

# 96. Final Learning Goal

By the end, you should be able to explain this sentence in your own words:

> "I wrote a small FastAPI application backed by PostgreSQL, containerized it using a multi-stage non-root Docker image, ran it with Docker Compose alongside Nginx and an observability stack, hardened an Ubuntu server with SSH keys and UFW, deployed the same stack to AWS EC2 behind a security group, built and published versioned images using GitHub Actions and GHCR, instrumented the application with Prometheus metrics, visualized application/container/host behavior in Grafana, and demonstrated automated detection and recovery from an intentional application failure."

That understanding is much more valuable than memorizing individual commands.
