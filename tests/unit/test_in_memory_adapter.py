# -*- coding: utf-8 -*-
"""
Юнит-тесты для InMemoryPaymentAdapter

Проверяем:
- Успешную обработку платежа
- Отказ при дублировании payment_id
- Успешный возврат платежа
- Отказ при возврате несуществующего платежа
"""
import pytest
from decimal import Decimal
from datetime import datetime

from src.payment_gateway_simulator.domain import (
    PaymentId,
    Amount,
    PaymentStatus,
    PaymentProcessingError,
)
from src.payment_gateway_simulator.adapters.payment import InMemoryPaymentAdapter


class TestInMemoryPaymentAdapter:
    """Тесты для in-memory адаптера обработки платежей"""

    def test_process_payment_success(self):
        """Успешная обработка платежа"""
        adapter = InMemoryPaymentAdapter()

        payment = adapter.process_payment(
            payment_id=PaymentId("pay_123"),
            amount=Amount(Decimal("100.00"), "USD"),
            description="Test payment",
            customer_email="test@example.com"
        )

        assert payment.id.value == "pay_123"
        assert payment.amount.value == Decimal("100.00")
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.description == "Test payment"
        assert payment.customer_email == "test@example.com"

    def test_process_payment_duplicate_id_raises_error(self):
        """Попытка создать платёж с существующим ID вызывает ошибку"""
        adapter = InMemoryPaymentAdapter()

        # Первый платёж — успешен
        adapter.process_payment(
            payment_id=PaymentId("pay_duplicate"),
            amount=Amount(Decimal("50.00"), "EUR")
        )

        # Второй платёж с тем же ID — ошибка
        with pytest.raises(PaymentProcessingError, match="already exists"):
            adapter.process_payment(
                payment_id=PaymentId("pay_duplicate"),
                amount=Amount(Decimal("75.00"), "EUR")
            )

    def test_refund_payment_success(self):
        """Успешный возврат платежа"""
        adapter = InMemoryPaymentAdapter()

        # Сначала создаём платёж
        original = adapter.process_payment(
            payment_id=PaymentId("pay_refund"),
            amount=Amount(Decimal("200.00"), "GBP")
        )

        # Затем возвращаем его
        refunded = adapter.refund_payment(
            payment_id=PaymentId("pay_refund"),
            reason="Customer request"
        )

        assert refunded.id.value == "pay_refund"
        assert refunded.amount.value == Decimal("200.00")  # Полный возврат
        assert refunded.status == PaymentStatus.REFUNDED
        assert "refund" in refunded.description.lower()

    def test_refund_payment_not_found_raises_error(self):
        """Попытка вернуть несуществующий платёж вызывает ошибку"""
        adapter = InMemoryPaymentAdapter()

        with pytest.raises(PaymentProcessingError, match="not found"):
            adapter.refund_payment(
                payment_id=PaymentId("non_existent_payment")
            )

    def test_partial_refund(self):
        """Частичный возврат платежа"""
        adapter = InMemoryPaymentAdapter()

        # Создаём платёж на 100.00
        adapter.process_payment(
            payment_id=PaymentId("pay_partial"),
            amount=Amount(Decimal("100.00"), "USD")
        )

        # Возвращаем только 30.00
        partial_refund = adapter.refund_payment(
            payment_id=PaymentId("pay_partial"),
            amount=Amount(Decimal("30.00"), "USD"),
            reason="Partial refund"
        )

        assert partial_refund.amount.value == Decimal("30.00")
        assert partial_refund.status == PaymentStatus.REFUNDED

    def test_adapter_state_isolation(self):
        """Разные экземпляры адаптера не делят состояние"""
        adapter1 = InMemoryPaymentAdapter()
        adapter2 = InMemoryPaymentAdapter()

        # Создаём платёж в первом адаптере
        adapter1.process_payment(
            payment_id=PaymentId("pay_isolated"),
            amount=Amount(Decimal("10.00"), "USD")
        )

        # Во втором адаптере платёж не существует
        with pytest.raises(PaymentProcessingError, match="not found"):
            adapter2.refund_payment(PaymentId("pay_isolated"))