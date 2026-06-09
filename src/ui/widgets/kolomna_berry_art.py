from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainterPath, QRegion
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QWidget

from src.core.config import ROOT
from src.models.product import Product
from src.ui.image_utils import load_pixmap, scale_pixmap
from src.ui.kolomna_tokens import scale


class KolomnaBerryArt(QWidget):
    """berry-art в prod-row__media: cream-deep фон, фото 150% с тенью."""

    def __init__(
        self,
        product: Product,
        media_w: int,
        media_h: int,
        *,
        radius: int = 0,
        bg: str = "#FFFFFF",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._radius = radius
        self._media_h = media_h
        self.setFixedWidth(media_w)
        self.setMinimumHeight(media_h)
        if radius > 0:
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.setStyleSheet(
                f"background: {bg}; border-radius: {radius}px;"
            )
        else:
            self.setStyleSheet(f"background: {bg};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setStyleSheet("background: transparent;")
        self._img_label = img
        self._product = product
        pix = self._load_pixmap(product)
        if pix and not pix.isNull():
            self._apply_pixmap(pix, media_w)
            shadow = QGraphicsDropShadowEffect(img)
            shadow.setBlurRadius(scale(26, media_w))
            shadow.setOffset(0, scale(18, media_w))
            shadow.setColor(QColor(20, 56, 33, 41))  # drop-shadow .16
            img.setGraphicsEffect(shadow)
        lay.addWidget(img)

    def _apply_pixmap(self, pix, width: int) -> None:
        aw = int(width * 1.5)
        ph = pix.height() * aw / max(1, pix.width())
        self._img_label.setPixmap(scale_pixmap(pix, aw, int(ph)))

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.refresh_image()

    def refresh_image(self) -> None:
        w = self.width()
        if w < 8:
            return
        pix = self._load_pixmap(self._product)
        if pix and not pix.isNull():
            self._apply_pixmap(pix, w)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._radius > 0:
            w, h = self.width(), self.height()
            if w >= 2 and h >= 2:
                path = QPainterPath()
                path.addRoundedRect(QRectF(0, 0, w, h), self._radius, self._radius)
                self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        self.refresh_image()

    def _load_pixmap(self, product: Product):
        if product.image_local:
            p = Path(product.image_local)
            if p.is_file():
                return load_pixmap(p)
        demo = ROOT / "assets" / "demo_products"
        for i in range(1, 13):
            p = demo / f"{i}.jpg"
            if p.is_file():
                return load_pixmap(p)
        return None
