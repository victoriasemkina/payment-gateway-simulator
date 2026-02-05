from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Amount:
    value: Decimal  # Сумма (например: Decimal("100.50"))
    currency: str  # Валюта (например: "USD", "EUR", "RUB")

    def __post_init__(self):
        if self.value <= Decimal("0"):
            raise ValueError("Amount must be positive")

        # Проверка 2: валюта должна быть 3-буквенным кодом (стандарт ISO 4217)
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code (e.g., USD, EUR, RUB)")

        # Нормализация: приводим валюту к верхнему регистру (USD, а не usd)
        normalized_currency = self.currency.upper()
        if normalized_currency != self.currency:
            object.__setattr__(self, 'currency', normalized_currency)

        # Округление до 2 знаков после запятой (как деньги)
        # Например: 99.999 → 100.00
        rounded_value = round(self.value, 2)
        if rounded_value != self.value:
            object.__setattr__(self, 'value', rounded_value)