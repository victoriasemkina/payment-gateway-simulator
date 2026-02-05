from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.payments import router as payments_router

# Создаём приложение
app = FastAPI(
    title="Payment Gateway Simulator",
    description="Mock для внешних платёжных шлюзов (аналог Stripe/PayPal)",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Разрешаем CORS (чтобы тесты из браузера/других сервисов могли вызывать API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(payments_router, prefix="/api")


@app.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса
    """
    return {"status": "ok", "service": "payment-gateway-simulator"}