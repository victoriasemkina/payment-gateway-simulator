import pytest
from unittest.mock import Mock
from decimal import Decimal
from datetime import datetime

from src.payment_gateway_simulator.domain import (
    Payment,
    PaymentId,
    Amount,
    PaymentStatus,
)
from src.payment_gateway_simulator.use_cases import (
    ProcessPaymentUseCase,
    ProcessPaymentInput,
)


class TestProcessPaymentUseCase:
    """Тесты для сценария обработки платежа"""

    def test_successful_payment_execution(self):
        """Успешная обработка платежа через моки портов"""
        # 1. Создаём моки портов (как в рабочем проекте!)
        mock_processor = Mock()
        mock_logger = Mock()

        # Настраиваем поведение мока процессора
        expected_payment = Payment(
            id=PaymentId("pay_test"),
            amount=Amount(Decimal("100.00"), "USD"),
            status=PaymentStatus.SUCCEEDED,
            created_at=datetime.now()
        )
        mock_processor.process_payment.return_value = expected_payment

        # 2. Создаём Use Case с моками (инверсия зависимостей!)
        use_case = ProcessPaymentUseCase(
            payment_processor=mock_processor,
            transaction_logger=mock_logger
        )

        # 3. Выполняем сценарий
        input_data = ProcessPaymentInput(
            payment_id="pay_test",
            amount=Decimal("100.00"),
            currency="USD",
            description="Test payment",
            customer_email="test@example.com"
        )
        result = use_case.execute(input_data)

        # 4. Проверяем результат и вызовы моков
        assert result == expected_payment
        assert result.status == PaymentStatus.SUCCEEDED

        # Проверяем, что процессор был вызван с правильными аргументами
        mock_processor.process_payment.assert_called_once()
        call_args = mock_processor.process_payment.call_args
        assert call_args.kwargs["payment_id"].value == "pay_test"
        assert call_args.kwargs["amount"].value == Decimal("100.00")
        assert call_args.kwargs["amount"].currency == "USD"

        # Проверяем, что логгер был вызван
        mock_logger.log_transaction.assert_called_once_with(expected_payment)

    def test_validation_rejects_empty_payment_id(self):
        """Валидация отклоняет пустой идентификатор платежа"""
        use_case = ProcessPaymentUseCase(Mock(), Mock())

        with pytest.raises(ValueError, match="non-empty"):
            use_case.execute(ProcessPaymentInput(
                payment_id="",
                amount=Decimal("50.00"),
                currency="EUR"
            ))

    def test_validation_rejects_whitespace_payment_id(self):
        """Валидация отклоняет идентификатор из пробелов"""
        use_case = ProcessPaymentUseCase(Mock(), Mock())

        with pytest.raises(ValueError, match="non-empty"):
            use_case.execute(ProcessPaymentInput(
                payment_id="   ",
                amount=Decimal("50.00"),
                currency="EUR"
            ))

    def test_validation_rejects_negative_amount(self):
        """Валидация отклоняет отрицательную сумму"""
        use_case = ProcessPaymentUseCase(Mock(), Mock())

        with pytest.raises(ValueError, match="positive"):
            use_case.execute(ProcessPaymentInput(
                payment_id="pay_negative",
                amount=Decimal("-10.00"),
                currency="USD"
            ))

    def test_validation_rejects_invalid_currency(self):
        """Валидация отклоняет неверный код валюты"""
        use_case = ProcessPaymentUseCase(Mock(), Mock())

        with pytest.raises(ValueError, match="3-letter"):
            use_case.execute(ProcessPaymentInput(
                payment_id="pay_invalid_currency",
                amount=Decimal("100.00"),
                currency="US"  # Только 2 символа
            ))

    def test_use_case_does_not_depend_on_concrete_adapters(self):
        """
        Use Case зависит ТОЛЬКО от абстракций (портов), а не от конкретных адаптеров.

        Это ключевой принцип архитектуры!
        """
        # Проверяем, что в коде Use Case нет импортов из адаптеров
        import inspect
        import src.payment_gateway_simulator.use_cases.process_payment as module

        source = inspect.getsource(module)
        assert "adapters" not in source.lower(), \
            "Use Case не должен зависеть от адаптеров!"
        assert "in_memory" not in source.lower(), \
            "Use Case не должен знать о конкретных реализациях!"
        assert "console" not in source.lower(), \
            "Use Case должен зависеть только от портов!"