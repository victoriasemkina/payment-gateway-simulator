from typing import List
import json
from datetime import datetime

from ...domain.payment import Payment
from ...domain.payment_id import PaymentId
from ...domain.ports.transaction_logger import TransactionLoggerPort


class ConsoleLoggerAdapter(TransactionLoggerPort):
    """
    Адаптер для логирования транзакций в консоль (stdout).

    Формат лога: JSON для удобного парсинга и чтения.
    """

    def __init__(self, pretty: bool = False):
        """
        :param pretty: Если True — красивый многострочный JSON, иначе одна строка
        """
        self._pretty = pretty

    def log_transaction(self, payment: Payment) -> None:
        """
        Залогировать транзакцию в консоль.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "payment_id": payment.id.value,
            "amount": str(payment.amount.value),
            "currency": payment.amount.currency,
            "status": payment.status.value,
            "description": payment.description,
            "customer_email": payment.customer_email,
            "error_message": payment.error_message
        }

        if self._pretty:
            print(json.dumps(log_entry, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(log_entry, ensure_ascii=False))

    def get_transactions_by_payment_id(self, payment_id: PaymentId) -> List[Payment]:
        """
        Получить историю транзакций по ID.

        В консольном адаптере возвращаем пустой список — консоль не хранит историю.
        В реальных адаптерах (БД, файл) здесь будет запрос к хранилищу.
        """
        return []