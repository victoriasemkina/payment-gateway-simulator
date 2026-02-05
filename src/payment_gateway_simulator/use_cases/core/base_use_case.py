from abc import ABC, abstractmethod
from typing import Generic, TypeVar

I = TypeVar('I')  # Тип входного параметра
O = TypeVar('O')  # Тип выходного результата


class BaseUseCase(ABC, Generic[I, O]):
    """
    Абстрактный базовый класс для всех сценариев использования (Use Cases).
    """

    @abstractmethod
    def execute(self, input: I) -> O:
        """
        Выполнить бизнес-сценарий.

        :param input: Входные данные сценария
        :return: Результат выполнения
        :raises DomainError: При ошибках валидации или бизнес-логики
        """
        pass