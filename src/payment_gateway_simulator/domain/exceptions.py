class DomainError(Exception):
    """Базовый класс для всех доменных ошибок"""
    pass


class InvalidPaymentIdError(DomainError, ValueError):
    """Исключение для невалидного идентификатора платежа"""
    def __init__(self, message: str):
        super().__init__(f"InvalidPaymentIdError: {message}")


class InvalidAmountError(DomainError, ValueError):
    """Исключение для невалидной суммы"""
    def __init__(self, message: str):
        super().__init__(f"InvalidAmountError: {message}")


class PaymentProcessingError(DomainError):
    """Исключение при обработке платежа (например, отказ карты)"""
    def __init__(self, message: str, payment_id: str = None):
        self.payment_id = payment_id
        detail = f" (payment_id={payment_id})" if payment_id else ""
        super().__init__(f"PaymentProcessingError: {message}{detail}")