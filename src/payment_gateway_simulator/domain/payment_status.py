from enum import Enum

class PaymentStatus(Enum):
    """
    Статус платежа — перечисление возможных состояний
    """
    PENDING = "pending"      # Платёж в обработке
    SUCCEEDED = "succeeded"  # Платёж успешен
    FAILED = "failed"        # Платёж провален
    REFUNDED = "refunded"    # Платёж возвращён