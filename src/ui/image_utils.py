from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

logger = logging.getLogger(__name__)


def load_pixmap(path: str | Path) -> QPixmap:
    """
    Загрузка изображения безопасно для путей с кириллицей (Windows + Qt).
    QPixmap(path) и QImage.load(path) часто падают, если в пути есть не-ASCII.
    """
    p = Path(path)
    if not p.is_file():
        return QPixmap()
    try:
        img = QImage.fromData(p.read_bytes())
        if img.isNull():
            logger.warning("Не удалось декодировать: %s", p.name)
            return QPixmap()
        return QPixmap.fromImage(img)
    except OSError as exc:
        logger.warning("Ошибка чтения %s: %s", p, exc)
        return QPixmap()


def scale_pixmap(
    pix: QPixmap,
    max_width: int,
    max_height: int,
) -> QPixmap:
    if pix.isNull() or max_width <= 0 or max_height <= 0:
        return QPixmap()
    return pix.scaled(
        max_width,
        max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def scale_pixmap_cover(pix: QPixmap, width: int, height: int) -> QPixmap:
    """Обрезка по центру без растягивания (object-fit: cover)."""
    if pix.isNull() or width <= 0 or height <= 0:
        return QPixmap()
    scaled = pix.scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = max(0, (scaled.width() - width) // 2)
    y = max(0, (scaled.height() - height) // 2)
    return scaled.copy(x, y, width, height)
