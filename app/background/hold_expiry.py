import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.services.booking_service import hold_expiry_cutoff

logger = logging.getLogger(__name__)


def expire_stale_holds() -> None:
    
    db = SessionLocal()
    try:
        cutoff = hold_expiry_cutoff()
        stale = (
            db.query(Booking)
            .filter(Booking.status == BookingStatus.pending, Booking.created_at < cutoff)
            .all()
        )
        for booking in stale:
            booking.status = BookingStatus.cancelled
        if stale:
            db.commit()
            logger.info("Expired %d stale booking hold(s)", len(stale))
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(expire_stale_holds, "interval", minutes=1, id="expire_stale_holds")
    scheduler.start()
    return scheduler