from __future__ import annotations

import logging
import socket
from dataclasses import dataclass
from datetime import datetime

from src.core.cart import CartLine
from src.core.config import HardwarePrinterConfig

logger = logging.getLogger(__name__)

# Документация: docs/hardware/04-hs-k33-printer.md

_INIT = b"\x1b\x40"
_CUT = b"\n\n\n\x1dV\x00"
_PROBE_PORTS = (9100, 9101, 9200, 6001, 515)
_CONNECT_TIMEOUT = 8.0
_PROBE_TIMEOUT = 1.5


@dataclass(frozen=True, slots=True)
class PrinterProbeResult:
    ok: bool
    message: str
    open_ports: tuple[int, ...] = ()


class PrinterHsK33Service:
    """Печать нефискальной квитанции (ESC/POS по RAW TCP)."""

    def __init__(
        self,
        config: HardwarePrinterConfig,
        *,
        bind_ip: str = "",
    ) -> None:
        self._cfg = config
        self._bind_ip = (bind_ip or "").strip()

    def print_text(self, text: str) -> bool:
        if not self._cfg.enabled or not text.strip():
            return True
        ok, _ = self._print_text_with_detail(text)
        return ok

    def print_test_receipt(self) -> PrinterProbeResult:
        """Тестовый чек для проверки связи (игнорирует hardware.printer.enabled)."""
        if self._cfg.connection != "ethernet":
            return PrinterProbeResult(
                ok=False,
                message="Тестовая печать доступна только при connection=ethernet",
            )
        probe = self.probe()
        if not probe.ok:
            return probe
        ok, detail = self._print_text_with_detail(self._format_test_receipt())
        if ok:
            return PrinterProbeResult(
                ok=True,
                message="Тестовый чек отправлен на принтер.",
            )
        return PrinterProbeResult(ok=False, message=detail, open_ports=probe.open_ports)

    def probe(self) -> PrinterProbeResult:
        """Проверка TCP до принтера; при ошибке сканирует типовые порты."""
        if self._cfg.connection != "ethernet":
            return PrinterProbeResult(ok=False, message="Принтер не в режиме ethernet")
        target = f"{self._cfg.host}:{self._cfg.port}"
        try:
            with self._connect():
                return PrinterProbeResult(ok=True, message=f"Связь с {target} установлена")
        except OSError as exc:
            detail = _format_os_error(exc, target)
            open_ports = self._scan_ports()
            if open_ports and self._cfg.port not in open_ports:
                ports = ", ".join(str(p) for p in open_ports)
                detail = (
                    f"{detail} Открыты порты: {ports}. "
                    f"Укажите нужный в hardware.printer.port."
                )
            elif not open_ports:
                detail = (
                    f"{detail} TCP-порты не отвечают. "
                    "Если принтер на отдельном switch — задайте IP на Ethernet NUC "
                    "(hardware.nuc.lan_ip) и проверьте кабель."
                )
            if self._bind_ip:
                detail = f"{detail} (исходящий IP: {self._bind_ip})"
            return PrinterProbeResult(ok=False, message=detail, open_ports=open_ports)

    def print_order_slip(self, lines: list[CartLine], total: float, order_id: str) -> bool:
        if not self._cfg.enabled:
            return True
        if self._cfg.connection != "ethernet":
            logger.warning("HS-K33: USB-режим не реализован, нужен драйвер HSPOS SDK")
            return False
        ok, _ = self._print_text_with_detail(self._format_slip(lines, total, order_id))
        return ok

    def _print_text_with_detail(self, text: str) -> tuple[bool, str]:
        if self._cfg.connection != "ethernet":
            return False, "Печать доступна только при connection=ethernet"
        target = f"{self._cfg.host}:{self._cfg.port}"
        try:
            payload = _INIT + text.encode("cp866", errors="replace") + _CUT
            with self._connect() as sock:
                sock.sendall(payload)
            logger.info("HS-K33: напечатано на %s (%d символов)", target, len(text))
            return True, ""
        except OSError as exc:
            msg = _format_os_error(exc, target)
            logger.error("HS-K33: ошибка печати %s: %s", target, msg)
            return False, msg

    def _connect(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_CONNECT_TIMEOUT)
        if self._bind_ip:
            try:
                sock.bind((self._bind_ip, 0))
            except OSError as exc:
                sock.close()
                raise OSError(
                    f"Не удалось привязать сокет к {self._bind_ip}: {exc}. "
                    "Проверьте IP Ethernet-адаптера NUC в hardware.nuc.lan_ip"
                ) from exc
        sock.connect((self._cfg.host, self._cfg.port))
        return sock

    def _scan_ports(self) -> tuple[int, ...]:
        found: list[int] = []
        for port in _PROBE_PORTS:
            if port == self._cfg.port:
                continue
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(_PROBE_TIMEOUT)
            try:
                if self._bind_ip:
                    sock.bind((self._bind_ip, 0))
                sock.connect((self._cfg.host, port))
                found.append(port)
            except OSError:
                pass
            finally:
                sock.close()
        return tuple(found)

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


def _format_os_error(exc: OSError, target: str) -> str:
    winerr = getattr(exc, "winerror", None)
    if winerr == 10060:
        return f"Таймаут подключения к {target}"
    if winerr == 10061:
        return f"Порт {target.split(':')[-1]} закрыт на {target.rsplit(':', 1)[0]}"
    if winerr in (10051, 10065):
        return f"Хост {target} недоступен в сети"
    text = str(exc).strip() or exc.__class__.__name__
    return f"{target}: {text}"
