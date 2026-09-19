import uuid
from decimal import Decimal

from pydantic import BaseModel


class PaymentInitResponse(BaseModel):
    """Everything the Flutter app needs to hand to the PayHere SDK's startPayment()."""
    merchant_id: str
    order_id: str
    amount: Decimal
    currency: str = "LKR"
    items: str
    sandbox: bool
    notify_url: str
    hash: str  


class PayHereWebhookPayload(BaseModel):
    merchant_id: str
    order_id: str
    payment_id: str
    payhere_amount: str
    payhere_currency: str
    status_code: str
    md5sig: str