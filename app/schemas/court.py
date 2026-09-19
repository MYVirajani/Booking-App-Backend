import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.models.court import SportType


class CourtCreate(BaseModel):
    name: str
    sport_type: SportType
    rate_per_hour: Decimal


class CourtOut(BaseModel):
    id: uuid.UUID
    name: str
    sport_type: SportType
    rate_per_hour: Decimal
    is_active: bool

    class Config:
        from_attributes = True