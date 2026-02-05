from typing import Optional, Dict
from datetime import datetime

from ...domain.payment import Payment
from ...domain.payment_id import PaymentId
from ...domain.amount import Amount
from ...domain.payment_status import PaymentStatus
from ...domain.ports.payment_processor import PaymentProcessorPort
from ...domain.exceptions import PaymentProcessingError


class InMemoryPaymentAdapter(PaymentProcessorPort):
    """
    Простой адаптер для обработки платежей в памяти.

    Хранит все платежи в словаре Python.
    Не сохраняет данные между перезапусками.
    """

    def __init__(self):
        # Внутреннее хранилище платежей: {payment_id.value: Payment}
        self._payments: Dict[str, Payment] = {}

    def process_payment(
            self,
            payment_id: PaymentId,
            amount: Amount,
            description: Optional[str] = None,
            customer_email: Optional[str] = None,
            meta: Optional[dict] = None
    ) -> Payment:
        """
        Обработать платёж в памяти.

        Всегда успешен (для демо). В реальных адаптерах здесь будет:
        - Вызов внешнего API (Stripe, PayPal)
        - Обработка ошибок сети
        - Симуляция отказов (через параметр fail_rate)
        """
        # Проверка: платёж с таким ID уже существует?
        if payment_id.value in self._payments:
            raise PaymentProcessingError(
                f"Payment with id={payment_id.value} already exists",
                payment_id=payment_id.value
            )

        # Создаём успешный платёж
        payment = Payment(
            id=payment_id,
            amount=amount,
            status=PaymentStatus.SUCCEEDED,
            created_at=datetime.now(),
            description=description,
            customer_email=customer_email
        )

        # Сохраняем в "хранилище"
        self._payments[payment_id.value] = payment

        return payment

    def refund_payment(
            self,
            payment_id: PaymentId,
            amount: Optional[Amount] = None,
            reason: Optional[str] = None
    ) -> Payment:
        """
        Вернуть платёж в памяти.

        Для демо: всегда успешен, если платёж существует.
        """
        # Проверка: платёж существует?
        if payment_id.value not in self._payments:
            raise PaymentProcessingError(
                f"Payment with id={payment_id.value} not found for refund",
                payment_id=payment_id.value
            )

        original_payment = self._payments[payment_id.value]

        # Создаём платёж со статусом возврата
        refunded_payment = Payment(
            id=original_payment.id,
            amount=amount or original_payment.amount,  # Полный или частичный возврат
            status=PaymentStatus.REFUNDED,
            created_at=datetime.now(),
            description=f"Refund: {reason or 'No reason provided'}",
            customer_email=original_payment.customer_email,
            error_message=None
        )

        # Обновляем хранилище
        self._payments[payment_id.value] = refunded_payment

        return refunded_payment