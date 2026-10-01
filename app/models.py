import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class LeadStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    won = "won"
    lost = "lost"


# won and lost are final, a closed lead can't be reopened
ALLOWED_TRANSITIONS = {
    LeadStatus.new: {LeadStatus.in_progress},
    LeadStatus.in_progress: {LeadStatus.won, LeadStatus.lost},
    LeadStatus.won: set(),
    LeadStatus.lost: set(),
}


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_name: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    # varchar instead of native postgres enum: adding a status later won't need ALTER TYPE
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, native_enum=False, length=20), default=LeadStatus.new
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
