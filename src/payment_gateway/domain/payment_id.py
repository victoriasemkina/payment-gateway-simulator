from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class PaymentId:
    value: str

    def __post_init__(self):
        # Проверка 1: значение должно быть строкой
        if not isinstance(self.value, str):
            raise ValueError("PaymentId must be a string")

        # Проверка 2: строка не должна быть пустой или состоять только из пробелов
        if not self.value.strip():
            raise ValueError("PaymentId must be a non-empty string")

        # Проверка 3: длина не должна превышать 100 символов
        if len(self.value) > 100:
            raise ValueError("PaymentId cannot be longer than 100 characters")