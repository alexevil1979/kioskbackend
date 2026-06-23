"""Диагностика QPainter / QBackingStore — лог paint_stack при ошибках Qt."""

from __future__ import annotations

import logging
import threading
import traceback
from pathlib import Path
from time import monotonic
from typing import Any

from PyQt6.QtCore import QEvent, QtMsgType, qInstallMessageHandler
from PyQt6.QtWidgets import QWidget

log = logging.getLogger("kiosk.qt_paint")

_PAINTER_MARKERS = (
    "active painter",
    "QBackingStore::endPaint",
    "QPainter::begin",
    "Paint device returned engine == 0",
)

_tls = threading.local()
_installed = False
_orig_widget_event = None
_dedupe_interval_s = 2.0
_dedupe_state: dict[str, tuple[float, int]] = {}


def _widget_label(widget: QWidget) -> str:
    name = widget.objectName()
    suffix = f" objectName={name!r}" if name else ""
    return f"{widget.__class__.__module__}.{widget.__class__.__name__}{suffix}"


def _paint_stack() -> list[str]:
    stack = getattr(_tls, "paint_stack", None)
    if not stack:
        return []
    return list(stack)


def _traced_widget_event(widget: QWidget, event: QEvent) -> bool:
    if event.type() == QEvent.Type.Paint:
        stack = getattr(_tls, "paint_stack", None)
        if stack is None:
            _tls.paint_stack = []
            stack = _tls.paint_stack

        label = _widget_label(widget)
        stack.append(label)
        try:
            assert _orig_widget_event is not None
            return _orig_widget_event(widget, event)
        except Exception:
            log.exception("Paint event упал в %s", label)
            raise
        finally:
            _tls.last_paint = {"label": label, "stack": list(stack)}
            stack.pop()

    assert _orig_widget_event is not None
    return _orig_widget_event(widget, event)


def _context_line(context: Any) -> str:
    if context is None:
        return "(нет контекста Qt)"
    try:
        return f"{context.file}:{context.line} in {context.function}()"
    except Exception:
        return repr(context)


def _should_log(key: str) -> tuple[bool, int]:
    now = monotonic()
    prev = _dedupe_state.get(key)
    if prev is None:
        _dedupe_state[key] = (now, 1)
        return True, 1
    last_ts, count = prev
    count += 1
    if now - last_ts >= _dedupe_interval_s:
        _dedupe_state[key] = (now, 0)
        return True, count
    _dedupe_state[key] = (last_ts, count)
    return False, count


def _recent_paint_stack() -> str:
    recent = getattr(_tls, "last_paint", None)
    if recent:
        return " → ".join(recent["stack"])
    stack = _paint_stack()
    if stack:
        return " → ".join(stack)
    return "(неизвестно — вне paintEvent)"


def _qt_message_handler(mode: QtMsgType, context: Any, message: str) -> None:
    text = message if isinstance(message, str) else str(message)
    if not any(marker in text for marker in _PAINTER_MARKERS):
        return

    stack_txt = _recent_paint_stack()
    key = f"qt|{text}|{stack_txt}"
    do_log, repeats = _should_log(key)
    if not do_log:
        return

    repeat_note = f" (повторов: {repeats})" if repeats > 1 else ""
    py_trace = "".join(traceback.format_stack(limit=12))

    log.warning(
        "Qt painter%s\n"
        "  message: %s\n"
        "  qt_context: %s\n"
        "  paint_stack: %s\n"
        "  python_stack:\n%s",
        repeat_note,
        text,
        _context_line(context),
        stack_txt,
        py_trace,
    )


def install_qt_paint_trace(*, log_dir: Path | None = None) -> None:
    """Лог `logs/qt_paint.log` + paint_stack при ошибках QPainter (без патча QPainter)."""
    global _installed, _orig_widget_event
    if _installed:
        return
    _installed = True

    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / "qt_paint.log"
        if not any(getattr(h, "baseFilename", "") == str(path) for h in log.handlers):
            fh = logging.FileHandler(path, encoding="utf-8")
            fh.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)-8s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            log.addHandler(fh)
            log.setLevel(logging.WARNING)
            log.propagate = True

    _orig_widget_event = QWidget.event
    QWidget.event = _traced_widget_event  # type: ignore[method-assign, assignment]
    qInstallMessageHandler(_qt_message_handler)

    dest = log_dir / "qt_paint.log" if log_dir else "kiosk.log"
    logging.getLogger("kiosk").info("Qt paint trace → %s", dest)
