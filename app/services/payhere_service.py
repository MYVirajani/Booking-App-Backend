import hashlib

from app.core.config import settings


def _md5_upper(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest().upper()


def generate_payment_hash(order_id: str, amount: str, currency: str = "LKR") -> str:
    secret_hash = _md5_upper(settings.payhere_merchant_secret)
    raw = f"{settings.payhere_merchant_id}{order_id}{amount}{currency}{secret_hash}"
    return _md5_upper(raw)


def verify_webhook_signature(
    merchant_id: str,
    order_id: str,
    payhere_amount: str,
    payhere_currency: str,
    status_code: str,
    md5sig: str,
) -> bool:
    
    secret_hash = _md5_upper(settings.payhere_merchant_secret)
    raw = f"{merchant_id}{order_id}{payhere_amount}{payhere_currency}{status_code}{secret_hash}"
    expected = _md5_upper(raw)
    return expected == md5sig.upper()