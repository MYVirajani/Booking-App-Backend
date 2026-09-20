import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.booking import Booking, BookingStatus
from app.models.court import Court


def get_bookings_for_day(db: Session, court_id: uuid.UUID, day: date) -> list[Booking]:
    day_start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    day_end = datetime.combine(day, time.max, tzinfo=timezone.utc)

    return (
        db.query(Booking)
        .filter(
            Booking.court_id == court_id,
            Booking.status != BookingStatus.cancelled,
            Booking.start_time < day_end,
            Booking.end_time > day_start,
        )
        .order_by(Booking.start_time)
        .all()
    )


def create_booking_hold(
    db: Session, court_id: uuid.UUID, user_id: uuid.UUID, start_time: datetime, end_time: datetime
) -> Booking:
    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    court = db.get(Court, court_id)
    if not court or not court.is_active:
        raise HTTPException(status_code=404, detail="Court not found or inactive")

    hours = Decimal((end_time - start_time).total_seconds()) / Decimal(3600)
    total_amount = (court.rate_per_hour * hours).quantize(Decimal("0.01"))

    booking = Booking(
        court_id=court_id,
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
        total_amount=total_amount,
        status=BookingStatus.pending,
    )
    db.add(booking)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This slot was just booked. Please pick another.")

    db.refresh(booking)
    return booking


def hold_expiry_cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=settings.booking_hold_minutes)