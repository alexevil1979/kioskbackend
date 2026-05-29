from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SbpPaymentSession:
    payment_id: str
    qr_payload: str
    amount_rub: float


class SbpPaymentService:
    """Заглушка СБП — заменить на API банка."""

    def create_payment(self, amount_rub: float, order_id: str) -> SbpPaymentSession:
        pid = str(uuid.uuid4())
        payload = f"ST00012|Name=Ферма|Sum={amount_rub:.2f}|Purpose=Заказ {order_id}"
        logger.info("СБП: создан платёж %s на %.2f ₽", pid, amount_rub)
        return SbpPaymentSession(payment_id=pid, qr_payload=payload, amount_rub=amount_rub)

    def check_status(self, payment_id: str) -> str:
        """pending | paid | failed | expired"""
        return "pending"

    def cancel(self, payment_id: str) -> None:
        logger.info("СБП: отмена %s", payment_id)
