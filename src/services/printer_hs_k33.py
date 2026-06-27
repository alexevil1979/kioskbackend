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

# HSPOS ESC/POS (hsprinter.com): n=7 CP866, n=6 WCP1251. НЕ Epson n=17/n=46!
# n=17 у HSPOS = WCP1253 Greek → на чеке были Ω, β. ESC R 7 у HSPOS = Spain, не Россия.
_CP866_TABLE = b"\x1b\x74\x07"
_CP1251_TABLE = b"\x1b\x74\x06"
_FEED_LINES = b"\x1b\x64\x05"
# GS V 0 — полная отрезка; GS V 66 n — подача n строк и отрезка (часто надёжнее)
_CUT_FULL = b"\x1dV\x00"
_FEED_AND_CUT = b"\x1dV\x42\x05"
_ESC_POS_TAIL = b"\r\n\r\n" + _FEED_LINES + _FEED_AND_CUT + _CUT_FULL
# Опционально: полный сброс перед выбором таблицы (редко нужен)
_INIT = b"\x1b\x40"
_PROBE_PORTS = (9100, 9101, 9200, 6001, 515)
_CONNECT_TIMEOUT = 8.0
_PROBE_TIMEOUT = 1.5


@dataclass(frozen=True, slots=True)
class PrinterProbeResult:
    ok: bool
    message: str
    open_ports: tuple[int, ...] = ()


class PrinterHsK33Service:
    """Печать нефискальной квитанции: Ethernet RAW TCP или USB (порт / spooler)."""

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
            port = (self._cfg.windows_port or "").strip() or win_print.probe_printer(name)
            mode = "прямой порт" if self._cfg.windows_use_direct_port and port else "spooler"
            port_txt = f", порт {port}" if port else ""
            return PrinterProbeResult(
                ok=True,
                message=f"Принтер Windows: {name} ({mode}{port_txt})",
            )
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
                via = self._send_usb(payload)
                target = via
            else:
                self._send_ethernet(payload)
                target = f"{self._cfg.host}:{self._cfg.port}"
            logger.info(
                "HS-K33: напечатано через %s (%d символов, enc=%s, prefix=%s)",
                target,
                len(text),
                self._encoding_name(),
                payload[:8].hex(),
            )
            return True, ""
        except OSError as exc:
            target = self._usb_target_label() if self._uses_usb() else f"{self._cfg.host}:{self._cfg.port}"
            msg = str(exc).strip() or _format_os_error(exc, target)
            logger.error("HS-K33: ошибка печати %s: %s", target, msg)
            return False, msg

    def _build_payload(self, text: str) -> bytes:
        return self._payload_prefix() + self._encode_body(text) + _ESC_POS_TAIL

    def _normalize_lines(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\n", "\r\n")

    def _encoding_name(self) -> str:
        return (self._cfg.windows_encoding or "cp866").strip().lower().replace("-", "")

    def _codepage_id(self) -> int:
        if self._cfg.windows_codepage_id >= 0:
            return self._cfg.windows_codepage_id
        enc = self._encoding_name()
        if enc in ("cp1251", "1251", "windows1251"):
            return 6
        return 7

    def _codepage_table(self) -> bytes:
        page_id = self._codepage_id()
        if not 0 <= page_id <= 255:
            raise ValueError(f"windows_codepage_id вне диапазона: {page_id}")
        return bytes((0x1B, 0x74, page_id))

    def _encode_body(self, text: str) -> bytes:
        enc = self._encoding_name()
        normalized = self._normalize_lines(text)
        if enc in ("cp866", "866", "dos"):
            return normalized.encode("cp866", errors="replace")
        if enc in ("cp1251", "1251", "windows1251"):
            return normalized.encode("cp1251", errors="replace")
        return normalized.encode(enc, errors="replace")

    def _payload_prefix(self) -> bytes:
        """ESC t n по мануалу HSPOS; без ESC @ и без ESC R."""
        table = self._codepage_table()
        if self._cfg.windows_escpos_codepage:
            return _INIT + table
        return table

    def _escpos_payload(self, text: str) -> bytes:
        """Совместимость со старым именем."""
        return self._build_payload(text)

    def _usb_target_label(self) -> str:
        try:
            return win_print.resolve_printer_name(self._cfg.windows_name)
        except OSError:
            return self._cfg.windows_name or "Windows default"

    def _send_usb(self, payload: bytes) -> str:
        name = win_print.resolve_printer_name(self._cfg.windows_name)
        datatype = (self._cfg.windows_datatype or "RAW").strip().upper() or "RAW"
        return win_print.print_bytes(
            name,
            payload,
            datatype=datatype,
            port_override=self._cfg.windows_port,
            use_direct_port=self._cfg.windows_use_direct_port,
        )

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
                name = win_print.resolve_printer_name(self._cfg.windows_name)
                port = (self._cfg.windows_port or "").strip() or win_print.get_printer_port(name)
                conn_line = f"Принтер: {name}" + (f", порт {port}" if port else "")
            except OSError:
                conn_line = f"Принтер Windows: {self._cfg.windows_name or 'по умолчанию'}"
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
            f"Кодировка: {self._encoding_name()} ESC t {self._codepage_id()}",
            "",
            "Связь: OK",
            f"Дата: {now}",
            "",
            "АБВГДЕ — проверка кириллицы",
            "",
            "Если вы видите этот текст -",
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
