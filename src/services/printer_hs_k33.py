from __future__ import annotations

import logging
import socket
from datetime import datetime

from src.core.cart import CartLine
from src.core.config import HardwarePrinterConfig

logger = logging.getLogger(__name__)

# Документация: docs/hardware/04-hs-k33-printer.md

_CUT = b"\n\n\n\x1dV\x00"


class PrinterHsK33Service:
    """Печать нефискальной квитанции (ESC/POS по RAW TCP)."""

    def __init__(self, config: HardwarePrinterConfig) -> None:
        self._cfg = config

    def print_text(self, text: str) -> bool:
        if not self._cfg.enabled or not text.strip():
            return True
        if self._cfg.connection != "ethernet":
            return False
        try:
            self._send_text(text)
            logger.info("HS-K33: напечатан текст чека (%d символов)", len(text))
            return True
        except OSError as exc:
            logger.error("HS-K33: ошибка печати чека: %s", exc)
            return False

    def print_test_receipt(self) -> bool:
        """Тестовый чек для проверки связи (игнорирует hardware.printer.enabled)."""
        if self._cfg.connection != "ethernet":
            logger.warning("HS-K33: тестовая печать доступна только для connection=ethernet")
            return False
        text = self._format_test_receipt()
        try:
            self._send_text(text)
            logger.info(
                "HS-K33: тестовый чек напечатан (%s:%s)",
                self._cfg.host,
                self._cfg.port,
            )
            return True
        except OSError as exc:
            logger.error("HS-K33: ошибка тестовой печати: %s", exc)
            return False

    def print_order_slip(self, lines: list[CartLine], total: float, order_id: str) -> bool:
        if not self._cfg.enabled:
            return True
        if self._cfg.connection != "ethernet":
            logger.warning("HS-K33: USB-режим не реализован, нужен драйвер HSPOS SDK")
            return False
        text = self._format_slip(lines, total, order_id)
        try:
            self._send_text(text)
            logger.info("HS-K33: квитанция напечатана заказ %s", order_id)
            return True
        except OSError as exc:
            logger.error("HS-K33: ошибка печати: %s", exc)
            return False

    def _send_text(self, text: str) -> None:
        with socket.create_connection((self._cfg.host, self._cfg.port), timeout=5) as sock:
            sock.sendall(text.encode("cp866", errors="replace"))
            sock.sendall(_CUT)

    def _format_test_receipt(self) -> str:
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        rows = [
            "=== ТЕСТОВЫЙ ЧЕК ===",
            "",
            "Сады Коломны",
            "Киоск самообслуживания",
            "",
            "Принтер: HS-K33",
            f"Адрес: {self._cfg.host}:{self._cfg.port}",
            "",
            "Связь: OK",
            f"Дата: {now}",
            "",
            "Если вы видите этот текст —",
            "печать настроена верно.",
            "",
            "------------------------",
        ]
        return "\n".join(rows)

    def _format_slip(self, lines: list[CartLine], total: float, order_id: str) -> str:
        rows = ["=== ФЕРМА ===", f"Заказ {order_id}", ""]
        for line in lines:
            rows.append(f"{line.product.name} x{line.quantity}  {line.line_total:.2f}")
        rows.append("")
        rows.append(f"ИТОГО: {total:.2f} руб.")
        rows.append("Спасибо за покупку!")
        return "\n".join(rows)
