from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class PaymentResponse:
    """
    Ответ с информацией о платеже.
    """
    payment_id: str
    amount: Decimal
    currency: str
    status: str
    description: Optional[str] = None
    customer_email: Optional[str] = None
    created_at: str = ""  # ISO 8601 строка