from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Lead, LeadStatus
from app.schemas import FunnelStats

router = APIRouter(prefix="/analytics", tags=["analytics"])


def conversion(won: int, lost: int) -> float | None:
    """Share of won leads among closed ones, in percent.

    Leads that are still open are not counted, otherwise the rate would drop
    every time new leads come in. None means there are no closed leads yet.
    """
    closed = won + lost
    if closed == 0:
        return None
    return round(won / closed * 100, 1)


@router.get("/funnel", response_model=FunnelStats)
def funnel(db: Session = Depends(get_db)):
    rows = db.execute(select(Lead.status, func.count()).group_by(Lead.status)).all()
    by_status = {s: 0 for s in LeadStatus}
    by_status.update({status: count for status, count in rows})
    return FunnelStats(
        total=sum(by_status.values()),
        by_status=by_status,
        conversion_percent=conversion(by_status[LeadStatus.won], by_status[LeadStatus.lost]),
    )
