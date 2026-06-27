"""Печать на принтер Windows: напрямую на USB/COM-порт или через spooler."""
from __future__ import annotations

import ctypes
import logging
import sys
from ctypes import wintypes

logger = logging.getLogger(__name__)

if sys.platform == "win32":
    _winspool = ctypes.WinDLL("winspool.drv")
else:
    _winspool = None


class _DOCINFO1(ctypes.Structure):
    _fields_ = [
        ("pDocName", wintypes.LPWSTR),
        ("pOutputFile", wintypes.LPWSTR),
        ("pDatatype", wintypes.LPWSTR),
    ]


class _PRINTER_INFO_5(ctypes.Structure):
    _fields_ = [
        ("pPrinterName", wintypes.LPWSTR),
        ("pPortName", wintypes.LPWSTR),
        ("Attributes", wintypes.DWORD),
        ("DeviceNotSelectedTimeout", wintypes.DWORD),
        ("TransmissionRetryTimeout", wintypes.DWORD),
    ]


def is_windows_spooler_available() -> bool:
    return sys.platform == "win32" and _winspool is not None


def default_printer_name() -> str | None:
    if not is_windows_spooler_available():
        return None
    size = wintypes.DWORD(0)
    _winspool.GetDefaultPrinterW(None, ctypes.byref(size))
    if size.value <= 0:
        return None
    buf = ctypes.create_unicode_buffer(size.value)
    if not _winspool.GetDefaultPrinterW(buf, ctypes.byref(size)):
        return None
    return buf.value or None


def resolve_printer_name(configured: str) -> str:
    name = (configured or "").strip()
    if name:
        return name
    default = default_printer_name()
    if not default:
        raise OSError("Не задан hardware.printer.windows_name и нет принтера по умолчанию в Windows")
    return default


def get_printer_port(printer_name: str) -> str:
    """Порт из свойств принтера: USB001, COM3 и т.д."""
    if not is_windows_spooler_available():
        raise OSError("Печать через Windows доступна только на win32")
    hprinter = wintypes.HANDLE()
    if not _winspool.OpenPrinterW(printer_name, ctypes.byref(hprinter), None):
        raise ctypes.WinError()
    try:
        needed = wintypes.DWORD(0)
        _winspool.GetPrinterW(hprinter, 5, None, 0, ctypes.byref(needed))
        if needed.value <= 0:
            return ""
        buf = (ctypes.c_byte * needed.value)()
        if not _winspool.GetPrinterW(
            hprinter, 5, ctypes.byref(buf), needed.value, ctypes.byref(needed)
        ):
            raise ctypes.WinError()
        info = _PRINTER_INFO_5.from_buffer(buf)
        return (info.pPortName or "").strip()
    finally:
        _winspool.ClosePrinter(hprinter)


def port_device_path(port_name: str) -> str:
    port = port_name.strip().rstrip(":")
    if not port:
        raise OSError("Пустое имя порта принтера")
    if port.startswith("\\\\"):
        return port
    return f"\\\\.\\{port}"


def write_port_raw(port_name: str, data: bytes) -> None:
    path = port_device_path(port_name)
    with open(path, "wb") as stream:
        stream.write(data)
        stream.flush()


def probe_printer(printer_name: str) -> str:
    """Проверка очереди; возвращает имя порта."""
    if not is_windows_spooler_available():
        raise OSError("Печать через Windows доступна только на win32")
    hprinter = wintypes.HANDLE()
    if not _winspool.OpenPrinterW(printer_name, ctypes.byref(hprinter), None):
        raise ctypes.WinError()
    _winspool.ClosePrinter(hprinter)
    return get_printer_port(printer_name)


def print_bytes_spooler(printer_name: str, data: bytes, *, datatype: str = "RAW") -> None:
    if not is_windows_spooler_available():
        raise OSError("Печать через Windows доступна только на win32")
    hprinter = wintypes.HANDLE()
    if not _winspool.OpenPrinterW(printer_name, ctypes.byref(hprinter), None):
        raise ctypes.WinError()
    try:
        doc = _DOCINFO1("Kiosk receipt", None, datatype)
        if not _winspool.StartDocPrinterW(hprinter, 1, ctypes.byref(doc)):
            raise ctypes.WinError()
        try:
            if not _winspool.StartPagePrinter(hprinter):
                raise ctypes.WinError()
            try:
                written = wintypes.DWORD(0)
                buf = (ctypes.c_char * len(data)).from_buffer_copy(data)
                if not _winspool.WritePrinter(
                    hprinter, buf, len(data), ctypes.byref(written)
                ):
                    raise ctypes.WinError()
            finally:
                _winspool.EndPagePrinter(hprinter)
        finally:
            _winspool.EndDocPrinter(hprinter)
    finally:
        _winspool.ClosePrinter(hprinter)


def print_bytes(
    printer_name: str,
    data: bytes,
    *,
    datatype: str = "RAW",
    port_override: str = "",
    use_direct_port: bool = True,
) -> str:
    """Печать; возвращает способ: direct:USB001 или spooler:RAW."""
    port = (port_override or "").strip() or get_printer_port(printer_name)
    if use_direct_port and port:
        try:
            write_port_raw(port, data)
            logger.info("Печать напрямую на порт %s (%d байт)", port, len(data))
            return f"direct:{port}"
        except OSError as exc:
            logger.warning("Прямая печать на %s не удалась: %s — spooler", port, exc)
    print_bytes_spooler(printer_name, data, datatype=datatype)
    return f"spooler:{datatype}"


# Совместимость со старым вызовом
def print_bytes_legacy(printer_name: str, data: bytes, *, datatype: str = "TEXT") -> None:
    print_bytes_spooler(printer_name, data, datatype=datatype)
