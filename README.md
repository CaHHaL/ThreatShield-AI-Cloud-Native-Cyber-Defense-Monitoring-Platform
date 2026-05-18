# 🛡️ ThreatShield AI — Cloud-Native Cyber Defense Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![AWS](https://img.shields.io/badge/AWS-EC2-orange.svg)
![Terraform](https://img.shields.io/badge/Terraform-IaC-purple.svg)

ThreatShield AI is a comprehensive, cloud-native cybersecurity monitoring and threat intelligence platform. It utilizes a network of honeypots to capture real-world attack telemetry, processes the data through a high-performance asynchronous backend, and visualizes live threats on a React-based SOC dashboard via WebSockets.

---

## ✨ Key Features
- **Active Defense Honeypots:** Deploys Cowrie (SSH/Telnet) and a custom Flask-based fake corporate web-login portal to trap attackers and capture telemetry.
- **Real-Time Data Pipeline:** An asynchronous FastAPI backend ingests honeypot logs instantly, utilizing WebSockets to stream live attacks to the frontend.
- **Threat Classification:** Automatically calculates threat severity scores, parses attacker commands, and maps IP addresses to geolocations using MaxMind GeoIP.
- **Modern SOC Dashboard:** A responsive, dark-themed React frontend featuring interactive Leaflet maps, Recharts timeline graphs, and live event feeds.
- **Infrastructure as Code (IaC):** 100% automated AWS EC2 provisioning using Terraform.
- **DevSecOps CI/CD:** Automated GitHub Actions pipeline featuring code linting, automated testing, and Aqua Security Trivy vulnerability scanning.
- **Observability Stack:** Fully integrated Prometheus and Grafana auto-provisioned dashboards for backend health and HTTP request monitoring.

---

## 🏗️ Architecture

1. **Frontend:** React, Vite, TailwindCSS (Hosted on Vercel Edge Network).
2. **Backend:** FastAPI, Python, SQLAlchemy AsyncIO, WebSockets.
3. **Database:** PostgreSQL.
4. **Honeypots:** Cowrie (SSH/Telnet), Flask (Web).
5. **Monitoring:** Prometheus, Grafana.
6. **Deployment:** Docker Compose, AWS EC2, Terraform.

---

## 🚀 Deployment Guide

This project is optimized for automated cloud deployment via Terraform on AWS.

### 1. Provision Infrastructure
Ensure you have the AWS CLI and Terraform installed and configured.
```bash
cd terraform
terraform init
terraform apply -var="key_name=your-aws-ssh-key" -var="aws_region=ap-south-1"
```
*Note: The EC2 instance utilizes a `userdata.sh` script to automatically install Docker, clone this repository, and spin up the entire backend container stack.*

### 2. Frontend Configuration
The frontend is designed to be deployed on Vercel. Because the AWS instance receives a dynamic IP, Vercel acts as a secure reverse proxy to the backend.

1. Deploy the `frontend/` directory to Vercel.
2. Update the `frontend/vercel.json` file with your new EC2 Public IP address.
3. Vercel will automatically route `/api/` and `/ws/` requests to your AWS instance, bypassing browser Mixed-Content restrictions.

---

## 🛡️ DevSecOps Pipeline
Every push to the `main` branch triggers the GitHub Actions pipeline (`.github/workflows/ci.yml`), which performs:
1. **Code Quality:** Python Ruff linting and React build checks.
2. **Integration Testing:** PyTest suite against an ephemeral PostgreSQL Docker container.
3. **Security Scanning:** Trivy filesystem scan looking for CRITICAL and HIGH vulnerabilities.
4. **Dry-Run Builds:** Validates all Dockerfiles prior to deployment.

---

## 💻 Local Development

To run the platform locally without AWS:

```bash
# 1. Clone the repository
git clone https://github.com/YourUsername/ThreatShield-AI.git
cd ThreatShield-AI

# 2. Setup environment variables
cp .env.example .env

# 3. Start backend services
docker compose up -d

# 4. Start the frontend
cd frontend
npm install
npm run dev
```

*The SOC Dashboard will be available at `http://localhost:5173`.*
