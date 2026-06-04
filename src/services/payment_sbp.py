from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from src.core.cart import Cart
from src.core.config import Settings
from src.models.order import OrderCreateResult, OrderReceiptResult
from src.services.crm_client import CRMClient
from src.services.kiosk_order import cart_lines_to_order_items

logger = logging.getLogger(__name__)


@dataclass
class SbpPaymentSession:
    payment_id: str
    qr_payload: str
    amount_rub: float
    order_id: int = 0
    qr_image_b64: str = ""
    expires_in_seconds: int = 300
    use_api_polling: bool = False


class SbpPaymentService:
    """СБП: Katusha Kiosk API (qr_sbp) или локальная заглушка."""

    def __init__(self, settings: Settings, crm: CRMClient) -> None:
        self._settings = settings
        self._crm = crm
        self._mock = settings.crm.use_mock or settings.payment.sbp.use_mock
        self._use_api = (
            not self._mock
            and crm.supports_kiosk_orders
        )

    @property
    def uses_katusha_api(self) -> bool:
        return self._use_api

    def create_payment(self, cart: Cart, kiosk_order_id: str) -> SbpPaymentSession:
        if self._use_api:
            return self._create_via_api(cart, kiosk_order_id)
        return self._create_mock(cart.total_rub, kiosk_order_id)

    def _create_via_api(self, cart: Cart, kiosk_order_id: str) -> SbpPaymentSession:
        if not self._crm.is_online():
            raise RuntimeError("API киоска недоступен")

        items = cart_lines_to_order_items(cart.lines)
        order: OrderCreateResult = self._crm.create_order(
            items,
            "qr_sbp",
            kiosk_order_id=kiosk_order_id,
        )
        payload = order.qr_code_payload
        if not payload and not order.qr_code_image:
            raise RuntimeError("API не вернул QR для оплаты СБП")

        logger.info(
            "СБП API: заказ %s, сумма %.2f ₽, истекает через %s с",
            order.order_id,
            order.total_amount,
            order.expires_in_seconds,
        )
        return SbpPaymentSession(
            payment_id=order.payment_id or str(order.order_id),
            qr_payload=payload,
            amount_rub=order.total_amount or cart.total_rub,
            order_id=order.order_id,
            qr_image_b64=order.qr_code_image,
            expires_in_seconds=order.expires_in_seconds,
            use_api_polling=True,
        )

    def _create_mock(self, amount_rub: float, order_id: str) -> SbpPaymentSession:
        pid = str(uuid.uuid4())
        payload = f"ST00012|Name=Катюша|Sum={amount_rub:.2f}|Purpose=Заказ {order_id}"
        logger.info("СБП mock: платёж %s на %.2f ₽", pid, amount_rub)
        return SbpPaymentSession(
            payment_id=pid,
            qr_payload=payload,
            amount_rub=amount_rub,
            use_api_polling=False,
        )

    def check_status(self, order_id: int) -> str:
        """pending | paid | failed | expired | cancelled"""
        if not self._use_api or not order_id:
            return "pending"

        try:
            status = self._crm.get_order_status(order_id)
        except Exception as exc:
            logger.warning("СБП: ошибка опроса статуса заказа %s: %s", order_id, exc)
            return "pending"

        if status.paid:
            logger.info("СБП: заказ %s оплачен (%s)", order_id, status.payment_status)
            return "paid"
        if status.cancelled:
            return "cancelled"
        ps = status.payment_status.upper()
        if ps in ("FAILED", "REJECTED", "DECLINED"):
            return "failed"
        if ps in ("EXPIRED",):
            return "expired"
        return "pending"

    def fetch_receipt(self, order_id: int) -> OrderReceiptResult | None:
        if not self._use_api or not order_id:
            return None
        try:
            return self._crm.get_order_receipt(order_id)
        except Exception as exc:
            logger.error("СБП: не удалось получить чек заказа %s: %s", order_id, exc)
            return None

    def cancel(self, payment_id: str) -> None:
        logger.info("СБП: отмена %s (ожидание истечения на сервере)", payment_id)
