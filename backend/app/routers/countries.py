from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models import AttackSession

router = APIRouter(prefix="/api/countries", tags=["countries"])


@router.get("")
async def get_countries(db: AsyncSession = Depends(get_db)):
    """Return attack counts grouped by country."""
    result = await db.execute(
        select(
            AttackSession.country,
            AttackSession.country_code,
            func.count(AttackSession.id).label("attacks"),
            func.avg(AttackSession.threat_score).label("avg_score"),
        )
        .where(AttackSession.country.isnot(None))
        .group_by(AttackSession.country, AttackSession.country_code)
        .order_by(desc("attacks"))
        .limit(50)
    )
    rows = result.all()
    return [
        {
            "country":      r.country,
            "country_code": r.country_code or "XX",
            "attacks":      r.attacks,
            "avg_score":    round(float(r.avg_score or 0), 1),
        }
        for r in rows
    ]
