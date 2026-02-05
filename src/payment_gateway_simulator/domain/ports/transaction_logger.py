from abc import ABC, abstractmethod
from typing import List

from ..payment import Payment
from ..payment_id import PaymentId


class TransactionLoggerPort(ABC):
    """
    Абстрактный порт для логирования транзакций.
    """

    @abstractmethod
    def log_transaction(self, payment: Payment) -> None:
        """
        Залогировать транзакцию.

        :param payment: Платёж для логирования
        """
        pass

    @abstractmethod
    def get_transactions_by_payment_id(self, payment_id: PaymentId) -> List[Payment]:
        """
        Получить историю транзакций по идентификатору платежа.

        :param payment_id: Идентификатор платежа
        :return: Список транзакций (обычно 1 основная + 0..N возвратов)
        """
        pass