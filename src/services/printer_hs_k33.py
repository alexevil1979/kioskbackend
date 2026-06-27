from __future__ import annotations

import base64
import io
import logging
import socket
import sys
from dataclasses import dataclass
from datetime import datetime

from PIL import Image

from src.core.cart import CartLine
from src.core.config import HardwarePrinterConfig
from src.models.order import OrderReceiptResult
from src.services import printer_windows_spooler as win_print

logger = logging.getLogger(__name__)

# Документация: docs/hardware/04-hs-k33-printer.md
# HSPOS ESC/POS: n=7 CP866, n=6 WCP1251 (НЕ Epson n=17 = Greek!)

_FEED_LINES = b"\x1b\x64\x05"
_CUT_FULL = b"\x1dV\x00"
_FEED_AND_CUT = b"\x1dV\x42\x05"
_ESC_POS_TAIL = b"\r\n\r\n" + _FEED_LINES + _FEED_AND_CUT + _CUT_FULL
_INIT = b"\x1b\x40"
_ALIGN_CENTER = b"\x1b\x61\x01"
_ALIGN_LEFT = b"\x1b\x61\x00"
_PROBE_PORTS = (9100, 9101, 9200, 6001, 515)
_CONNECT_TIMEOUT = 8.0
_PROBE_TIMEOUT = 1.5


@dataclass(frozen=True, slots=True)
class PrinterProbeResult:
    ok: bool
    message: str
    open_ports: tuple[int, ...] = ()


class PrinterHsK33Service:
    """Печать нефискальной квитанции: Ethernet RAW TCP или USB (spooler / порт)."""

    def __init__(
        self,
        config: HardwarePrinterConfig,
        *,
        bind_ip: str = "",
    ) -> None:
        self._cfg = config
        self._bind_ip = (bind_ip or "").strip()
        self._last_via = ""

    def print_text(self, text: str) -> bool:
        if not self._cfg.enabled or not text.strip():
            return True
        ok, _ = self._print_payload_with_detail(self._build_payload(text), len(text))
        return ok

    def print_receipt(self, text: str, qr_image_data_url: str = "") -> bool:
        """Текст чека из API + QR выдачи (pickup_qr_image)."""
        if not self._cfg.enabled or not text.strip():
            return True
        ok, _ = self._print_payload_with_detail(
            self._build_payload(text, qr_image_data_url),
            len(text),
            qr=bool(qr_image_data_url.strip()),
        )
        return ok

    def print_test_receipt(self) -> PrinterProbeResult:
        """Тестовый чек (игнорирует hardware.printer.enabled)."""
        probe = self.probe()
        if not probe.ok:
            return probe
        text = self._format_test_receipt()
        ok, detail = self._print_payload_with_detail(self._build_payload(text), len(text))
        if ok:
            via = self._last_via
            msg = f"Тестовый чек отправлен ({via})." if via else "Тестовый чек отправлен на принтер."
            return PrinterProbeResult(ok=True, message=msg)
        return PrinterProbeResult(ok=False, message=detail, open_ports=probe.open_ports)

    def print_paid_order_receipt(self, receipt: OrderReceiptResult) -> PrinterProbeResult:
        """Чек оплаченного заказа из API (игнорирует hardware.printer.enabled)."""
        probe = self.probe()
        if not probe.ok:
            return probe
        if not receipt.receipt_text.strip():
            return PrinterProbeResult(ok=False, message="API не вернул receipt_text", open_ports=probe.open_ports)
        ok, detail = self._print_payload_with_detail(
            self._build_payload(receipt.receipt_text, receipt.pickup_qr_image),
            len(receipt.receipt_text),
            qr=bool(receipt.pickup_qr_image.strip()),
        )
        if ok:
            qr_note = " + QR" if receipt.pickup_qr_image.strip() else ""
            via = self._last_via
            msg = (
                f"Чек заказа #{receipt.order_id}{qr_note} отправлен ({via})."
                if via
                else f"Чек заказа #{receipt.order_id}{qr_note} отправлен на принтер."
            )
            return PrinterProbeResult(ok=True, message=msg)
        return PrinterProbeResult(ok=False, message=detail, open_ports=probe.open_ports)

    def probe(self) -> PrinterProbeResult:
        if self._uses_usb():
            return self._probe_usb()
        return self._probe_ethernet()

    def print_order_slip(self, lines: list[CartLine], total: float, order_id: str) -> bool:
        if not self._cfg.enabled:
            return True
        text = self._format_slip(lines, total, order_id)
        ok, _ = self._print_payload_with_detail(self._build_payload(text), len(text))
        return ok

    def _uses_usb(self) -> bool:
        return (self._cfg.connection or "").strip().lower() == "usb"

    def _usb_transport(self) -> str:
        explicit = (self._cfg.windows_usb_transport or "").strip().lower()
        if explicit in ("spooler", "direct", "direct_first"):
            return explicit
        return "direct" if self._cfg.windows_use_direct_port else "spooler"

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
            transport = self._usb_transport()
            port_txt = f", порт {port}" if port else ""
            return PrinterProbeResult(
                ok=True,
                message=f"Принтер: {name} ({transport}{port_txt})",
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

    def _print_payload_with_detail(
        self,
        payload: bytes,
        text_len: int,
        *,
        qr: bool = False,
    ) -> tuple[bool, str]:
        try:
            if self._uses_usb():
                via = self._send_usb(payload)
            else:
                self._send_ethernet(payload)
                via = f"{self._cfg.host}:{self._cfg.port}"
            self._last_via = via
            logger.info(
                "HS-K33: %s, enc=%s, page=%s, prefix=%s, %d симв.%s",
                via,
                self._encoding_name(),
                self._codepage_id(),
                payload[:12].hex(),
                text_len,
                ", QR" if qr else "",
            )
            return True, ""
        except OSError as exc:
            target = self._usb_target_label() if self._uses_usb() else f"{self._cfg.host}:{self._cfg.port}"
            msg = str(exc).strip() or _format_os_error(exc, target)
            logger.error("HS-K33: ошибка печати %s: %s", target, msg)
            return False, msg

    def _build_payload(self, text: str, qr_image_data_url: str = "") -> bytes:
        body = self._payload_prefix() + self._encode_body(text)
        qr_part = self._build_qr_raster_payload(qr_image_data_url)
        if qr_part:
            body += b"\r\n\r\n" + _ALIGN_CENTER + qr_part + _ALIGN_LEFT
        return body + _ESC_POS_TAIL

    def _build_qr_raster_payload(self, data_url: str) -> bytes:
        data_url = (data_url or "").strip()
        if not data_url:
            return b""
        try:
            img = _decode_data_image(data_url)
            return _image_to_escpos_raster(img, self._cfg.qr_raster_width)
        except Exception as exc:
            logger.warning("HS-K33: QR не напечатан: %s", exc)
            return b""

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
        if not self._cfg.windows_escpos_table:
            return b""
        table = self._codepage_table()
        if self._cfg.windows_escpos_codepage:
            return _INIT + table
        return table

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
            transport=self._usb_transport(),
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
            "",
            "Связь: OK",
            f"Дата: {now}",
            "",
            "Спасибо за покупку!",
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


def _decode_data_image(data_url: str) -> Image.Image:
    payload = data_url.split(",", 1)[1] if "," in data_url else data_url
    raw = base64.b64decode(payload, validate=False)
    with Image.open(io.BytesIO(raw)) as img:
        return img.convert("RGBA").copy()


def _image_to_escpos_raster(img: Image.Image, max_width: int) -> bytes:
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    else:
        img = img.convert("RGB")
    img = img.convert("L")
    width, height = img.size
    limit = max_width if max_width > 0 else width
    if width > limit:
        ratio = limit / width
        height = max(1, int(height * ratio))
        width = limit
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    img = img.point(lambda x: 0 if x < 160 else 255, mode="1")
    row_bytes = (img.width + 7) // 8
    if img.width % 8:
        padded = Image.new("1", (row_bytes * 8, img.height), 1)
        padded.paste(img, (0, 0))
        img = padded
    width = img.width
    height = img.height
    pixels = img.load()
    raster = bytearray()
    for y in range(height):
        row = bytearray(row_bytes)
        for x in range(width):
            if pixels[x, y] == 0:
                row[x // 8] |= 0x80 >> (x % 8)
        raster.extend(row)
    xL = row_bytes % 256
    xH = row_bytes // 256
    yL = height % 256
    yH = height // 256
    return bytes((0x1D, 0x76, 0x30, 0x00, xL, xH, yL, yH)) + bytes(raster)
