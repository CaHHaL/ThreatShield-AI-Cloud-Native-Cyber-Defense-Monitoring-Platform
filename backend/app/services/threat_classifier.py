"""
Threat classification engine.

Analyzes attacker behavior (credentials tried, commands run, malware activity)
and assigns an AttackType and Severity score from 0–100.
"""

from app.models import AttackType, Severity


# ─── Detection rules ──────────────────────────────────────────────────────────

# Commands that indicate post-compromise/malware activity
MALWARE_COMMANDS = [
    "wget", "curl", "chmod +x", "python", "perl", "ruby", "bash -i",
    "nc ", "netcat", "nmap", "/tmp/", "base64 -d", "eval", "exec",
    "rm -rf", "dd if=", "> /dev/null", "xmrig", "miner", "cryptonight",
    "|bash", "| bash", "|sh", "| sh", ">/dev/tcp/", "mkfifo",
    "iptables -F", "/bin/sh", "uname -a", "cat /etc/shadow",
]

# Usernames commonly tried by automated scanners
AUTOMATION_USERNAMES = [
    "root", "admin", "guest", "test", "ubuntu", "pi", "oracle",
    "postgres", "user", "support", "ftp", "www", "mail", "operator",
    "administrator", "vagrant", "ansible", "deploy", "jenkins",
]

BRUTE_FORCE_THRESHOLD = 5    # login attempts to classify as brute_force
AUTOMATION_THRESHOLD  = 3    # auto-usernames to classify as automation


def classify_attack(
    username_attempts: list[str],
    commands: list[str],
    source: str = "cowrie",
    malware_downloads: int = 0,
) -> tuple[AttackType, Severity, int]:
    """
    Classify an attack and return (AttackType, Severity, threat_score 0–100).

    Args:
        username_attempts: All usernames tried in the session
        commands:          All shell commands executed
        source:            "cowrie" or "web_login"
        malware_downloads: Count of malware download events
    """
    score = 0
    attack_type = AttackType.unknown

    # ── Web login path ──────────────────────────────────────────────────────
    if source == "web_login":
        attempts = len(username_attempts)
        score += attempts * 5
        if attempts >= BRUTE_FORCE_THRESHOLD:
            attack_type = AttackType.credential_stuffing
            score += 25
        else:
            attack_type = AttackType.web_recon
            score += 10
        score = min(score, 100)
        return attack_type, _score_to_severity(score), score

    # ── Cowrie SSH/Telnet path ───────────────────────────────────────────────

    # Malware delivery is the most severe — check first
    if malware_downloads > 0:
        attack_type = AttackType.malware_delivery
        score += 40 + min(malware_downloads * 10, 40)

    # Suspicious command execution
    if commands:
        suspicious_cmds = [
            c for c in commands
            if any(kw in c.lower() for kw in MALWARE_COMMANDS)
        ]
        score += len(suspicious_cmds) * 8
        if suspicious_cmds and attack_type == AttackType.unknown:
            attack_type = (
                AttackType.malware_delivery
                if malware_downloads > 0
                else AttackType.reconnaissance
            )

    # Brute force detection
    if len(username_attempts) >= BRUTE_FORCE_THRESHOLD:
        score += min(len(username_attempts) * 3, 45)
        if attack_type == AttackType.unknown:
            attack_type = AttackType.brute_force

    # Automation detection (generic usernames)
    auto_count = sum(
        1 for u in username_attempts
        if u.lower() in AUTOMATION_USERNAMES
    )
    if auto_count >= AUTOMATION_THRESHOLD and attack_type == AttackType.unknown:
        attack_type = AttackType.automation
        score += 20

    # Baseline — any connection is at least reconnaissance
    if attack_type == AttackType.unknown:
        attack_type = AttackType.reconnaissance
        score += 10

    score = min(score, 100)
    return attack_type, _score_to_severity(score), score


def _score_to_severity(score: int) -> Severity:
    """Map numeric threat score to a Severity enum."""
    if score >= 70:
        return Severity.CRITICAL
    elif score >= 45:
        return Severity.HIGH
    elif score >= 20:
        return Severity.MEDIUM
    return Severity.LOW
