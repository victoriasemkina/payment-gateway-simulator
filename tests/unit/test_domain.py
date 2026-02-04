import pytest
from datetime import datetime
from decimal import Decimal

# Импортируем все классы из доменного слоя
from src.payment_gateway.domain import (
    PaymentStatus,
    PaymentId,
    Amount,
    Payment,
)


# ============================================================================
# Тесты для PaymentStatus (перечисление)
# ============================================================================

class TestPaymentStatus:
    """Тесты для перечисления статусов платежа"""

    def test_all_statuses_exist(self):
        """Проверяем, что все ожидаемые статусы существуют"""
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.SUCCEEDED.value == "succeeded"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.REFUNDED.value == "refunded"

    def test_status_comparison(self):
        """Проверяем сравнение статусов"""
        assert PaymentStatus.SUCCEEDED == PaymentStatus.SUCCEEDED
        assert PaymentStatus.SUCCEEDED != PaymentStatus.FAILED


# ============================================================================
# Тесты для PaymentId (Value Object)
# ============================================================================

class TestPaymentId:
    """Тесты для идентификатора платежа"""

    def test_valid_payment_id(self):
        """Успешное создание корректного PaymentId"""
        payment_id = PaymentId("pay_12345")
        assert payment_id.value == "pay_12345"

    def test_empty_payment_id_raises_error(self):
        """Пустой идентификатор вызывает ошибку"""
        with pytest.raises(ValueError, match="non-empty"):
            PaymentId("")

    def test_none_payment_id_raises_error(self):
        """None в качестве идентификатора вызывает ошибку"""
        with pytest.raises(ValueError):
            PaymentId(None)  # type: ignore

    def test_whitespace_payment_id_raises_error(self):
        """Идентификатор из пробелов вызывает ошибку"""
        with pytest.raises(ValueError, match="non-empty"):
            PaymentId("   ")

    def test_too_long_payment_id_raises_error(self):
        """Слишком длинный идентификатор вызывает ошибку"""
        long_id = "x" * 101
        with pytest.raises(ValueError, match="longer than 100"):
            PaymentId(long_id)

    def test_payment_id_is_immutable(self):
        """PaymentId неизменяемый (frozen)"""
        payment_id = PaymentId("pay_123")
        with pytest.raises(AttributeError):
            payment_id.value = "new_id"  # type: ignore


# ============================================================================
# Тесты для Amount (Value Object)
# ============================================================================

class TestAmount:
    """Тесты для суммы платежа"""

    def test_valid_amount(self):
        """Успешное создание корректной суммы"""
        amount = Amount(Decimal("100.50"), "USD")
        assert amount.value == Decimal("100.50")
        assert amount.currency == "USD"

    def test_negative_amount_raises_error(self):
        """Отрицательная сумма вызывает ошибку"""
        with pytest.raises(ValueError, match="positive"):
            Amount(Decimal("-10"), "USD")

    def test_zero_amount_raises_error(self):
        """Нулевая сумма вызывает ошибку"""
        with pytest.raises(ValueError, match="positive"):
            Amount(Decimal("0"), "USD")

    def test_invalid_currency_length_raises_error(self):
        """Неверная длина кода валюты вызывает ошибку"""
        with pytest.raises(ValueError, match="3-letter"):
            Amount(Decimal("100"), "US")  # Только 2 символа

    def test_empty_currency_raises_error(self):
        """Пустая валюта вызывает ошибку"""
        with pytest.raises(ValueError, match="3-letter"):
            Amount(Decimal("100"), "")

    def test_amount_rounding(self):
        """Сумма округляется до 2 знаков"""
        amount = Amount(Decimal("99.999"), "EUR")
        assert amount.value == Decimal("100.00")

    def test_currency_normalization(self):
        """Валюта нормализуется к верхнему регистру"""
        amount = Amount(Decimal("50.00"), "rub")
        assert amount.currency == "RUB"

    def test_amount_is_immutable(self):
        """Amount неизменяемый (frozen)"""
        amount = Amount(Decimal("100.00"), "USD")
        with pytest.raises(AttributeError):
            amount.value = Decimal("200.00")  # type: ignore


# ============================================================================
# Тесты для Payment (Entity)
# ============================================================================

class TestPayment:
    """Тесты для сущности платежа"""

    def test_create_successful_payment(self):
        """Создание успешного платежа"""
        payment = Payment(
            id=PaymentId("pay_123"),
            amount=Amount(Decimal("100.00"), "USD"),
            status=PaymentStatus.SUCCEEDED,
            created_at=datetime.now(),
            description="Test payment",
            customer_email="test@example.com"
        )

        assert payment.id.value == "pay_123"
        assert payment.amount.value == Decimal("100.00")
        assert payment.amount.currency == "USD"
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.description == "Test payment"
        assert payment.customer_email == "test@example.com"
        assert payment.is_successful() is True
        assert payment.is_failed() is False

    def test_create_failed_payment(self):
        """Создание проваленного платежа"""
        payment = Payment(
            id=PaymentId("pay_456"),
            amount=Amount(Decimal("50.00"), "EUR"),
            status=PaymentStatus.FAILED,
            created_at=datetime.now(),
            error_message="Card declined"
        )

        assert payment.is_failed() is True
        assert payment.error_message == "Card declined"
        assert payment.is_successful() is False

    def test_payment_is_immutable(self):
        """Платёж неизменяемый (frozen)"""
        payment = Payment(
            id=PaymentId("pay_789"),
            amount=Amount(Decimal("200.00"), "GBP"),
            status=PaymentStatus.PENDING,
            created_at=datetime.now()
        )

        # Попытка изменить поле должна вызвать ошибку
        with pytest.raises(AttributeError):
            payment.status = PaymentStatus.SUCCEEDED  # type: ignore

    def test_payment_str_representation(self):
        """Проверка строкового представления платежа"""
        payment = Payment(
            id=PaymentId("pay_123"),
            amount=Amount(Decimal("100.00"), "USD"),
            status=PaymentStatus.SUCCEEDED,
            created_at=datetime(2026, 2, 4, 15, 30, 0)
        )

        result = str(payment)
        assert "pay_123" in result
        assert "100.00 USD" in result
        assert "succeeded" in result

    def test_optional_fields_can_be_none(self):
        """Опциональные поля могут быть None"""
        payment = Payment(
            id=PaymentId("pay_999"),
            amount=Amount(Decimal("1.00"), "USD"),
            status=PaymentStatus.PENDING,
            created_at=datetime.now()
            # description, customer_email, error_message не указаны — будут None
        )

        assert payment.description is None
        assert payment.customer_email is None
        assert payment.error_message is None