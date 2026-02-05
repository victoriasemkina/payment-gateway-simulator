from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

from ...use_cases import ProcessPaymentUseCase, ProcessPaymentInput
from ...adapters.payment import InMemoryPaymentAdapter
from ...adapters.logging import ConsoleLoggerAdapter
from ...domain import Payment, PaymentStatus

# Создаём роутер
router = APIRouter(tags=["payments"])


# === DTO для запросов/ответов ===

class PaymentRequest(BaseModel):
    """
    Запрос на создание платежа
    """
    payment_id: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3, pattern="^[A-Z]{3}$")
    description: Optional[str] = Field(None, max_length=500)
    customer_email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    meta: Optional[dict] = None


class PaymentResponse(BaseModel):
    """
    Ответ с информацией о платеже
    """
    payment_id: str
    amount: float
    currency: str
    status: str
    description: Optional[str] = None
    customer_email: Optional[str] = None
    created_at: str


# === Инициализация зависимостей ===

# Создаём адаптеры (реализации портов)
_payment_adapter = InMemoryPaymentAdapter()
_logger_adapter = ConsoleLoggerAdapter(pretty=False)

# Создаём Use Case с внедрёнными адаптерами
_payment_use_case = ProcessPaymentUseCase(
    payment_processor=_payment_adapter,
    transaction_logger=_logger_adapter
)


# === Эндпоинты ===

@router.post("/pay", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(request: PaymentRequest):
    """
    Создать платёж
    """
    try:
        # Выполняем сценарий с реальными адаптерами (как в рабочем проекте!)
        payment: Payment = _payment_use_case.execute(
            ProcessPaymentInput(
                payment_id=request.payment_id,
                amount=Decimal(str(request.amount)),
                currency=request.currency,
                description=request.description,
                customer_email=request.customer_email,
                meta=request.meta
            )
        )

        # Преобразуем доменный объект в DTO для ответа
        return PaymentResponse(
            payment_id=payment.id.value,
            amount=float(payment.amount.value),
            currency=payment.amount.currency,
            status=payment.status.value,
            description=payment.description,
            customer_email=payment.customer_email,
            created_at=payment.created_at.isoformat()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )


@router.get("/pay/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """
    Получить информацию о платеже по ID

    Пока возвращает заглушку — в будущем можно добавить хранилище
    """
    # Для демо: возвращаем фиктивный платёж
    return PaymentResponse(
        payment_id=payment_id,
        amount=100.0,
        currency="USD",
        status=PaymentStatus.SUCCEEDED.value,
        description="Demo payment",
        customer_email="demo@example.com",
        created_at="2026-02-04T12:00:00"
    )