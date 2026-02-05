from abc import ABC, abstractmethod
from typing import Optional

from ..payment import Payment
from ..payment_id import PaymentId
from ..amount import Amount
from ..exceptions import DomainError


class PaymentProcessorPort(ABC):
    """
    Абстрактный порт для обработки платежей.
    """

    @abstractmethod
    def process_payment(
            self,
            payment_id: PaymentId,
            amount: Amount,
            description: Optional[str] = None,
            customer_email: Optional[str] = None,
            metadata: Optional[dict] = None
    ) -> Payment:
        """
        Обработать платёж через внешний шлюз.

        :param payment_id: Уникальный идентификатор платежа
        :param amount: Сумма и валюта
        :param description: Описание платежа (опционально)
        :param customer_email: Email клиента (опционально)
        :param metadata: Дополнительные данные для шлюза (опционально)
        :return: Созданный платёж со статусом
        :raises PaymentProcessingError: Если платёж отклонён или произошла ошибка
        """
        pass

    @abstractmethod
    def refund_payment(
            self,
            payment_id: PaymentId,
            amount: Optional[Amount] = None,
            reason: Optional[str] = None
    ) -> Payment:
        """
        Вернуть платёж (полностью или частично).

        :param payment_id: Идентификатор платежа для возврата
        :param amount: Сумма возврата (если None — полный возврат)
        :param reason: Причина возврата (опционально)
        :return: Обновлённый платёж со статусом REFUNDED
        :raises PaymentProcessingError: Если возврат невозможен
        """
        pass