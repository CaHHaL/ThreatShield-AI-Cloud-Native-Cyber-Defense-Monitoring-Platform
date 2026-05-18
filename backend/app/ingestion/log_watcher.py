"""
Log watcher: background asyncio task that tails Cowrie and web-login log files,
parses new entries, persists them to the database, and broadcasts real-time
events to all connected WebSocket clients.
"""

import asyncio
import os
import uuid
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import AttackSession, CredentialAttempt, CommandLog
from app.parsers.cowrie_parser import parse_cowrie_line, parse_web_login_line
from app.services.geoip_service import lookup_ip
from app.services.threat_classifier import classify_attack, MALWARE_COMMANDS
from app.config import get_settings
from app.websocket.feed import broadcast_event

settings   = get_settings()
logger     = logging.getLogger(__name__)
POLL_SECS  = 2  # poll interval in seconds


# ─── Main watcher loop ────────────────────────────────────────────────────────

async def watch_logs():
    """
    Continuously tail both honeypot log files and process new lines.
    Handles file rotation/truncation gracefully.
    Runs as a background task from FastAPI lifespan.
    """
    cowrie_path    = settings.COWRIE_LOG_PATH
    web_login_path = settings.WEB_LOGIN_LOG_PATH

    cowrie_pos = 0
    web_pos    = 0

    logger.info(f"[Watcher] Starting. Cowrie: {cowrie_path} | Web: {web_login_path}")

    # ── Skip to end of existing files on startup (only process NEW lines) ──
    if os.path.exists(cowrie_path):
        cowrie_pos = os.path.getsize(cowrie_path)
        logger.info(f"[Watcher] Cowrie log found ({cowrie_pos} bytes) — skipping to end")
    else:
        logger.warning(f"[Watcher] Cowrie log NOT found at {cowrie_path} — will watch for creation")

    if os.path.exists(web_login_path):
        web_pos = os.path.getsize(web_login_path)
        logger.info(f"[Watcher] Web-login log found ({web_pos} bytes) — skipping to end")
    else:
        logger.warning(f"[Watcher] Web-login log NOT found at {web_login_path} — will watch for creation")

    # Log what files are actually in the volume for diagnostics
    logs_dir = os.path.dirname(cowrie_path)
    if os.path.isdir(logs_dir):
        contents = os.listdir(logs_dir)
        logger.info(f"[Watcher] Files in {logs_dir}: {contents}")
    else:
        logger.warning(f"[Watcher] Directory {logs_dir} does not exist!")

    while True:
        try:
            await asyncio.sleep(POLL_SECS)

            async with AsyncSessionLocal() as db:
                # ── Cowrie log ──────────────────────────────────────────────
                if os.path.exists(cowrie_path):
                    try:
                        size = os.path.getsize(cowrie_path)
                        if size < cowrie_pos:
                            logger.info("[Watcher] Cowrie log rotated — resetting position")
                            cowrie_pos = 0
                        with open(cowrie_path, "r", encoding="utf-8", errors="ignore") as f:
                            f.seek(cowrie_pos)
                            new_lines = f.readlines()
                            cowrie_pos = f.tell()
                        if new_lines:
                            logger.info(f"[Watcher] {len(new_lines)} new Cowrie lines")
                            for line in new_lines:
                                try:
                                    await _process_cowrie_line(line, db)
                                except Exception as e:
                                    logger.error(f"[Watcher] Cowrie line error: {e}")
                    except Exception as e:
                        logger.error(f"[Watcher] Error reading cowrie log: {e}")

                # ── Web-login log ───────────────────────────────────────────
                if os.path.exists(web_login_path):
                    try:
                        size = os.path.getsize(web_login_path)
                        if size < web_pos:
                            logger.info("[Watcher] Web-login log rotated — resetting position")
                            web_pos = 0
                        with open(web_login_path, "r", encoding="utf-8", errors="ignore") as f:
                            f.seek(web_pos)
                            new_lines = f.readlines()
                            web_pos = f.tell()
                        if new_lines:
                            logger.info(f"[Watcher] {len(new_lines)} new web-login lines")
                            for line in new_lines:
                                try:
                                    await _process_web_login_line(line, db)
                                except Exception as e:
                                    logger.error(f"[Watcher] Web-login line error: {e}")
                    except Exception as e:
                        logger.error(f"[Watcher] Error reading web-login log: {e}")

        except asyncio.CancelledError:
            logger.info("[Watcher] Stopped (cancelled)")
            raise
        except Exception as e:
            logger.error(f"[Watcher] Unexpected error: {e}", exc_info=True)
            await asyncio.sleep(5)  # Back off on major errors


# ─── Cowrie event handlers ─────────────────────────────────────────────────────

async def _process_cowrie_line(line: str, db: AsyncSession):
    """Dispatch a single Cowrie JSON log line to the correct handler."""
    evt = parse_cowrie_line(line)
    if not evt:
        return

    eid = evt.get("eventid", "")
    if eid == "cowrie.session.connect":
        await _handle_connect(evt, db)
    elif eid in ("cowrie.login.failed", "cowrie.login.success"):
        await _handle_credential(evt, db)
    elif eid == "cowrie.command.input":
        await _handle_command(evt, db)
    elif eid == "cowrie.session.file_download":
        await _handle_malware(evt, db)
    elif eid == "cowrie.session.closed":
        await _handle_close(evt, db)


async def _handle_connect(evt: dict, db: AsyncSession):
    """Create a new AttackSession when a connection is established."""
    sid = evt.get("session", str(uuid.uuid4()))

    # Deduplicate — skip if session already exists
    existing = await db.execute(
        select(AttackSession).where(AttackSession.session_id == sid)
    )
    if existing.scalar_one_or_none():
        return

    ip  = evt.get("src_ip", "0.0.0.0")
    geo = lookup_ip(ip)

    session = AttackSession(
        session_id   = sid,
        source       = "cowrie",
        attacker_ip  = ip,
        country      = geo["country"],
        country_code = geo["country_code"],
        city         = geo["city"],
        latitude     = geo["latitude"],
        longitude    = geo["longitude"],
        started_at   = datetime.utcnow(),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    await broadcast_event({
        "type":      "new_session",
        "severity":  "LOW",
        "message":   f"New SSH connection from {ip} ({geo['country']})",
        "ip":        ip,
        "country":   geo["country"],
        "timestamp": datetime.utcnow().isoformat(),
    })


async def _handle_credential(evt: dict, db: AsyncSession):
    """Record a login attempt and update threat classification."""
    sid = evt.get("session")
    result = await db.execute(
        select(AttackSession).where(AttackSession.session_id == sid)
    )
    session = result.scalar_one_or_none()
    if not session:
        return

    username = evt.get("username", "")
    password = evt.get("password", "")
    success  = evt.get("eventid") == "cowrie.login.success"

    cred = CredentialAttempt(
        session_id=session.id,
        username=username,
        password=password,
        success=success,
    )
    db.add(cred)
    session.login_attempts = (session.login_attempts or 0) + 1

    # Re-classify with updated credential list
    all_creds = await db.execute(
        select(CredentialAttempt).where(CredentialAttempt.session_id == session.id)
    )
    usernames = [c.username for c in all_creds.scalars().all()] + [username]
    attack_type, severity, score = classify_attack(usernames, [], source="cowrie")
    session.attack_type  = attack_type
    session.severity     = severity
    session.threat_score = score

    await db.commit()
    await broadcast_event({
        "type":      "credential_attempt",
        "severity":  severity.value,
        "message":   f"{'✅ Login SUCCESS' if success else '❌ Login failed'}: {username}/{password} from {session.attacker_ip}",
        "ip":        session.attacker_ip,
        "country":   session.country,
        "timestamp": datetime.utcnow().isoformat(),
    })


async def _handle_command(evt: dict, db: AsyncSession):
    """Record a shell command and escalate threat if suspicious."""
    sid = evt.get("session")
    result = await db.execute(
        select(AttackSession).where(AttackSession.session_id == sid)
    )
    session = result.scalar_one_or_none()
    if not session:
        return

    cmd          = evt.get("input", "")
    is_suspicious = any(kw in cmd.lower() for kw in MALWARE_COMMANDS)

    log = CommandLog(
        session_id=session.id,
        command=cmd,
        is_suspicious=is_suspicious,
    )
    db.add(log)
    session.commands_run = (session.commands_run or 0) + 1

    # Re-classify with updated command list
    all_creds = await db.execute(
        select(CredentialAttempt).where(CredentialAttempt.session_id == session.id)
    )
    all_cmds = await db.execute(
        select(CommandLog).where(CommandLog.session_id == session.id)
    )
    usernames = [c.username for c in all_creds.scalars().all()]
    commands  = [c.command  for c in all_cmds.scalars().all()] + [cmd]
    attack_type, severity, score = classify_attack(usernames, commands, source="cowrie")
    session.attack_type  = attack_type
    session.severity     = severity
    session.threat_score = score

    await db.commit()

    if is_suspicious:
        await broadcast_event({
            "type":      "suspicious_command",
            "severity":  severity.value,
            "message":   f"⚠️ Suspicious cmd: `{cmd[:80]}` from {session.attacker_ip}",
            "ip":        session.attacker_ip,
            "country":   session.country,
            "timestamp": datetime.utcnow().isoformat(),
        })


async def _handle_malware(evt: dict, db: AsyncSession):
    """Record a malware download attempt and escalate to CRITICAL."""
    sid = evt.get("session")
    result = await db.execute(
        select(AttackSession).where(AttackSession.session_id == sid)
    )
    session = result.scalar_one_or_none()
    if not session:
        return

    session.malware_downloads = (session.malware_downloads or 0) + 1
    url = evt.get("url", "unknown")

    all_creds = await db.execute(
        select(CredentialAttempt).where(CredentialAttempt.session_id == session.id)
    )
    usernames = [c.username for c in all_creds.scalars().all()]
    attack_type, severity, score = classify_attack(
        usernames, [], source="cowrie",
        malware_downloads=session.malware_downloads
    )
    session.attack_type  = attack_type
    session.severity     = severity
    session.threat_score = score
    await db.commit()

    await broadcast_event({
        "type":      "malware_download",
        "severity":  "CRITICAL",
        "message":   f"💀 MALWARE download: {url} from {session.attacker_ip}",
        "ip":        session.attacker_ip,
        "country":   session.country,
        "timestamp": datetime.utcnow().isoformat(),
    })


async def _handle_close(evt: dict, db: AsyncSession):
    """Mark a session as ended."""
    sid = evt.get("session")
    result = await db.execute(
        select(AttackSession).where(AttackSession.session_id == sid)
    )
    session = result.scalar_one_or_none()
    if session:
        session.ended_at = datetime.utcnow()
        await db.commit()


# ─── Web-login event handler ──────────────────────────────────────────────────

async def _process_web_login_line(line: str, db: AsyncSession):
    """Parse and store a web-login honeypot event."""
    summary = parse_web_login_line(line)
    if not summary or not summary.get("attacker_ip"):
        return

    sid = summary["session_id"] or str(uuid.uuid4())

    # Deduplicate
    existing = await db.execute(
        select(AttackSession).where(AttackSession.session_id == sid)
    )
    if existing.scalar_one_or_none():
        return

    ip  = summary["attacker_ip"]
    geo = lookup_ip(ip)
    attack_type, severity, score = classify_attack(
        summary["usernames"], [], source="web_login"
    )

    session = AttackSession(
        session_id   = sid,
        source       = "web_login",
        attacker_ip  = ip,
        attack_type  = attack_type,
        severity     = severity,
        threat_score = score,
        country      = geo["country"],
        country_code = geo["country_code"],
        city         = geo["city"],
        latitude     = geo["latitude"],
        longitude    = geo["longitude"],
        started_at   = summary["started_at"],
        login_attempts = 1,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Store credentials
    for u, p in zip(summary["usernames"], summary["passwords"]):
        db.add(CredentialAttempt(
            session_id=session.id,
            username=u,
            password=p,
        ))
    await db.commit()

    first_user = summary["usernames"][0] if summary["usernames"] else "?"
    await broadcast_event({
        "type":      "web_login_attempt",
        "severity":  severity.value,
        "message":   f"🔑 Web login attempt: {first_user} from {ip} ({geo['country']})",
        "ip":        ip,
        "country":   geo["country"],
        "timestamp": datetime.utcnow().isoformat(),
    })
