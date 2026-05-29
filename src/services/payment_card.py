from __future__ import annotations

import logging
import socket
import subprocess
from dataclasses import dataclass

from src.core.config import HardwareTbankTerminalConfig, PaymentConfig

logger = logging.getLogger(__name__)

# Документация: docs/hardware/05-tbank-terminal.md
# Целевой протокол: INPAS Smart Sale, TCP (порт по умолчанию 27015)


@dataclass
class CardPaymentResult:
    success: bool
    message: str = ""
    auth_code: str = ""


class CardPaymentService:
    """Оплата картой через POS Т-Банк (Smart Sale)."""

    def __init__(self, payment: PaymentConfig, terminal: HardwareTbankTerminalConfig) -> None:
        self._legacy_path = payment.card_terminal_path
        self._terminal = terminal

    def pay(self, amount_rub: float, order_id: str) -> CardPaymentResult:
        if self._terminal.use_mock:
            logger.info("POS mock: %.2f ₽ заказ %s (Smart Sale %s:%s)",
                        amount_rub, order_id, self._terminal.host, self._terminal.port)
            return CardPaymentResult(success=True, message="mock")

        if not self._terminal.smart_sale_enabled:
            return self._legacy_exe(amount_rub, order_id)

        return self._smart_sale_pay(amount_rub, order_id)

    def _legacy_exe(self, amount_rub: float, order_id: str) -> CardPaymentResult:
        if self._legacy_path:
            try:
                subprocess.Popen(
                    [self._legacy_path, str(amount_rub), order_id],
                    creationflags=subprocess.CREATE_NO_WINDOW
                    if hasattr(subprocess, "CREATE_NO_WINDOW")
                    else 0,
                )
                return CardPaymentResult(success=True, message="Ожидание терминала (exe)")
            except OSError as exc:
                return CardPaymentResult(success=False, message=str(exc))
        return CardPaymentResult(
            success=False,
            message="Укажите Smart Sale или путь к POS в config/settings.yaml",
        )

    def _smart_sale_pay(self, amount_rub: float, order_id: str) -> CardPaymentResult:
        """
        Заглушка TCP: проверяем доступность порта.
        Реальный пакет Smart Sale — после получения SDK от Т-Банка.
        """
        host, port = self._terminal.host, self._terminal.port
        amount_kop = int(round(amount_rub * 100))
        try:
            with socket.create_connection((host, port), timeout=3):
                logger.info(
                    "POS: порт %s:%s доступен, сумма %s коп (заказ %s) — нужен SDK Smart Sale",
                    host,
                    port,
                    amount_kop,
                    order_id,
                )
                return CardPaymentResult(
                    success=False,
                    message="Smart Sale: подключите SDK INPAS от банка",
                )
        except OSError as exc:
            logger.error("POS: нет связи %s:%s — %s", host, port, exc)
            return CardPaymentResult(success=False, message=f"Терминал недоступен: {exc}")
