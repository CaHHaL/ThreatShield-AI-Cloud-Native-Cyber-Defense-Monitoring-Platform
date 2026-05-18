from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models import AttackSession

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Return attack count grouped by attack type (for pie/donut chart)."""
    result = await db.execute(
        select(
            AttackSession.attack_type,
            func.count(AttackSession.id).label("count"),
        )
        .group_by(AttackSession.attack_type)
        .order_by(desc("count"))
    )
    rows = result.all()

    # Color map for each attack type
    color_map = {
        "brute_force":         "#ff3d71",
        "credential_stuffing": "#ffaa00",
        "reconnaissance":      "#00d4ff",
        "malware_delivery":    "#a855f7",
        "automation":          "#00e096",
        "web_recon":           "#0066ff",
        "unknown":             "#475569",
    }

    return [
        {
            "name":  r.attack_type or "unknown",
            "value": r.count,
            "color": color_map.get(r.attack_type, "#475569"),
        }
        for r in rows
        if r.attack_type
    ]
