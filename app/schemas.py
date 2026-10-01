from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import LeadStatus


class LeadCreate(BaseModel):
    client_name: str = Field(min_length=1, max_length=200)
    source: str = Field(min_length=1, max_length=50)
    amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class LeadUpdate(BaseModel):
    # status is changed only via /status, so reject it here instead of ignoring
    model_config = ConfigDict(extra="forbid")

    client_name: str | None = Field(default=None, min_length=1, max_length=200)
    source: str | None = Field(default=None, min_length=1, max_length=50)
    amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)


class StatusUpdate(BaseModel):
    status: LeadStatus


class FunnelStats(BaseModel):
    total: int
    by_status: dict[LeadStatus, int]
    conversion_percent: float | None


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_name: str
    source: str
    amount: Decimal
    status: LeadStatus
    created_at: datetime
