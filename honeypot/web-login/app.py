"""
ThreatShield AI — Fake Corporate Web Login Honeypot

Mimics a corporate employee portal to attract and capture
credential stuffing attacks. All login attempts are logged
to a JSON file watched by the backend.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Log file path — shared with backend via Docker volume
LOG_PATH = os.environ.get("WEB_LOGIN_LOG_PATH", "/app/logs/web-login.json")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def _log_attempt(ip: str, username: str, password: str, user_agent: str, path: str = "/login"):
    """Write a login attempt to the JSON log file."""
    entry = {
        "request_id": str(uuid.uuid4()),
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "ip":         ip,
        "username":   username,
        "password":   password,
        "user_agent": user_agent,
        "path":       path,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _get_ip():
    """Get the real client IP, respecting reverse proxy headers."""
    return (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.remote_addr
        or "0.0.0.0"
    )


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username   = request.form.get("username", "").strip()
        password   = request.form.get("password", "").strip()
        ip         = _get_ip()
        user_agent = request.headers.get("User-Agent", "unknown")
        _log_attempt(ip, username, password, user_agent)
        # Always deny — honeypot never grants access
        error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)


@app.route("/dashboard")
@app.route("/portal")
@app.route("/admin")
def fake_portal():
    """Redirect crawlers back to login."""
    return redirect(url_for("login"))


@app.route("/api/auth", methods=["POST"])
def api_auth():
    """Fake API endpoint for automated scanners."""
    data       = request.get_json(silent=True) or {}
    username   = data.get("username", "")
    password   = data.get("password", "")
    ip         = _get_ip()
    user_agent = request.headers.get("User-Agent", "unknown")
    _log_attempt(ip, username, password, user_agent, path="/api/auth")
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
