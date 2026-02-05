import pytest
import httpx
from decimal import Decimal
import uuid

from src.test_framework import (
    CreatePaymentUseCase,
    GetPaymentUseCase,
    RestPaymentAdapter,
)


class TestPaymentApi:
    """Интеграционные тесты для платежного API через фреймворк"""

    @pytest.fixture(scope="function")
    def payment_use_case(self):
        """Фикстура: создаёт сценарий создания платежа"""
        adapter = RestPaymentAdapter(base_url="http://127.0.0.1:8000")  # ← КЛЮЧЕВОЕ ИЗМЕНЕНИЕ
        return CreatePaymentUseCase(adapter)

    @pytest.fixture(scope="function")
    def get_payment_use_case(self):
        """Фикстура: сценарий получения платежа"""
        adapter = RestPaymentAdapter(base_url="http://127.0.0.1:8000")  # ← КЛЮЧЕВОЕ ИЗМЕНЕНИЕ
        return GetPaymentUseCase(adapter)

    @pytest.fixture(scope="function")
    def unique_payment_id(self):
        """Генерирует уникальный идентификатор платежа для каждого теста"""
        return f"pay_{uuid.uuid4().hex[:12]}"

    def test_health_check(self):
        """Проверка работоспособности сервиса напрямую"""
        response = httpx.get("http://127.0.0.1:8000/health", timeout=5.0)  # ← КЛЮЧЕВОЕ ИЗМЕНЕНИЕ

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "payment-gateway-simulator"

    def test_create_payment_success(self, payment_use_case, unique_payment_id):
        """Успешное создание платежа через тестовый фреймворк"""
        result = payment_use_case.execute(
            payment_id=unique_payment_id,
            amount=Decimal("100.50"),
            currency="USD",
            description="Integration test payment",
            customer_email="test@example.com"
        )

        assert result.payment_id == unique_payment_id
        assert result.amount == Decimal("100.50")
        assert result.currency == "USD"
        assert result.status == "succeeded"
        assert result.description == "Integration test payment"
        assert result.customer_email == "test@example.com"
        assert result.created_at

    def test_create_payment_duplicate_id(self, payment_use_case, unique_payment_id):
        """Повторный платёж с тем же ID возвращает ошибку"""
        payment_use_case.execute(
            payment_id=unique_payment_id,
            amount=Decimal("50.00"),
            currency="EUR"
        )

        with pytest.raises(RuntimeError) as exc_info:
            payment_use_case.execute(
                payment_id=unique_payment_id,
                amount=Decimal("75.00"),
                currency="EUR"
            )

        assert "already exists" in str(exc_info.value).lower()

    def test_create_payment_invalid_currency(self, payment_use_case, unique_payment_id):
        """Неверный код валюты возвращает ошибку валидации"""
        with pytest.raises(ValueError) as exc_info:
            payment_use_case.execute(
                payment_id=unique_payment_id,
                amount=Decimal("100.00"),
                currency="US"
            )

        assert "validation" in str(exc_info.value).lower()

    def test_create_payment_negative_amount(self, payment_use_case, unique_payment_id):
        """Отрицательная сумма возвращает ошибку валидации"""
        with pytest.raises(ValueError) as exc_info:
            payment_use_case.execute(
                payment_id=unique_payment_id,
                amount=Decimal("-10.00"),
                currency="USD"
            )

        assert "validation" in str(exc_info.value).lower()

    def test_get_payment(self, get_payment_use_case, unique_payment_id):
        """Получение информации о платеже по ID"""
        result = get_payment_use_case.execute(payment_id=unique_payment_id)

        assert result.payment_id == unique_payment_id
        assert result.status == "succeeded"