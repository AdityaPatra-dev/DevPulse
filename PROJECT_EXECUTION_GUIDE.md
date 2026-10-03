# DevPulse — Complete Project Execution & Cloud Learning Guide

> **Track:** Track B — Watch It  
> **Host OS:** Fedora Linux  
> **Local Hypervisor:** KVM / Virtual Machine Manager (`virt-manager`)  
> **Local Guest OS:** Ubuntu Live Server 26  
> **Cloud Provider:** AWS EC2 `t3.micro` (`ap-south-1` Mumbai)  

This guide provides the exact step-by-step roadmap to complete every stage of the DevPulse project, with a deep focus on the **hands-on Linux, KVM, Docker, AWS Cloud, CI/CD, and Track B Observability** requirements.

---

## Table of Contents
1. [Git Commit Strategy (Spread across 6+ Days)](#1-git-commit-strategy)
2. [Stage 1: Verify the Application & Docker Locally (Fedora Host)](#2-stage-1-verify-application--docker-locally)
3. [Stage 2: Local Linux Administration (KVM + Ubuntu Live Server 26)](#3-stage-2-local-linux-administration-kvm--ubuntu-live-server-26)
4. [Stage 3: AWS Cloud Setup (Budget, MFA, IAM, Security Groups)](#4-stage-3-aws-cloud-setup)
5. [Stage 4: Deploying to AWS EC2](#5-stage-4-deploying-to-aws-ec2)
6. [Stage 5: GitHub Actions CI/CD & GHCR](#6-stage-5-github-actions-cicd--ghcr)
7. [Stage 6: Track B Observability & Chaos Experiment](#7-stage-6-track-b-observability--chaos-experiment)
8. [Stage 7: Evidence Collection, Report & Demo Video](#8-stage-7-evidence-collection-report--demo-video)
9. [Stage 8: Final Teardown](#9-stage-8-final-teardown)

---

## 1. Git Commit Strategy

### Mandatory Rules
- **At least 15 meaningful commits** (target ~20 commits).
- **Commits spread across at least 6 different days**.
- **Zero secrets in Git history** (never commit `.env`, `*.pem`, or AWS credentials).

### Suggested Commit Roadmap

| Day | Commit Message | Files Affected / Milestone |
| :--- | :--- | :--- |
| **Day 1** | `feat: initialize DevPulse application models and config` | `app/config.py`, `app/database.py`, `app/models.py`, `app/schemas.py` |
| **Day 1** | `feat: implement services, incidents, and healthz API routes` | `app/routes/*`, `app/main.py` |
| **Day 2** | `feat: add Track B Prometheus metrics middleware and endpoint` | `app/metrics.py` |
| **Day 2** | `feat: add minimal web dashboard UI and client assets` | `app/static/*` |
| **Day 3** | `test: add pytest unit test suite for API endpoints` | `tests/test_api.py`, `requirements-dev.txt` |
| **Day 3** | `docker: create multi-stage Dockerfile and .dockerignore` | `Dockerfile`, `.dockerignore` |
| **Day 4** | `compose: create Docker Compose stack with postgres and nginx` | `docker-compose.yml`, `nginx/nginx.conf` |
| **Day 4** | `monitoring: configure Prometheus, Grafana dashboards, and exporters` | `monitoring/*` |
| **Day 5** | `ops: add systemd maintenance service and disk monitor cron scripts` | `scripts/*` |
| **Day 5** | `ci: configure GitHub Actions workflow for lint, test, and GHCR` | `.github/workflows/ci.yml` |
| **Day 6** | `docs: update project README and execution documentation` | `README.md`, guides |
| **Day 6** | `test: simulate intentional CI test failure for pipeline validation` | Intentional break in test |
| **Day 6** | `fix: resolve test failure and demonstrate green CI run` | Fix test |
| **Day 7** | `deploy: configure production environment templates and Makefile` | `Makefile`, `.env.example` |
| **Day 8** | `docs: add live EC2 endpoint, architecture diagram, and evidence links`| `README.md` |

---

## 2. Stage 1: Verify Application & Docker Locally

Run these checks on your Fedora host machine to verify the codebase before moving to VM and Cloud:

### 2.1 Set Up Environment
```bash
cp .env.example .env
```

### 2.2 Build the Docker Image
```bash
docker build -t devpulse-app:local .
```

Verify requirements:
1. **Image size < 250 MB:**
   ```bash
   docker images devpulse-app:local
   # SIZE should show ~180MB (well below 250MB)
   ```
2. **Non-root user verification:**
   ```bash
   docker run --rm devpulse-app:local whoami
   # Must output: appuser (NOT root)
   ```
3. **Container healthcheck:**
   ```bash
   docker run -d --name devpulse-test -p 8000:8000 devpulse-app:local
   sleep 12
   docker inspect --format='{{json .State.Health.Status}}' devpulse-test
   # Must output: "healthy"
   docker stop devpulse-test && docker rm devpulse-test
   ```

### 2.3 Test the Full Docker Compose Stack
```bash
docker compose up -d
docker compose ps
```

Verify services running:
- `devpulse_app` (Up / Healthy)
- `devpulse_postgres` (Up / Healthy)
- `devpulse_nginx` (Up on port 80)
- `devpulse_prometheus` (Up on port 9090)
- `devpulse_grafana` (Up on port 3000)
- `devpulse_cadvisor` (Up on port 8080)
- `devpulse_node_exporter` (Up on port 9100)

### 2.4 Verify Database Persistence
```bash
# 1. Add a service via curl
curl -X POST http://localhost/services \
  -H "Content-Type: application/json" \
  -d '{"name": "Auth API", "url": "https://auth.devpulse.local"}'

# 2. Check service exists
curl http://localhost/services

# 3. Stop stack WITHOUT deleting volumes
docker compose down

# 4. Restart stack
docker compose up -d

# 5. Verify service is STILL there (confirms named volume persistence)
curl http://localhost/services
```

---

## 3. Stage 2: Local Linux Administration (KVM + Ubuntu Live Server 26)

This stage fulfills all assignment requirements for hypervisor configuration, Linux systems administration, security hardening, systemd, and cron.

### 3.1 Install KVM & Virtual Machine Manager on Fedora
```bash
sudo dnf install -y @virtualization virt-manager libvirt-client
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt $USER
```
*(Log out and log back in so group permissions take effect)*

### 3.2 Create the Virtual Machine
1. Open **Virtual Machine Manager** (`virt-manager`).
2. Click **Create a new virtual machine** -> **Local install media** -> browse to the `Ubuntu Live Server 26` ISO.
3. Configure VM specs:
   - **RAM:** 4096 MB (4 GB)
   - **CPUs:** 2 vCPU
   - **Storage:** 25 GB disk
   - **Network:** Default NAT network (`virbr0`)
4. Complete standard Ubuntu Server installation:
   - Name your primary user (e.g. `aditya`).
   - Enable OpenSSH Server during setup.

### 3.3 Take the Base VM Snapshot (CRITICAL)
Before changing any SSH or network settings, create a clean snapshot:
```bash
# In virt-manager GUI: Open VM window -> Manage VM Snapshots -> + Create Snapshot
# Or via CLI on Fedora:
virsh snapshot-create-as --domain <vm-name> --name clean-ubuntu-base --description "Clean base snapshot"
```
*(Screenshot this snapshot in virt-manager for assignment evidence)*

### 3.4 Configure Static IP with Netplan (Inside Ubuntu VM)
Check interface name:
```bash
ip a
# Assume interface is ens3 or enp1s0
```

Edit Netplan configuration:
```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```
Configure static IP matching your `virbr0` subnet (e.g., `192.168.122.50/24`):
```yaml
network:
  version: 2
  ethernets:
    enp1s0:
      dhcp4: no
      addresses:
        - 192.168.122.50/24
      routes:
        - to: default
          via: 192.168.122.1
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
```

Apply and verify:
```bash
sudo netplan try
sudo netplan apply
ip a
sudo reboot
# Verify the IP persists after reboot
```

### 3.5 SSH Key Authentication & Hardening
1. On your **Fedora host**, generate an ed25519 SSH keypair:
   ```bash
   ssh-keygen -t ed25519 -C "devpulse-local-vm" -f ~/.ssh/id_ed25519_devpulse
   ```
2. Copy the public key to the Ubuntu VM:
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519_devpulse.pub aditya@192.168.122.50
   ```
3. Test key login from Fedora:
   ```bash
   ssh -i ~/.ssh/id_ed25519_devpulse aditya@192.168.122.50
   ```
4. **Harden SSH** on the VM:
   Edit `/etc/ssh/sshd_config`:
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
   Set:
   ```text
   Port 2222
   PasswordAuthentication no
   PermitRootLogin no
   PubkeyAuthentication yes
   ```
5. Restart SSH daemon:
   ```bash
   sudo systemctl restart ssh
   ```
6. **Do NOT close your existing terminal session!** Open a new terminal on Fedora and test:
   ```bash
   ssh -i ~/.ssh/id_ed25519_devpulse -p 2222 aditya@192.168.122.50
   ```

### 3.6 UFW Firewall
Inside the Ubuntu VM:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp comment 'Hardened SSH Port'
sudo ufw allow 80/tcp comment 'HTTP Web'
sudo ufw enable
sudo ufw status verbose
```
*(Screenshot `sudo ufw status verbose`)*

### 3.7 Linux Users, Groups & Permissions
Inside the Ubuntu VM:
```bash
# 1. Create deployment user
sudo adduser deploy --gecos "" --disabled-password

# 2. Create project group
sudo groupadd devpulse

# 3. Add users to devpulse group
sudo usermod -aG devpulse $USER
sudo usermod -aG devpulse deploy

# 4. Create project directory
sudo mkdir -p /opt/devpulse

# 5. Set ownership and SGID bit
sudo chown -R $USER:devpulse /opt/devpulse
sudo chmod -R 2775 /opt/devpulse

# 6. Verify permissions
ls -ld /opt/devpulse
# Must show: drwxrwsr-x (2775: SetGID ensures new files inherit the devpulse group)
```

### 3.8 systemd Custom Service
Copy `scripts/devpulse_maintenance.sh` to `/opt/devpulse/scripts/devpulse_maintenance.sh`:
```bash
sudo mkdir -p /opt/devpulse/scripts
sudo cp scripts/devpulse_maintenance.sh /opt/devpulse/scripts/
sudo chmod +x /opt/devpulse/scripts/devpulse_maintenance.sh

# Copy service unit
sudo cp scripts/devpulse-maintenance.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable devpulse-maintenance
sudo systemctl start devpulse-maintenance
sudo systemctl status devpulse-maintenance
```

**Demonstrate Auto-restart:**
```bash
# Find PID
ps aux | grep devpulse_maintenance.sh
# Kill process
sudo kill -9 <PID>
# Check status - systemd will have restarted it immediately
sudo systemctl status devpulse-maintenance
```
*(Screenshot showing PID restart)*

### 3.9 Cron Job
Configure disk monitoring:
```bash
sudo cp scripts/disk_monitor.sh /opt/devpulse/scripts/
sudo chmod +x /opt/devpulse/scripts/disk_monitor.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/devpulse/scripts/disk_monitor.sh") | crontab -

# Verify crontab
crontab -l
# Wait 5 minutes and check log output
cat /var/log/devpulse_disk_usage.log
```

### 3.10 Networking Evidence
Run and screenshot each command inside the VM:
```bash
ip a
ss -tulpn
ping -c 4 8.8.8.8
traceroute 8.8.8.8
dig google.com
```

---

## 4. Stage 3: AWS Cloud Setup

This is the cloud environment where the real deployment lives.

### 4.1 Root MFA & Security
1. Log in to AWS Console with Root account.
2. Go to **IAM Dashboard** -> Enable **MFA for Root user** (use Google Authenticator or 1Password).
3. *(Screenshot showing Root MFA enabled)*.

### 4.2 Create AWS Budget (MANDATORY BEFORE EC2)
1. Go to **AWS Budgets** in AWS Console.
2. Click **Create budget** -> **Cost budget - Recommended**.
3. Name: `devpulse-zero-spend-budget`.
4. Budgeted amount: `$5.00` (or `$0.01` for zero-spend tracking).
5. Set alert thresholds:
   - **50% of budgeted amount** -> Send email to your personal address.
   - **80% of budgeted amount** -> Send email.
   - **100% of budgeted amount** -> Send email.
6. *(Screenshot showing the budget with alert thresholds)*.

### 4.3 Create IAM User for Daily Work
1. Go to **IAM** -> **Users** -> **Create user**.
2. Username: `aditya-devops`.
3. Attach policies: `AdministratorAccess` (or custom EC2/VPC admin policy).
4. Create **Access Keys** for CLI access (save CSV securely).
5. Configure AWS CLI on Fedora:
   ```bash
   aws configure
   # Enter Access Key ID, Secret Access Key, Region: ap-south-1, Output: json
   ```
6. Verify identity:
   ```bash
   aws sts get-caller-identity
   ```
   *(Screenshot of `aws sts get-caller-identity` showing your IAM user)*.

### 4.4 EC2 Key Pair
1. Go to **EC2** -> **Key Pairs** -> **Create key pair**.
2. Name: `devpulse-ec2-key`.
3. Type: `ED25519` (or `RSA`), File format: `.pem`.
4. Save file to Fedora:
   ```bash
   chmod 400 ~/devpulse-ec2-key.pem
   ```

### 4.5 EC2 Security Group
Create Security Group named `devpulse-ec2-sg` in `ap-south-1`:
- **Inbound Rules:**
  1. **SSH:** Port `22`, Source: `My IP` (`<YOUR_PUBLIC_IP>/32`) — **NEVER 0.0.0.0/0**!
  2. **HTTP:** Port `80`, Source: `0.0.0.0/0` (Allows public access to web app)
  3. **Grafana:** Port `3000`, Source: `<YOUR_PUBLIC_IP>/32` (Allows evaluator to view dashboard)
  4. **Prometheus:** Port `9090`, Source: `<YOUR_PUBLIC_IP>/32` (Optional for debug)
- **Outbound Rules:**
  - All traffic to `0.0.0.0/0`.
*(Screenshot of Security Group inbound rules showing the restricted /32 SSH rule)*.

### 4.6 Launch the EC2 Instance
1. Go to **EC2** -> **Launch Instances**.
2. Name: `devpulse-production`.
3. AMI: **Ubuntu Server 24.04 LTS** (Free tier eligible).
4. Instance type: **t3.micro** (Free tier eligible, 1 vCPU, 1 GB RAM).
5. Key pair: `devpulse-ec2-key`.
6. Network settings: Select `devpulse-ec2-sg`.
7. Storage: 20 GB gp3.
8. Click **Launch instance**.
9. Note down the **Public IPv4 Address** of your instance.

---

## 5. Stage 4: Deploying to AWS EC2

### 5.1 Connect via SSH
```bash
ssh -i ~/devpulse-ec2-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### 5.2 Set Up Swap Space (Crucial for 1 GB RAM t3.micro)
Because `t3.micro` only has 1 GB RAM, building or running multiple containers alongside monitoring can cause OOM. Add 2 GB swap:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

### 5.3 Install Docker Engine & Compose on EC2
```bash
# Update and install dependencies
sudo apt update && sudo apt install -y ca-certificates curl gnupg git

# Add Docker official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add ubuntu user to docker group
sudo usermod -aG docker $USER
newgrp docker
docker --version
docker compose version
```

### 5.4 Deploy the DevPulse Application
```bash
# Clone your repository
git clone https://github.com/AdityaPatra-dev/DevPulse.git
cd DevPulse

# Create .env on EC2 (DO NOT commit this file to git)
cp .env.example .env

# Start the full stack
docker compose up -d

# Verify all containers are running
docker compose ps
```
*(Screenshot `docker compose ps` on EC2)*.

### 5.5 Test Public Access
1. Open your web browser on your phone using **cellular/mobile data** (disconnected from your home Wi-Fi).
2. Browse to: `http://<EC2_PUBLIC_IP>`
3. You should see the DevPulse dashboard with `System Healthy (DB: connected)`.
4. Add a test service (e.g., "Payment Gateway") and report an incident.
5. *(Screenshot showing mobile browser loading http://<EC2_PUBLIC_IP> with the working app)*.

### 5.6 Document Local KVM vs EC2 Differences
Record at least 3 genuine differences for your final report:
1. **Memory:** Local KVM VM has 4 GB RAM; EC2 `t3.micro` has only 1 GB RAM (requiring a 2GB swapfile to prevent OOM errors during container startup).
2. **OS Distribution:** Local VM is Ubuntu Live Server 26 on KVM (`x86_64`), while EC2 runs Ubuntu 24.04 LTS official AWS AMI.
3. **Network Ingress:** Local VM relies on KVM NAT `virbr0` with internal routing, whereas EC2 uses AWS Internet Gateway and AWS Security Groups with public IPv4 allocation.

---

## 6. Stage 5: GitHub Actions CI/CD & GHCR

### 6.1 Set Package Visibility to Public on GitHub
1. After the first CI push completes, navigate to your GitHub Profile -> **Packages** -> `devpulse`.
2. Package Settings -> Change visibility to **Public** (so the image can be pulled without docker login credentials).

### 6.2 Validate GHCR Tags
In GitHub Packages, confirm the image has two tags:
- `latest`
- `<commit-sha>` (e.g., `a7566dc...`)
*(Screenshot showing both tags in GHCR)*.

### 6.3 Demonstrate Broken and Green CI Runs (MANDATORY REQUIREMENT)
1. **Simulate a broken test:**
   Edit `tests/test_api.py` and modify an assertion to fail:
   ```python
   # In test_healthz:
   assert response.status_code == 500  # Intentionally wrong
   ```
2. Commit and push:
   ```bash
   git commit -am "test: introduce intentional test failure for CI demonstration"
   git push origin main
   ```
3. Go to GitHub Actions tab. Show the **RED** run failed at the `Run Pytest Suite` step, preventing the `Docker Build & GHCR Push` stage from ever running.
4. *(Screenshot the red run)*.
5. **Fix the test:**
   Restore `assert response.status_code == 200`.
6. Commit and push:
   ```bash
   git commit -am "fix: restore passing health check test"
   git push origin main
   ```
7. Go to GitHub Actions tab. Show the **GREEN** run completing both `test` and `build-and-push` jobs.
8. *(Screenshot the green run)*.

---

## 7. Stage 6: Track B Observability & Chaos Experiment

### 7.1 Access Grafana
Browse to: `http://<EC2_PUBLIC_IP>:3000` (or `http://localhost:3000` locally).  
Credentials:
- Username: `admin`
- Password: `devpulse_admin`

Go to **Dashboards** -> Open **DevPulse Track B — Observability Dashboard**.

Verify all 4 panels display live metrics:
1. **HTTP Request Rate (req/sec)** (Prometheus metric `http_requests_total`)
2. **HTTP Error Rate (%)**
3. **p95 Request Latency (seconds)** (`http_request_duration_seconds`)
4. **Container CPU & Memory Utilization** (cAdvisor metrics)

*(Screenshot all 4 panels running)*.

### 7.2 Execute the Chaos Experiment
Demonstrate system resilience and observability:

1. **Baseline:** Open Grafana dashboard on one side and terminal on the other. Generate some traffic:
   ```bash
   for i in {1..20}; do curl -s http://localhost/services > /dev/null; sleep 0.2; done
   ```
2. **Trigger Outage:** Stop the FastAPI backend container:
   ```bash
   docker stop devpulse_app
   ```
3. **Observe Breakdown:**
   - In Prometheus (`http://<IP>:9090/targets`), the `devpulse-app` target status changes from `UP` to `DOWN`.
   - In Grafana, the request rate drops to zero.
   - The alert fires (`up{job="devpulse-app"} == 0` for 1 minute).
   - *(Screenshot showing target DOWN and alert firing in Grafana/Prometheus)*.
4. **Recovery:** Restart the container:
   ```bash
   docker start devpulse_app
   ```
5. **Observe Healing:**
   - In Prometheus, target state recovers to `UP`.
   - Healthcheck `/healthz` responds `healthy` again.
   - Alert resolves in Grafana.
   - *(Screenshot showing recovery)*.

---

## 8. Stage 7: Evidence Collection, Report & Demo Video

### 8.1 Evidence Screenshots Checklist
Save all screenshots in `docs/screenshots/` with descriptive names:

- [ ] `01_kvm_vm_configuration.png` (virt-manager VM details: 2 vCPU, 4GB RAM)
- [ ] `02_kvm_snapshot.png` (virt-manager showing `clean-ubuntu-base` snapshot)
- [ ] `03_ubuntu_static_ip.png` (`ip a` and `netplan` config)
- [ ] `04_ssh_key_login.png` (Fedora terminal logging into VM via SSH key without password on port 2222)
- [ ] `05_ufw_status.png` (`sudo ufw status verbose` on VM)
- [ ] `06_systemd_restart.png` (Killing process and showing systemd auto-restart)
- [ ] `07_cron_log.png` (`cat /var/log/devpulse_disk_usage.log`)
- [ ] `08_networking_evidence.png` (`ping`, `traceroute`, `ss -tulpn`, `dig`)
- [ ] `09_docker_image_size.png` (`docker images` showing devpulse under 250 MB)
- [ ] `10_docker_non_root.png` (`docker run devpulse whoami` showing `appuser`)
- [ ] `11_compose_persistence.png` (Data persists after `docker compose down` and `docker compose up -d`)
- [ ] `12_aws_budget.png` (AWS Console showing $5 budget with 50%, 80%, 100% email alerts)
- [ ] `13_aws_root_mfa.png` (IAM dashboard showing Root user MFA active)
- [ ] `14_aws_iam_identity.png` (`aws sts get-caller-identity` in terminal)
- [ ] `15_aws_security_group.png` (Inbound rules showing SSH restricted to `/32`)
- [ ] `16_ec2_docker_ps.png` (`docker compose ps` on EC2)
- [ ] `17_public_mobile_access.png` (Screenshot of mobile phone on 4G/5G loading `http://<EC2_IP>`)
- [ ] `18_ci_red_run.png` (GitHub Actions tab showing red failed run)
- [ ] `19_ci_green_run.png` (GitHub Actions tab showing green successful run)
- [ ] `20_ghcr_tags.png` (GHCR package showing both `latest` and commit-SHA tags)
- [ ] `21_grafana_dashboard.png` (Grafana showing all 4 required Track B panels)
- [ ] `22_chaos_alert_firing.png` (Grafana/Prometheus showing app down alert firing during `docker stop`)
- [ ] `23_chaos_recovery.png` (Grafana showing metric recovery after `docker start`)
- [ ] `24_ec2_teardown.png` (AWS EC2 console showing 0 running instances after termination)

### 8.2 Demo Video (5–10 Minutes)
Script outline:
1. **0:00 - 1:00:** Introduce yourself, roll number, project name, Track B declaration.
2. **1:00 - 2:30:** Local KVM VM demonstration: SSH key login on port 2222, `sudo ufw status`, `systemctl status devpulse-maintenance`.
3. **2:30 - 4:00:** Cloud EC2 & App: Show AWS Security Group with `/32` restriction, show `docker compose ps` on EC2, open `http://<EC2_IP>` in browser, create a service and incident.
4. **4:00 - 5:30:** CI/CD: Show GitHub Actions workflow runs (demonstrate the red run and the green run), show GHCR package tags.
5. **5:30 - 7:30:** Track B Observability: Open Grafana dashboard, explain the 4 panels (rate, errors, p95 latency, container CPU/RAM). Stop the app container, show Prometheus target drop & alert fire, restart app, show recovery.
6. **7:30 - 8:30:** Closing: Explain one genuine breakage you encountered and solved (e.g. 1GB RAM EC2 swap issue or Netplan formatting).

---

## 9. Stage 8: Final Teardown

**Only perform this AFTER your demo video is recorded and all screenshots are captured!**

```bash
# 1. On EC2: Stop containers and delete volumes
docker compose down -v

# 2. In AWS Console:
# - Go to EC2 Instances -> Select devpulse-production -> Instance State -> Terminate instance
# - Confirm Termination
# - Go to Elastic IPs -> Release any allocated Elastic IP (if created)
# - Go to Security Groups -> Delete devpulse-ec2-sg (after instance terminates)
# - Go to Key Pairs -> Delete devpulse-ec2-key
# - Check other AWS regions to verify 0 active resources
```

**Final Teardown Evidence:**
Take a screenshot of the AWS EC2 Dashboard showing **0 Running Instances**. Save to `docs/screenshots/24_ec2_teardown.png`.
