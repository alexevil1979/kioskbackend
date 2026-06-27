"""Печать RAW/TEXT на принтер Windows (USB, spooler)."""
from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

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


def probe_printer(printer_name: str) -> None:
    """Проверка, что очередь принтера доступна."""
    if not is_windows_spooler_available():
        raise OSError("Печать через Windows доступна только на win32")
    hprinter = wintypes.HANDLE()
    if not _winspool.OpenPrinterW(printer_name, ctypes.byref(hprinter), None):
        raise ctypes.WinError()
    _winspool.ClosePrinter(hprinter)


def print_bytes(printer_name: str, data: bytes, *, datatype: str = "TEXT") -> None:
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
