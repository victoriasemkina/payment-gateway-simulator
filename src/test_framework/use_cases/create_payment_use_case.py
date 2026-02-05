from decimal import Decimal
from typing import Optional

from ..domain.payment_api_port import PaymentApiPort
from ..dtos import PaymentResponse


class CreatePaymentUseCase:
    """
    Сценарий создания платежа для тестов.

    Оркестрирует вызов порта — тесты работают через этот класс,
    а не напрямую с адаптером.
    """

    def __init__(self, payment_api_port: PaymentApiPort):
        """
        Внедрение зависимости через конструктор (как в рабочем проекте).

        :param payment_api_port: Абстракция для работы с платежным симулятором
        """
        self._payment_api_port = payment_api_port

    def execute(
            self,
            payment_id: str,
            amount: Decimal,
            currency: str,
            description: Optional[str] = None,
            customer_email: Optional[str] = None
    ) -> PaymentResponse:
        """
        Выполнить создание платежа.

        :return: Ответ с информацией о платеже
        """
        return self._payment_api_port.create_payment(
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            description=description,
            customer_email=customer_email
        )