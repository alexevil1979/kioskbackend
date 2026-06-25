from __future__ import annotations

import base64
import logging
import re
from io import BytesIO

import qrcode
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

logger = logging.getLogger(__name__)

try:
    from PyQt6.QtSvg import QSvgRenderer
except ImportError:  # pragma: no cover
    QSvgRenderer = None  # type: ignore[misc, assignment]


def is_svg_markup(text: str) -> bool:
    head = text.lstrip()[:256].lower()
    return head.startswith("<svg") or "<?xml" in head and "<svg" in head


def _decode_image_b64(data: str) -> bytes:
    raw = data.strip()
    if raw.startswith("data:"):
        raw = raw.split(",", 1)[-1]
    raw = re.sub(r"\s+", "", raw)
    return base64.b64decode(raw)


def _scale(pix: QPixmap, size: int) -> QPixmap:
    return pix.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def _render_svg(svg_text: str, size: int) -> QPixmap | None:
    if QSvgRenderer is None:
        logger.error("PyQt6.QtSvg недоступен — не могу отрисовать SVG QR")
        return None
    renderer = QSvgRenderer(svg_text.encode("utf-8"))
    if not renderer.isValid():
        logger.error("Невалидный SVG QR от API")
        return None
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    from PyQt6.QtGui import QPainter

    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return pix


def _qr_image_to_pixmap(image_data: str, size: int) -> QPixmap | None:
    raw = image_data.strip()
    if not raw:
        return None
    if is_svg_markup(raw):
        return _render_svg(raw, size)
    try:
        blob = _decode_image_b64(raw)
        text = blob.decode("utf-8", errors="ignore")
        if is_svg_markup(text):
            return _render_svg(text, size)
        qimg = QImage.fromData(blob)
        if not qimg.isNull():
            return _scale(QPixmap.fromImage(qimg), size)
    except Exception as exc:
        logger.warning("Не удалось декодировать qr_code_image: %s", exc)
    return None


def _is_nspk_payment_url(text: str) -> bool:
    low = text.lower()
    return "qr.nspk.ru" in low


def _render_payload(payload: str, size: int) -> QPixmap | None:
    from src.ui.kolomna_qr_render import render_kolomna_qr_pixmap, scale_qr_for_display

    pix = render_kolomna_qr_pixmap(payload, px=560, color="#000000", logo="")
    if pix.isNull():
        return None
    return scale_qr_for_display(pix, size)


def render_qr_pixmap(
    *,
    payload: str = "",
    image_b64: str = "",
    size: int = 268,
) -> QPixmap | None:
    """
    QR для экрана СБП:
    - payment_url (qr.nspk.ru) — локальная генерация, как на странице НСПК;
    - qr_code_image (PNG / SVG) от API;
    - qr_code_payload (ST00012 и др.) — локальная генерация.
    """
    text = (payload or "").strip()

    if text and _is_nspk_payment_url(text):
        pix = _render_payload(text, size)
        if pix is not None and not pix.isNull():
            return pix

    if image_b64:
        pix = _qr_image_to_pixmap(image_b64, size)
        if pix is not None and not pix.isNull():
            return pix

    if not text:
        return None

    if is_svg_markup(text):
        return _render_svg(text, size)

    try:
        return _render_payload(text, size)
    except ValueError as exc:
        logger.error(
            "QR payload слишком длинный для локальной генерации (%s символов): %s",
            len(text),
            exc,
        )
        return None
