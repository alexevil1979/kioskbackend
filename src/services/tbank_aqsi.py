from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any

import requests

from src.core.cart import CartLine
from src.core.config import HardwareAqsiConfig

logger = logging.getLogger(__name__)

# Документация: docs/hardware/07-tbank-aqsi.md
# API: https://api.aqsi.ru/#tag/Orders


@dataclass
class AqsiOrderResult:
    success: bool
    order_id: str = ""
    external_id: str = ""
    status: str = "pending"
    error: str = ""
    raw: dict[str, Any] | None = None


class AqsiOrderService:
    """Заказ в aQsi (Т-Банк «3 в 1»): оплата и фискальный чек на терминале."""

    def __init__(self, config: HardwareAqsiConfig) -> None:
        self._cfg = config
        self._session = requests.Session()
        if config.api_key:
            self._session.headers["Authorization"] = f"Bearer {config.api_key}"
        self._session.headers.setdefault("Content-Type", "application/json")

    def create_order(
        self,
        lines: list[CartLine],
        total: float,
        kiosk_order_id: str,
    ) -> AqsiOrderResult:
        external_id = kiosk_order_id or str(uuid.uuid4())[:12]
        if self._cfg.use_mock:
            logger.info("aQsi mock: заказ %s на %.2f ₽ (%d поз.)", external_id, total, len(lines))
            return AqsiOrderResult(
                success=True,
                order_id=f"MOCK-{external_id}",
                external_id=external_id,
                status="created",
            )

        if not self._cfg.api_key:
            return AqsiOrderResult(success=False, error="Не задан hardware.aqsi.api_key")

        body = self._build_order_body(lines, total, external_id)
        url = f"{self._cfg.api_base.rstrip('/')}/v2/Orders"
        try:
            r = self._session.post(url, json=body, timeout=self._cfg.timeout_sec)
            r.raise_for_status()
            data = r.json()
            order_id = str(data.get("id") or data.get("orderId") or "")
            logger.info("aQsi: заказ создан %s", order_id)
            return AqsiOrderResult(
                success=True,
                order_id=order_id,
                external_id=external_id,
                status=str(data.get("status", "created")),
                raw=data if isinstance(data, dict) else None,
            )
        except requests.RequestException as exc:
            logger.exception("aQsi: ошибка создания заказа")
            return AqsiOrderResult(success=False, external_id=external_id, error=str(exc))

    def poll_order_status(self, order_id: str) -> str:
        """pending | paid | failed | unknown"""
        if self._cfg.use_mock:
            return "paid"
        if not order_id or not self._cfg.api_key:
            return "unknown"
        url = f"{self._cfg.api_base.rstrip('/')}/v2/Orders/{order_id}"
        try:
            r = self._session.get(url, timeout=self._cfg.timeout_sec)
            r.raise_for_status()
            data = r.json()
            return str(data.get("status", "unknown")).lower()
        except requests.RequestException as exc:
            logger.warning("aQsi: poll %s: %s", order_id, exc)
            return "unknown"

    def _build_order_body(
        self,
        lines: list[CartLine],
        total: float,
        external_id: str,
    ) -> dict[str, Any]:
        """Минимальное тело — уточнить по OpenAPI api.aqsi.ru под ваш договор."""
        positions = [
            {
                "name": line.product.name,
                "quantity": line.quantity,
                "price": line.product.price_rub,
                "sku": line.product.id,
            }
            for line in lines
        ]
        return {
            "externalId": external_id,
            "comment": f"Киоск {external_id}",
            "positions": positions,
            "total": total,
        }
