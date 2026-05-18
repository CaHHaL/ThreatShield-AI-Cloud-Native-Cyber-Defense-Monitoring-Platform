# 🛡️ ThreatShield AI

**Cloud-native cybersecurity monitoring & threat intelligence platform**

Real-time SOC dashboard powered by Cowrie SSH/Telnet honeypots, a fake corporate web-login honeypot, FastAPI backend, React frontend, and Prometheus/Grafana monitoring — all containerized with Docker Compose.

---

## 🏗️ Architecture

```
Browser → Frontend (Nginx:3000)
              ↕ HTTP/WS
         Backend (FastAPI:8000)
              ↕
         PostgreSQL:5432
              ↑
         Log Files (shared volume)
              ↑
    Cowrie:2222/2323 + Web-Login:8080

Prometheus:9090 → scrapes → Backend
Grafana:3001    → queries → Prometheus
```

## 🚀 Quick Start (Local Docker)

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Git

### 1. Clone & Configure

```bash
git clone <your-repo-url> ThreatShield-AI
cd ThreatShield-AI
cp .env.example .env
```

Edit `.env` — the defaults work for local development.

### 2. Start All Services

```bash
docker compose up -d
```

This starts 7 services:
| Service | URL | Description |
|---|---|---|
| Frontend | http://localhost:3000 | SOC Dashboard |
| Backend API | http://localhost:8000 | FastAPI + Swagger |
| API Docs | http://localhost:8000/docs | OpenAPI docs |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3001 | Dashboards (admin/ThreatShield2024!) |
| Web Login HP | http://localhost:8080 | Fake corporate portal |
| SSH Honeypot | localhost:2222 | Fake SSH server |
| Telnet HP | localhost:2323 | Fake Telnet server |

### 3. Seed Test Data (first run)

```bash
docker exec -it threatshield-backend python seed_data.py
```

This creates 60 synthetic attack sessions across 20 countries with realistic severity distribution.

### 4. Open Dashboard

Navigate to **http://localhost:3000** — you should see the full SOC dashboard.

---

## 🧪 Testing the Honeypots

### SSH Honeypot (Cowrie)
```bash
ssh -p 2222 root@localhost          # Try to connect (will be captured)
ssh -p 2222 admin@localhost         # Try another username
```

### Telnet Honeypot
```bash
telnet localhost 2323               # Fake Telnet (Linux/Mac/WSL)
```

### Web Login Honeypot
```bash
# Manual test
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=password123"

# Automated scanner simulation
for i in {1..10}; do
  curl -s -X POST http://localhost:8080/login \
    -d "username=admin&password=pass$i" > /dev/null
  echo "Attempt $i sent"
  sleep 0.5
done
```

### Watch Real-Time Ingestion
```bash
docker logs -f threatshield-backend  # See log parsing in action
```

---

## 📁 Project Structure

```
DevSecOps_2/
├── .env.example          # Environment template
├── .env                  # Local config (gitignored)
├── docker-compose.yml    # Full orchestration
├── .github/workflows/    # CI/CD pipeline
├── backend/
│   ├── app/
│   │   ├── main.py       # FastAPI entry
│   │   ├── models.py     # SQLAlchemy ORM
│   │   ├── config.py     # Pydantic settings
│   │   ├── database.py   # Async engine
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # GeoIP + threat classifier
│   │   ├── parsers/      # Log parsers
│   │   ├── ingestion/    # File watcher
│   │   └── websocket/    # WS manager
│   └── seed_data.py      # Synthetic data generator
├── frontend/
│   └── src/
│       ├── components/   # All UI components
│       ├── charts/       # Recharts visualizations
│       ├── pages/        # Dashboard layout
│       └── services/     # API + hooks
├── honeypot/
│   ├── cowrie/           # SSH/Telnet honeypot
│   └── web-login/        # Flask fake portal
├── monitoring/
│   ├── prometheus/       # Scrape config
│   └── grafana/          # Auto-provisioned dashboard
└── docker/
    └── 01-init.sql       # DB initialization
```

---

## 🔧 Development (without Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
# Set up a local PostgreSQL instance, then:
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/threatshield_db uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev    # Starts on http://localhost:5173
```

---

## 🌍 GeoIP Setup (Real IP Geolocation)

The platform works without GeoIP using an intelligent fallback, but for real geolocation:

1. Create a free account at https://www.maxmind.com/en/geolite2/signup
2. Download **GeoLite2-City.mmdb**
3. Copy to `backend/geoip/GeoLite2-City.mmdb`
4. Mount with: `docker compose up -d --build backend`

Or use the Docker volume:
```bash
docker cp GeoLite2-City.mmdb threatshield-backend:/app/geoip/
docker restart threatshield-backend
```

---

## 🌐 AWS EC2 Migration Guide

### 1. Launch EC2 Instance
- AMI: Ubuntu 22.04 LTS
- Instance: t3.small (2 vCPU, 2GB RAM) minimum
- Storage: 20GB gp3

### 2. Security Group Rules
| Port | Protocol | Source | Purpose |
|---|---|---|---|
| 22  | TCP | Your IP | SSH admin |
| 80  | TCP | 0.0.0.0/0 | Frontend |
| 8000| TCP | 0.0.0.0/0 | Backend API |
| 2222| TCP | 0.0.0.0/0 | SSH Honeypot |
| 2323| TCP | 0.0.0.0/0 | Telnet Honeypot |
| 8080| TCP | 0.0.0.0/0 | Web Login Honeypot |
| 9090| TCP | Your IP | Prometheus |
| 3001| TCP | Your IP | Grafana |
| 3000| TCP | 0.0.0.0/0 | Dashboard |

### 3. Server Setup
```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone project
git clone <your-repo-url> /opt/threatshield
cd /opt/threatshield
```

### 4. Configure for EC2
```bash
cp .env.example .env
# Edit .env:
nano .env
# Change:
# VITE_API_URL=http://<EC2_PUBLIC_IP>:8000
# VITE_WS_URL=ws://<EC2_PUBLIC_IP>:8000
# BACKEND_CORS_ORIGINS=http://<EC2_PUBLIC_IP>:3000
```

### 5. Deploy
```bash
docker compose up -d
docker exec -it threatshield-backend python seed_data.py
```

### 6. Access
- Dashboard:  `http://<EC2_PUBLIC_IP>:3000`
- Backend API: `http://<EC2_PUBLIC_IP>:8000/docs`
- Grafana:    `http://<EC2_PUBLIC_IP>:3001`

---

## 📊 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/stats` | GET | Platform-wide KPI metrics |
| `/api/attacks` | GET | Attack sessions (paginated) |
| `/api/attacks/{id}` | GET | Full session detail |
| `/api/top-ips` | GET | Top 20 attacker IPs |
| `/api/countries` | GET | Attacks by country |
| `/api/timeline` | GET | Hourly attack timeline |
| `/api/categories` | GET | Attack type distribution |
| `/ws/feed` | WS | Real-time event stream |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | Swagger UI |

---

## 🔒 Security Notes

- All honeypot credentials are FAKE — never real credentials
- The web-login portal always rejects logins (honeypot behavior)
- Never expose PostgreSQL port publicly
- Change `GF_SECURITY_ADMIN_PASSWORD` before production
- `SECRET_KEY` must be changed before any real deployment
- This platform is for **educational/defensive research** only

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit (`git commit -m 'feat: add amazing feature'`)
4. Push (`git push origin feat/amazing-feature`)
5. Open a Pull Request

CI/CD will automatically lint, test, scan, and build your changes.
