"""
Юнит-тесты для ConsoleLoggerAdapter

Проверяем:
- Формат лога (JSON)
- Содержимое полей лога
- Работу параметра pretty
"""
import json
from decimal import Decimal
from datetime import datetime

from src.payment_gateway_simulator.domain import (
    Payment,
    PaymentId,
    Amount,
    PaymentStatus,
)
from src.payment_gateway_simulator.adapters.logging import ConsoleLoggerAdapter


class TestConsoleLoggerAdapter:
    """Тесты для консольного адаптера логирования"""

    def test_log_transaction_outputs_json(self, capsys):
        """Лог транзакции выводится в формате JSON"""
        logger = ConsoleLoggerAdapter(pretty=False)

        payment = Payment(
            id=PaymentId("pay_json_test"),
            amount=Amount(Decimal("42.99"), "EUR"),
            status=PaymentStatus.SUCCEEDED,
            created_at=datetime.now(),
            description="JSON test",
            customer_email="test@example.com"
        )

        logger.log_transaction(payment)

        # Захватываем вывод консоли
        captured = capsys.readouterr()
        log_line = captured.out.strip()

        # Проверяем, что вывод — валидный JSON
        log_data = json.loads(log_line)

        assert log_data["payment_id"] == "pay_json_test"
        assert log_data["amount"] == "42.99"
        assert log_data["currency"] == "EUR"
        assert log_data["status"] == "succeeded"
        assert log_data["description"] == "JSON test"
        assert log_data["customer_email"] == "test@example.com"
        assert "timestamp" in log_data

    def test_log_transaction_pretty_format(self, capsys):
        """Лог в красивом формате содержит переносы строк"""
        logger = ConsoleLoggerAdapter(pretty=True)

        payment = Payment(
            id=PaymentId("pay_pretty"),
            amount=Amount(Decimal("1.00"), "USD"),
            status=PaymentStatus.FAILED,
            created_at=datetime.now(),
            error_message="Card declined"
        )

        logger.log_transaction(payment)

        captured = capsys.readouterr()
        log_output = captured.out

        # Красивый формат содержит переносы строк и отступы
        assert "\n" in log_output
        assert "  " in log_output  # отступы

    def test_get_transactions_returns_empty_list(self):
        """Консольный адаптер не хранит историю — возвращает пустой список"""
        logger = ConsoleLoggerAdapter()

        transactions = logger.get_transactions_by_payment_id(PaymentId("any_id"))

        assert transactions == []