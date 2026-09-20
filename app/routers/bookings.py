import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas.booking import AvailabilitySlot, BookingCreate, BookingOut
from app.services.booking_service import create_booking_hold, get_bookings_for_day

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/availability", response_model=list[AvailabilitySlot])
def get_availability(
    court_id: uuid.UUID = Query(...),
    booking_date: date = Query(..., description="e.g. 2026-09-24"),
    db: Session = Depends(get_db),
):
    
    bookings = get_bookings_for_day(db, court_id, booking_date)
    return [
        AvailabilitySlot(start_time=b.start_time, end_time=b.end_time, status="booked")
        for b in bookings
    ]


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    booking = create_booking_hold(
        db,
        court_id=payload.court_id,
        user_id=current_user.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    return booking


@router.get("/me", response_model=list[BookingOut])
def my_bookings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.start_time.desc())
        .all()
    )


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = BookingStatus.cancelled
    db.commit()
    db.refresh(booking)
    return booking