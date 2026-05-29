from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from src.core.cart import CartLine
from src.core.config import FiscalConfig

logger = logging.getLogger(__name__)

# Документация: docs/hardware/08-tbank-pos-printer.md
# CloudKassir + Т-Банк: https://www.tbank.ru/business/help/business-payments/internet-acquiring/kassa/how-connect/


@dataclass
class CloudFiscalResult:
    success: bool
    receipt_id: str = ""
    receipt_url: str = ""
    error: str = ""
    raw: dict[str, Any] | None = None


class CloudFiscalService:
    """Фискализация без УМКА: CloudKassir / Чеки Т-Бизнеса (API — после получения ключей)."""

    def __init__(self, config: FiscalConfig) -> None:
        self._cfg = config

    def print_receipt(
        self,
        lines: list[CartLine],
        total: float,
        payment_type: str,
        order_id: str,
    ) -> CloudFiscalResult:
        if not self._cfg.enabled:
            logger.info("Облачная касса отключена (mock OK)")
            return CloudFiscalResult(success=True, receipt_id=f"MOCK-{order_id}")

        provider = (self._cfg.provider or "none").lower()
        if provider in ("none", ""):
            logger.warning(
                "Фискализация включена, но provider=none — задайте cloudkassir или tbusiness"
            )
            return CloudFiscalResult(success=False, error="Не задан fiscal.provider")

        if self._cfg.use_mock:
            logger.info(
                "Облачный чек mock: %s, %.2f ₽, заказ %s (%d поз.)",
                provider,
                total,
                order_id,
                len(lines),
            )
            return CloudFiscalResult(
                success=True,
                receipt_id=f"CLOUD-MOCK-{order_id}",
                receipt_url="",
            )

        # TODO: CloudKassir API / API «Чеки Т-Бизнеса» после ключей от заказчика
        logger.error("Облачная касса %s: API не подключён", provider)
        return CloudFiscalResult(
            success=False,
            error=f"Интеграция {provider} не реализована — нужны API-ключи",
        )
