from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Относительные импорты из того же пакета `domain`
from .payment_id import PaymentId
from .amount import Amount
from .payment_status import PaymentStatus


@dataclass(frozen=True)
class Payment:
    id: PaymentId  # Уникальный идентификатор платежа
    amount: Amount  # Сумма платежа
    status: PaymentStatus  # Статус платежа
    created_at: datetime  # Дата создания (аналог LocalDateTime в Java)
    description: Optional[str] = None  # Описание платежа
    customer_email: Optional[str] = None  # Email клиента
    error_message: Optional[str] = None  # Сообщение об ошибке (если статус FAILED)

    """
    Проверка, успешен ли платёж.
    """
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.SUCCEEDED

    """
    Проверка, провален ли платёж.
    """
    def is_failed(self) -> bool:
        return self.status == PaymentStatus.FAILED

    """
    Строковое представление объекта (аналог toString() в Java).
    """
    def __str__(self) -> str:

        return (
            f"Payment(id={self.id.value}, "
            f"amount={self.amount.value} {self.amount.currency}, "
            f"status={self.status.value})"
        )