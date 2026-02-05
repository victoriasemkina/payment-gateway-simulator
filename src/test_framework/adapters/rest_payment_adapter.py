import httpx
from decimal import Decimal
from typing import Optional

from ..domain.payment_api_port import PaymentApiPort
from ..dtos import PaymentResponse


class RestPaymentAdapter(PaymentApiPort):
    """
    Реализация порта через HTTP-вызовы к симулятору.

    Скрывает все технические детали:
    - Пути к эндпоинтам
    - Маппинг запросов/ответов
    - Обработку статус-кодов
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        :param base_url: Базовый URL симулятора
        """
        self._client = httpx.Client(base_url=base_url, timeout=10.0)
        self._base_url = base_url

    def create_payment(
            self,
            payment_id: str,
            amount: Decimal,
            currency: str,
            description: Optional[str] = None,
            customer_email: Optional[str] = None
    ) -> PaymentResponse:
        # Маппинг из доменных объектов в структуру запроса
        request_data = {
            "payment_id": payment_id,
            "amount": float(amount),
            "currency": currency,
            "description": description,
            "customer_email": customer_email
        }

        # Вызов реального симулятора через HTTP
        response = self._client.post("/api/pay", json=request_data)

        # Обработка статус-кодов в одном месте (как в рабочем проекте)
        if response.status_code == 422:
            error_detail = response.json().get("detail", "Validation error")
            raise ValueError(f"Validation error: {error_detail}")

        if response.status_code >= 500:
            raise RuntimeError(
                f"Server error {response.status_code}: {response.text}"
            )

        if response.status_code != 201:
            raise RuntimeError(
                f"Unexpected status {response.status_code}: {response.text}"
            )

        # Маппинг ответа в доменный объект
        data = response.json()
        return PaymentResponse(
            payment_id=data["payment_id"],
            amount=Decimal(str(data["amount"])),
            currency=data["currency"],
            status=data["status"],
            description=data.get("description"),
            customer_email=data.get("customer_email"),
            created_at=data.get("created_at", "")
        )

    def get_payment(self, payment_id: str) -> PaymentResponse:
        response = self._client.get(f"/api/pay/{payment_id}")

        if response.status_code == 404:
            raise RuntimeError(f"Payment {payment_id} not found")

        if response.status_code >= 500:
            raise RuntimeError(
                f"Server error {response.status_code}: {response.text}"
            )

        data = response.json()
        return PaymentResponse(
            payment_id=data["payment_id"],
            amount=Decimal(str(data["amount"])),
            currency=data["currency"],
            status=data["status"],
            description=data.get("description"),
            customer_email=data.get("customer_email"),
            created_at=data.get("created_at", "")
        )