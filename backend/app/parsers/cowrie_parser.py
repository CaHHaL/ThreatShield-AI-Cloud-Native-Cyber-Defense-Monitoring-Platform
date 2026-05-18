"""
Log parsers for Cowrie SSH honeypot and web-login honeypot JSON formats.
"""

import json
from datetime import datetime
from typing import Optional


# ─── Cowrie JSON log parser ───────────────────────────────────────────────────

def parse_cowrie_line(line: str) -> Optional[dict]:
    """
    Parse a single Cowrie JSON log line.
    Returns the parsed dict or None on malformed input.

    Cowrie writes one JSON object per line in cowrie.json, e.g.:
      {"eventid":"cowrie.session.connect","src_ip":"1.2.3.4","session":"abc123",...}
    """
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def extract_session_events(lines: list[str]) -> dict:
    """
    Group Cowrie log lines by session ID.
    Returns: dict[session_id] -> list[event_dict]
    """
    sessions: dict[str, list] = {}
    for line in lines:
        evt = parse_cowrie_line(line)
        if not evt:
            continue
        sid = evt.get("session")
        if not sid:
            continue
        sessions.setdefault(sid, []).append(evt)
    return sessions


def build_session_summary(events: list[dict]) -> dict:
    """
    Collapse a list of Cowrie events for one session into a summary dict.
    Used for batch processing (not used in real-time streaming path).
    """
    summary = {
        "session_id":       None,
        "attacker_ip":      None,
        "source":           "cowrie",
        "started_at":       None,
        "ended_at":         None,
        "login_attempts":   0,
        "commands_run":     0,
        "malware_downloads": 0,
        "usernames":        [],
        "passwords":        [],
        "commands":         [],
        "raw_events":       events,
    }

    for evt in events:
        eid    = evt.get("eventid", "")
        ts_str = evt.get("timestamp", "")

        ts = None
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                # Strip timezone to keep all datetimes naive (UTC assumed)
                if ts.tzinfo is not None:
                    ts = ts.replace(tzinfo=None)
            except Exception:
                pass

        if summary["session_id"] is None:
            summary["session_id"] = evt.get("session")
        if summary["attacker_ip"] is None:
            summary["attacker_ip"] = evt.get("src_ip")

        if eid == "cowrie.session.connect":
            if ts and summary["started_at"] is None:
                summary["started_at"] = ts

        elif eid == "cowrie.session.closed":
            if ts:
                summary["ended_at"] = ts

        elif eid in ("cowrie.login.failed", "cowrie.login.success"):
            summary["login_attempts"] += 1
            username = evt.get("username", "")
            password = evt.get("password", "")
            if username and username not in summary["usernames"]:
                summary["usernames"].append(username)
            if password and password not in summary["passwords"]:
                summary["passwords"].append(password)

        elif eid == "cowrie.command.input":
            summary["commands_run"] += 1
            cmd = evt.get("input", "")
            if cmd:
                summary["commands"].append(cmd)

        elif eid == "cowrie.session.file_download":
            summary["malware_downloads"] += 1

    if summary["started_at"] is None:
        summary["started_at"] = datetime.utcnow()

    return summary


# ─── Web-login honeypot JSON parser ──────────────────────────────────────────

def parse_web_login_line(line: str) -> Optional[dict]:
    """
    Parse a single web-login-honeypot JSON log line.

    The Flask honeypot writes entries like:
    {"request_id":"uuid","timestamp":"ISO","ip":"x.x.x.x","username":"...","password":"...","user_agent":"..."}

    Returns a normalized summary dict compatible with log_watcher expectations,
    or None on error.
    """
    line = line.strip()
    if not line:
        return None
    try:
        data = json.loads(line)
        ts_str = data.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            # Strip timezone to keep all datetimes naive (UTC assumed)
            if ts.tzinfo is not None:
                ts = ts.replace(tzinfo=None)
        except Exception:
            ts = datetime.utcnow()

        return {
            "session_id":       data.get("request_id"),
            "attacker_ip":      data.get("ip"),
            "source":           "web_login",
            "started_at":       ts,
            "ended_at":         None,
            "login_attempts":   1,
            "commands_run":     0,
            "malware_downloads": 0,
            "usernames":        [data.get("username", "")],
            "passwords":        [data.get("password", "")],
            "commands":         [],
            "raw_events":       [data],
        }
    except Exception:
        return None
