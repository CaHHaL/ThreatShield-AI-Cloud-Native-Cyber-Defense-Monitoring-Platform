"""
ThreatShield AI — SQLAlchemy ORM Models

Tables:
  attack_sessions     — One row per honeypot interaction session
  credential_attempts — Login attempts within a session
  command_logs        — Shell commands run within a cowrie session
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum,
    Boolean, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class AttackType(str, enum.Enum):
    brute_force         = "brute_force"
    reconnaissance      = "reconnaissance"
    malware_delivery    = "malware_delivery"
    automation          = "automation"
    credential_stuffing = "credential_stuffing"
    web_recon           = "web_recon"
    unknown             = "unknown"


class Severity(str, enum.Enum):
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


# ─── Models ───────────────────────────────────────────────────────────────────

class AttackSession(Base):
    """
    Represents one attacker interaction session.
    One Cowrie SSH session = one row.
    One web-login attempt = one row.
    """
    __tablename__ = "attack_sessions"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    source     = Column(String(32), default="cowrie", nullable=False)  # cowrie | web_login

    # Attacker info
    attacker_ip = Column(String(45), index=True, nullable=False)

    # Threat classification
    attack_type  = Column(Enum(AttackType), default=AttackType.unknown)
    severity     = Column(Enum(Severity), default=Severity.LOW, index=True)
    threat_score = Column(Integer, default=0)  # 0–100

    # GeoIP data (from MaxMind — may be null if DB not available)
    country      = Column(String(64),  nullable=True, index=True)
    country_code = Column(String(4),   nullable=True)
    city         = Column(String(64),  nullable=True)
    latitude     = Column(Float,       nullable=True)
    longitude    = Column(Float,       nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at   = Column(DateTime, nullable=True)

    # Activity counts (denormalized for fast stats queries)
    login_attempts   = Column(Integer, default=0)
    commands_run     = Column(Integer, default=0)
    malware_downloads = Column(Integer, default=0)

    # Relationships
    credentials = relationship(
        "CredentialAttempt", back_populates="session", cascade="all, delete-orphan"
    )
    commands = relationship(
        "CommandLog", back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_sessions_started_at", "started_at"),
        Index("ix_sessions_country",    "country"),
        Index("ix_sessions_severity",   "severity"),
    )


class CredentialAttempt(Base):
    """Login credential captured by a honeypot."""
    __tablename__ = "credential_attempts"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attack_sessions.id", ondelete="CASCADE"), index=True)
    username   = Column(String(128), nullable=False, default="")
    password   = Column(String(256), nullable=False, default="")
    success    = Column(Boolean, default=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)

    session = relationship("AttackSession", back_populates="credentials")


class CommandLog(Base):
    """Shell command executed during a Cowrie SSH session."""
    __tablename__ = "command_logs"

    id           = Column(Integer, primary_key=True, index=True)
    session_id   = Column(Integer, ForeignKey("attack_sessions.id", ondelete="CASCADE"), index=True)
    command      = Column(Text, nullable=False)
    timestamp    = Column(DateTime, default=datetime.utcnow)
    is_suspicious = Column(Boolean, default=False)

    session = relationship("AttackSession", back_populates="commands")
