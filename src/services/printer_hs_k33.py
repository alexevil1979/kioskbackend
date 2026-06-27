from __future__ import annotations

import logging
import socket
import sys
from dataclasses import dataclass
from datetime import datetime

from src.core.cart import CartLine
from src.core.config import HardwarePrinterConfig
from src.services import printer_windows_spooler as win_print

logger = logging.getLogger(__name__)

# Документация: docs/hardware/04-hs-k33-printer.md

_INIT = b"\x1b\x40"
# ESC t 17 — таблица CP866 (как на самотесте принтера HS-K33)
_CP866_TABLE = b"\x1b\x74\x11"
_CUT = b"\n\n\n\x1dV\x00"
# Подача ленты перед отрезкой (ESC d n)
_FEED_BEFORE_CUT = b"\x1b\x64\x05"
_PROBE_PORTS = (9100, 9101, 9200, 6001, 515)
_CONNECT_TIMEOUT = 8.0
_PROBE_TIMEOUT = 1.5


@dataclass(frozen=True, slots=True)
class PrinterProbeResult:
    ok: bool
    message: str
    open_ports: tuple[int, ...] = ()


class PrinterHsK33Service:
    """Печать нефискальной квитанции: Ethernet RAW TCP или USB (очередь Windows)."""

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
        """Тестовый чек (игнорирует hardware.printer.enabled)."""
        probe = self.probe()
        if not probe.ok:
            return probe
        ok, detail = self._print_text_with_detail(self._format_test_receipt())
        if ok:
            return PrinterProbeResult(ok=True, message="Тестовый чек отправлен на принтер.")
        return PrinterProbeResult(ok=False, message=detail, open_ports=probe.open_ports)

    def probe(self) -> PrinterProbeResult:
        if self._uses_usb():
            return self._probe_usb()
        return self._probe_ethernet()

    def print_order_slip(self, lines: list[CartLine], total: float, order_id: str) -> bool:
        if not self._cfg.enabled:
            return True
        ok, _ = self._print_text_with_detail(self._format_slip(lines, total, order_id))
        return ok

    def _uses_usb(self) -> bool:
        return (self._cfg.connection or "").strip().lower() == "usb"

    def _probe_usb(self) -> PrinterProbeResult:
        if sys.platform != "win32":
            return PrinterProbeResult(
                ok=False,
                message="USB-печать поддерживается только на Windows",
            )
        if not win_print.is_windows_spooler_available():
            return PrinterProbeResult(ok=False, message="Служба печати Windows недоступна")
        try:
            name = win_print.resolve_printer_name(self._cfg.windows_name)
            win_print.probe_printer(name)
            return PrinterProbeResult(ok=True, message=f"Принтер Windows: {name}")
        except OSError as exc:
            return PrinterProbeResult(ok=False, message=str(exc))

    def _probe_ethernet(self) -> PrinterProbeResult:
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

    def _print_text_with_detail(self, text: str) -> tuple[bool, str]:
        try:
            payload = self._build_payload(text)
            if self._uses_usb():
                self._send_usb(payload)
                target = self._usb_target_label()
            else:
                self._send_ethernet(payload)
                target = f"{self._cfg.host}:{self._cfg.port}"
            logger.info("HS-K33: напечатано на %s (%d символов)", target, len(text))
            return True, ""
        except OSError as exc:
            target = self._usb_target_label() if self._uses_usb() else f"{self._cfg.host}:{self._cfg.port}"
            msg = str(exc).strip() or _format_os_error(exc, target)
            logger.error("HS-K33: ошибка печати %s: %s", target, msg)
            return False, msg

    def _build_payload(self, text: str) -> bytes:
        if self._uses_usb():
            # USB + Generic/Text Only: только байты CP866, без ESC/POS —
            # иначе драйвер печатает управляющие коды как «кракозябры».
            return self._usb_plain_payload(text)
        return self._escpos_payload(text)

    def _usb_plain_payload(self, text: str) -> bytes:
        body = text.encode("cp866", errors="replace")
        return body + b"\n\n\n\n"

    def _escpos_payload(self, text: str) -> bytes:
        body = text.encode("cp866", errors="replace")
        return _INIT + _CP866_TABLE + body + _CUT

    def _usb_target_label(self) -> str:
        try:
            return win_print.resolve_printer_name(self._cfg.windows_name)
        except OSError:
            return self._cfg.windows_name or "Windows default"

    def _send_usb(self, payload: bytes) -> None:
        name = win_print.resolve_printer_name(self._cfg.windows_name)
        datatype = (self._cfg.windows_datatype or "RAW").strip().upper() or "RAW"
        win_print.print_bytes(name, payload, datatype=datatype)

    def _send_ethernet(self, payload: bytes) -> None:
        with self._connect() as sock:
            sock.sendall(payload)

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
        if self._uses_usb():
            try:
                target = win_print.resolve_printer_name(self._cfg.windows_name)
            except OSError:
                target = self._cfg.windows_name or "по умолчанию"
            conn_line = f"Принтер Windows: {target}"
        else:
            conn_line = f"Адрес: {self._cfg.host}:{self._cfg.port}"
        rows = [
            "=== ТЕСТОВЫЙ ЧЕК ===",
            "",
            "Сады Коломны",
            "Киоск самообслуживания",
            "",
            "Принтер: HS-K33",
            conn_line,
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
