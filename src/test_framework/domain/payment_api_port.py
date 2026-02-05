from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from ..dtos import PaymentResponse


class PaymentApiPort(ABC):
    """
    Абстракция для работы с платежным симулятором.
    Тесты зависят от этого порта, а не от конкретной реализации (HTTP-вызовов).
    """

    @abstractmethod
    def create_payment(
            self,
            payment_id: str,
            amount: Decimal,
            currency: str,
            description: Optional[str] = None,
            customer_email: Optional[str] = None
    ) -> PaymentResponse:
        """
        Создать платёж через симулятор.

        :param payment_id: Идентификатор платежа
        :param amount: Сумма
        :param currency: Валюта (3-буквенный код)
        :param description: Описание (опционально)
        :param customer_email: Email клиента (опционально)
        :return: Ответ с информацией о платеже
        :raises ValueError: При ошибках валидации
        :raises RuntimeError: При ошибках сервера
        """
        pass

    @abstractmethod
    def get_payment(self, payment_id: str) -> PaymentResponse:
        """
        Получить информацию о платеже по идентификатору.

        :param payment_id: Идентификатор платежа
        :return: Ответ с информацией о платеже
        :raises RuntimeError: Если платёж не найден
        """
        pass