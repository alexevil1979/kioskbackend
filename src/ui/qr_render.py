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


def _render_payload(payload: str, size: int) -> QPixmap | None:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image()
    buf = BytesIO()
    img.save(buf, format="PNG")
    qimg = QImage.fromData(buf.getvalue())
    if qimg.isNull():
        return None
    return _scale(QPixmap.fromImage(qimg), size)


def render_qr_pixmap(
    *,
    payload: str = "",
    image_b64: str = "",
    size: int = 268,
) -> QPixmap | None:
    """
    QR для экрана СБП:
    - qr_code_image (base64/png) от API;
    - qr_code_payload как SVG (Katusha);
    - короткий payload (URL / ST00012) — локальная генерация.
    """
    if image_b64:
        try:
            blob = _decode_image_b64(image_b64)
            qimg = QImage.fromData(blob)
            if not qimg.isNull():
                return _scale(QPixmap.fromImage(qimg), size)
        except Exception as exc:
            logger.warning("Не удалось декодировать qr_code_image: %s", exc)

    text = (payload or "").strip()
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
