import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import PaymentInitResponse
from app.services.payhere_service import generate_payment_hash, verify_webhook_signature

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/init/{booking_id}", response_model=PaymentInitResponse)
def init_payment(
    booking_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    booking = db.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Booking is not awaiting payment")

    order_id = f"BOOK-{booking.id}"
    amount = f"{booking.total_amount:.2f}"
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if not payment:
        payment = Payment(
            booking_id=booking.id,
            amount=booking.total_amount,
            payhere_order_id=order_id,
            status=PaymentStatus.pending,
        )
        db.add(payment)
        db.commit()

    return PaymentInitResponse(
        merchant_id=settings.payhere_merchant_id,
        order_id=order_id,
        amount=booking.total_amount,
        items=f"Court booking {booking.id}",
        sandbox=settings.payhere_sandbox,
        notify_url="",
        hash=generate_payment_hash(order_id, amount),
    )


@router.post("/webhook")
async def payhere_webhook(
    request: Request,
    merchant_id: str = Form(...),
    order_id: str = Form(...),
    payment_id: str = Form(...),
    payhere_amount: str = Form(...),
    payhere_currency: str = Form(...),
    status_code: str = Form(...),
    md5sig: str = Form(...),
    db: Session = Depends(get_db),
):
    
    if not verify_webhook_signature(
        merchant_id, order_id, payhere_amount, payhere_currency, status_code, md5sig
    ):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payment = db.query(Payment).filter(Payment.payhere_order_id == order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")

    if status_code == "2":
        payment.status = PaymentStatus.success
        payment.payhere_payment_id = payment_id
        payment.paid_at = datetime.now(timezone.utc)

        booking = db.get(Booking, payment.booking_id)
        booking.status = BookingStatus.confirmed
    else:
        payment.status = PaymentStatus.failed

    db.commit()
    return {"received": True}