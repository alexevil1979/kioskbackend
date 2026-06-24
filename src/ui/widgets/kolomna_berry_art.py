from __future__ import annotations

from typing import Literal

from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPixmap, QRegion
from PyQt6.QtWidgets import QSizePolicy, QWidget

from src.models.product import Product
from src.ui.image_utils import load_pixmap, scale_pixmap_cover
from src.ui.product_image_display import product_display_image_path
from src.ui.kolomna_tokens import scale

BerryArtFit = Literal["contain", "cover"]


class KolomnaBerryArt(QWidget):
    """berry-art: рисует фото в paintEvent, overflow:hidden (без QLabel → layout)."""

    def __init__(
        self,
        product: Product,
        media_w: int,
        media_h: int,
        *,
        radius: int = 0,
        bg: str = "#FFFFFF",
        img_scale: float = 1.5,
        fluid_width: bool = False,
        ground_shadow: bool = False,
        fit: BerryArtFit = "contain",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._radius = radius
        self._media_h = media_h
        self._img_scale = img_scale
        self._fluid = fluid_width
        self._ground_shadow = ground_shadow
        self._fit = fit
        self._base_w = max(1, media_w)
        self._bg = bg
        self._product = product
        self._source = self._load_pixmap(product)
        self._cache_key: tuple[int, int, str] | None = None
        self._cache_pm: QPixmap | None = None

        if fluid_width:
            self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, media_h)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.setFixedWidth(self._base_w)
            self.setFixedHeight(media_h)

        if radius > 0:
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.setStyleSheet(f"background: {bg}; border-radius: {radius}px;")
        else:
            self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            self.setStyleSheet(f"background: {bg};")

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(0, self._media_h)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(0, self._media_h)

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return False

    def _draw_w(self) -> int:
        if self._fluid:
            w = self.width()
            return max(1, w if w > 0 else self._base_w)
        return self._base_w

    def _scaled_pixmap(self, draw_w: int, draw_h: int) -> QPixmap | None:
        if self._source is None or self._source.isNull():
            return None
        key = (draw_w, draw_h, self._fit)
        if key == self._cache_key and self._cache_pm is not None and not self._cache_pm.isNull():
            return self._cache_pm

        if self._fit == "cover":
            pm = scale_pixmap_cover(self._source, draw_w, draw_h)
        else:
            aw = max(1, int(draw_w * self._img_scale))
            ph = max(1, int(self._source.height() * aw / max(1, self._source.width())))
            pm = self._source.scaled(
                aw,
                ph,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        self._cache_key = key
        self._cache_pm = pm
        return pm

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.fillRect(self.rect(), QColor(self._bg))

        w, h = max(1, self.width()), max(1, self.height())
        pm = self._scaled_pixmap(w, h)
        if pm is None or pm.isNull():
            p.end()
            return

        if self._fit == "cover":
            p.setClipRect(self.rect())
            p.drawPixmap(0, 0, pm)
            p.end()
            return

        aw, ph = pm.width(), pm.height()
        x = (w - aw) / 2.0
        y = (h - ph) / 2.0
        if self._ground_shadow:
            vw = max(self._base_w, self.width())
            shadow = QRectF(x, y + ph - scale(8, vw), aw, scale(18, vw))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(20, 56, 33, 41))
            p.drawEllipse(shadow)

        p.setClipRect(self.rect())
        p.drawPixmap(int(x), int(y), pm)
        p.end()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._radius > 0:
            w, h = self.width(), self.height()
            if w >= 2 and h >= 2:
                path = QPainterPath()
                path.addRoundedRect(QRectF(0, 0, w, h), self._radius, self._radius)
                self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def refresh_image(self) -> None:
        """Сброс кэша после смены ширины (overlay / каталог)."""
        self._source = self._load_pixmap(self._product)
        self._cache_key = None
        self._cache_pm = None
        self.update()

    def _load_pixmap(self, product: Product) -> QPixmap | None:
        path = product_display_image_path(product)
        if path is not None:
            return load_pixmap(path)
        return None
