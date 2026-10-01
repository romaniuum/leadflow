from fastapi import APIRouter, Depends
from sqlalchemy import Numeric, cast, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Lead, LeadStatus
from app.schemas import FunnelStats, SourceStats

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


@router.get("/sources", response_model=list[SourceStats])
def sources(db: Session = Depends(get_db)):
    is_won = Lead.status == LeadStatus.won
    total = func.count().label("total")
    # same type as the column, so an empty sum comes back as 0.00, not 0
    zero = cast(0, Numeric(12, 2))
    query = (
        select(
            Lead.source,
            total,
            func.count().filter(is_won).label("won"),
            func.count().filter(Lead.status == LeadStatus.lost).label("lost"),
            func.coalesce(func.sum(Lead.amount).filter(is_won), zero).label("won_amount"),
        )
        .group_by(Lead.source)
        .order_by(total.desc(), Lead.source)
    )
    return [
        SourceStats(
            source=row.source,
            total=row.total,
            won=row.won,
            won_amount=row.won_amount,
            conversion_percent=conversion(row.won, row.lost),
        )
        for row in db.execute(query)
    ]
