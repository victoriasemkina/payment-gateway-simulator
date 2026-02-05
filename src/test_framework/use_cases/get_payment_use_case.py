from ..domain.payment_api_port import PaymentApiPort
from ..dtos import PaymentResponse


class GetPaymentUseCase:
    """Сценарий получения платежа по идентификатору"""

    def __init__(self, payment_api_port: PaymentApiPort):
        self._payment_api_port = payment_api_port

    def execute(self, payment_id: str) -> PaymentResponse:
        """
        Выполнить получение платежа.

        :return: Ответ с информацией о платеже
        """
        return self._payment_api_port.get_payment(payment_id=payment_id)