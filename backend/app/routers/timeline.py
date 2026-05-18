from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime, timedelta

from app.database import get_db
from app.models import AttackSession

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


@router.get("")
async def get_timeline(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """
    Return hourly attack counts for the last N hours.
    Produces data points for the area chart.
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    result = await db.execute(
        select(
            func.date_trunc("hour", AttackSession.started_at).label("hour"),
            func.count(AttackSession.id).label("attacks"),
        )
        .where(AttackSession.started_at >= since)
        .group_by("hour")
        .order_by("hour")
    )
    rows = result.all()

    # Build a full timeline with zero-fill for missing hours
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    all_hours = {
        (now - timedelta(hours=i)).isoformat(): 0
        for i in range(hours - 1, -1, -1)
    }

    for r in rows:
        if r.hour:
            key = r.hour.replace(minute=0, second=0, microsecond=0).isoformat()
            all_hours[key] = r.attacks

    return [{"time": k, "attacks": v} for k, v in all_hours.items()]
