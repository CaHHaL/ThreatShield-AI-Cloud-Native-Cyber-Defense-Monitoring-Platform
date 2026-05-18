from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models import AttackSession

router = APIRouter(prefix="/api/top-ips", tags=["top-ips"])


@router.get("")
async def get_top_ips(db: AsyncSession = Depends(get_db)):
    """Return the top 20 most active attacker IPs."""
    result = await db.execute(
        select(
            AttackSession.attacker_ip,
            AttackSession.country,
            AttackSession.country_code,
            func.count(AttackSession.id).label("attack_count"),
            func.max(AttackSession.threat_score).label("max_score"),
            func.sum(AttackSession.login_attempts).label("total_logins"),
            func.sum(AttackSession.commands_run).label("total_commands"),
        )
        .group_by(
            AttackSession.attacker_ip,
            AttackSession.country,
            AttackSession.country_code,
        )
        .order_by(desc("attack_count"))
        .limit(20)
    )
    rows = result.all()
    return [
        {
            "ip":                   r.attacker_ip,
            "country":              r.country or "Unknown",
            "country_code":         r.country_code or "XX",
            "attack_count":         r.attack_count,
            "max_threat_score":     r.max_score or 0,
            "total_login_attempts": int(r.total_logins or 0),
            "total_commands":       int(r.total_commands or 0),
        }
        for r in rows
    ]
