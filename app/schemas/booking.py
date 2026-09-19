import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    court_id: uuid.UUID
    start_time: datetime
    end_time: datetime


class BookingOut(BaseModel):
    id: uuid.UUID
    court_id: uuid.UUID
    user_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    total_amount: Decimal
    status: BookingStatus

    class Config:
        from_attributes = True


class AvailabilitySlot(BaseModel):
    start_time: datetime
    end_time: datetime
    status: str  