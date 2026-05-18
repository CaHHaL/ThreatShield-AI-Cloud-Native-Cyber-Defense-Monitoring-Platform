from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import AttackSession, Severity

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Return platform-wide statistics for the KPI cards.
    Optimized with a single query per metric.
    """
    total = (await db.execute(
        select(func.count()).select_from(AttackSession)
    )).scalar() or 0

    critical = (await db.execute(
        select(func.count()).select_from(AttackSession)
        .where(AttackSession.severity == Severity.CRITICAL)
    )).scalar() or 0

    high = (await db.execute(
        select(func.count()).select_from(AttackSession)
        .where(AttackSession.severity == Severity.HIGH)
    )).scalar() or 0

    medium = (await db.execute(
        select(func.count()).select_from(AttackSession)
        .where(AttackSession.severity == Severity.MEDIUM)
    )).scalar() or 0

    country_count = (await db.execute(
        select(func.count(func.distinct(AttackSession.country)))
        .select_from(AttackSession)
    )).scalar() or 0

    avg_score = (await db.execute(
        select(func.avg(AttackSession.threat_score)).select_from(AttackSession)
    )).scalar() or 0

    web_count = (await db.execute(
        select(func.count()).select_from(AttackSession)
        .where(AttackSession.source == "web_login")
    )).scalar() or 0

    ssh_count = total - web_count
    top_port  = "2222/SSH" if ssh_count >= web_count else "8080/HTTP"

    unique_ips = (await db.execute(
        select(func.count(func.distinct(AttackSession.attacker_ip)))
        .select_from(AttackSession)
    )).scalar() or 0

    return {
        "total_attacks":       total,
        "critical_threats":    critical,
        "high_threats":        high,
        "medium_threats":      medium,
        "countries_detected":  country_count,
        "unique_ips":          unique_ips,
        "avg_threat_score":    round(float(avg_score), 1),
        "active_honeypots":    2,
        "top_targeted_port":   top_port,
        "ssh_attacks":         ssh_count,
        "web_attacks":         web_count,
    }
