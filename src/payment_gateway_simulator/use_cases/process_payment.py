from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from .core.base_use_case import BaseUseCase
from ..domain.payment import Payment
from ..domain.payment_id import PaymentId
from ..domain.amount import Amount
from ..domain.ports.payment_processor import PaymentProcessorPort
from ..domain.ports.transaction_logger import TransactionLoggerPort


@dataclass(frozen=True)
class ProcessPaymentInput:
    """
    Входные данные для сценария обработки платежа.
    """
    payment_id: str
    amount: Decimal
    currency: str
    description: Optional[str] = None
    customer_email: Optional[str] = None
    meta: Optional[dict] = None


class ProcessPaymentUseCase(BaseUseCase[ProcessPaymentInput, Payment]):
    """
    Сценарий обработки платежа.

    Оркестрирует взаимодействие с портами:
    1. Валидация входных данных
    2. Вызов порта обработки платежа
    3. Логирование результата
    """

    def __init__(
            self,
            payment_processor: PaymentProcessorPort,
            transaction_logger: TransactionLoggerPort
    ):
        """
        Внедрение зависимостей через конструктор
        """
        self._payment_processor = payment_processor
        self._transaction_logger = transaction_logger

    def execute(self, input: ProcessPaymentInput) -> Payment:
        """
        Выполнить обработку платежа.

        Бизнес-правила:
        - Идентификатор платежа не может быть пустым
        - Сумма должна быть положительной
        - Валюта должна быть 3-буквенным кодом

        :param input: Входные данные платежа
        :return: Созданный платёж
        :raises ValueError: При невалидных входных данных
        :raises PaymentProcessingError: При ошибке обработки платежа
        """
        # Валидация входных данных (защита от некорректных вызовов)
        if not input.payment_id or not input.payment_id.strip():
            raise ValueError("payment_id must be non-empty")

        if input.amount <= Decimal("0"):
            raise ValueError("amount must be positive")

        if not input.currency or len(input.currency) != 3:
            raise ValueError("currency must be a 3-letter ISO code")

        # Создаём доменные объекты из входных данных
        payment_id = PaymentId(input.payment_id)
        amount = Amount(input.amount, input.currency)

        # Вызываем порт для обработки платежа
        payment = self._payment_processor.process_payment(
            payment_id=payment_id,
            amount=amount,
            description=input.description,
            customer_email=input.customer_email,
            meta=input.meta
        )

        # Логируем транзакцию через другой порт
        self._transaction_logger.log_transaction(payment)

        return payment