from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import AttackSession, CredentialAttempt, CommandLog

router = APIRouter(prefix="/api/attacks", tags=["attacks"])


@router.get("")
async def list_attacks(
    limit:    int  = Query(50, le=500),
    offset:   int  = Query(0, ge=0),
    severity: str  = Query(None),
    source:   str  = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated list of attack sessions, newest first."""
    q = select(AttackSession).order_by(desc(AttackSession.started_at))
    if severity:
        q = q.where(AttackSession.severity == severity)
    if source:
        q = q.where(AttackSession.source == source)
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    sessions = result.scalars().all()
    return [_to_dict(s) for s in sessions]


@router.get("/{session_id}")
async def get_attack(session_id: str, db: AsyncSession = Depends(get_db)):
    """Return full detail for a single session including credentials and commands."""
    result = await db.execute(
        select(AttackSession).where(AttackSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    creds_r = await db.execute(
        select(CredentialAttempt).where(CredentialAttempt.session_id == session.id)
        .order_by(CredentialAttempt.timestamp)
    )
    cmds_r = await db.execute(
        select(CommandLog).where(CommandLog.session_id == session.id)
        .order_by(CommandLog.timestamp)
    )

    d = _to_dict(session)
    d["credentials"] = [
        {
            "username":  c.username,
            "password":  c.password,
            "success":   c.success,
            "timestamp": c.timestamp.isoformat() if c.timestamp else None,
        }
        for c in creds_r.scalars().all()
    ]
    d["commands"] = [
        {
            "command":       c.command,
            "is_suspicious": c.is_suspicious,
            "timestamp":     c.timestamp.isoformat() if c.timestamp else None,
        }
        for c in cmds_r.scalars().all()
    ]
    return d


def _to_dict(s: AttackSession) -> dict:
    return {
        "id":               s.id,
        "session_id":       s.session_id,
        "source":           s.source,
        "attacker_ip":      s.attacker_ip,
        "attack_type":      s.attack_type,
        "severity":         s.severity,
        "threat_score":     s.threat_score,
        "country":          s.country,
        "country_code":     s.country_code,
        "city":             s.city,
        "latitude":         s.latitude,
        "longitude":        s.longitude,
        "started_at":       s.started_at.isoformat() if s.started_at else None,
        "ended_at":         s.ended_at.isoformat()   if s.ended_at   else None,
        "login_attempts":   s.login_attempts or 0,
        "commands_run":     s.commands_run or 0,
        "malware_downloads": s.malware_downloads or 0,
    }
