from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QRectF, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QImage, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.config import ROOT
from src.ui.image_utils import load_pixmap, scale_pixmap
from src.ui.kolomna_tokens import CREAM, STRAWBERRY, STRAWBERRY_EDGE, scale


class AttractLogo(QWidget):
    """
    attract__logo: клубничный логотип на кремовом фоне (CSS mask, без капли).
    aspect-ratio 700/425, max-width 84%.
    """

    def __init__(self, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        logo_w = min(scale(760, viewport_width), int(viewport_width * 0.84))
        logo_h = max(1, round(logo_w * 425 / 700))
        self.setFixedSize(logo_w, logo_h)

        logo_path = ROOT / "assets" / "kolomna" / "logo.webp"
        pix = load_pixmap(logo_path) if logo_path.is_file() else QPixmap()
        if pix.isNull():
            return

        scaled = scale_pixmap(pix, logo_w, logo_h)
        tinted = QPixmap(scaled.size())
        tinted.fill(Qt.GlobalColor.transparent)
        painter = QPainter(tinted)
        painter.fillRect(tinted.rect(), QColor(STRAWBERRY))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        label = QLabel()
        label.setPixmap(tinted)
        label.setStyleSheet("background: transparent;")
        lay.addWidget(label)


def _css_rounded_rect_path(
    rect: QRectF,
    rx: tuple[float, float, float, float],
    ry: tuple[float, float, float, float],
) -> QPainterPath:
    """CSS border-radius: TL TR BR BL / TL TR BR BL (абсолютные rx, ry)."""
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    rxtl, rxtr, rxbr, rxbl = rx
    rytl, rytr, rybr, rybl = ry

    f = 1.0
    if rxtl + rxtr > 0:
        f = min(f, w / (rxtl + rxtr))
    if rxbl + rxbr > 0:
        f = min(f, w / (rxbl + rxbr))
    if rytl + rybl > 0:
        f = min(f, h / (rytl + rybl))
    if rytr + rybr > 0:
        f = min(f, h / (rytr + rybr))

    rxtl, rxtr, rxbr, rxbl = (v * f for v in (rxtl, rxtr, rxbr, rxbl))
    rytl, rytr, rybr, rybl = (v * f for v in (rytl, rytr, rybr, rybl))

    path = QPainterPath()
    path.moveTo(x + rxtl, y)
    path.lineTo(x + w - rxtr, y)
    if rxtr or rytr:
        path.arcTo(QRectF(x + w - 2 * rxtr, y, 2 * rxtr, 2 * rytr), 90, -90)
    path.lineTo(x + w, y + h - rybr)
    if rxbr or rybr:
        path.arcTo(QRectF(x + w - 2 * rxbr, y + h - 2 * rybr, 2 * rxbr, 2 * rybr), 0, -90)
    path.lineTo(x + rxbl, y + h)
    if rxbl or rybl:
        path.arcTo(QRectF(x, y + h - 2 * rybl, 2 * rxbl, 2 * rybl), 270, -90)
    path.lineTo(x, y + rytl)
    if rxtl or rytl:
        path.arcTo(QRectF(x, y, 2 * rxtl, 2 * rytl), 180, -90)
    path.closeSubpath()
    return path


def _logo_drop_path(rect: QRectF) -> QPainterPath:
    """drop-fill: border-radius 46% 54% 48% 52% / 6% 6% 96% 94%."""
    w, h = rect.width(), rect.height()
    return _css_rounded_rect_path(
        rect,
        (0.46 * w, 0.54 * w, 0.48 * w, 0.52 * w),
        (0.06 * h, 0.06 * h, 0.96 * h, 0.94 * h),
    )


def _tint_logo_cream(pix: QPixmap, cream: str) -> QPixmap:
    """CSS filter на logo.webp → кремовый цвет на капле."""
    out = QPixmap(pix.size())
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.fillRect(out.rect(), QColor(cream))
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    painter.drawPixmap(0, 0, pix)
    painter.end()
    return out


def _logo_mask_paths() -> tuple[Path, ...]:
    root = ROOT / "assets" / "kolomna"
    return (
        root / "logo_mask.png",
        root / "_raw_7cf0b883-ce6d-4b58-ae06-f25604148458",
        root / "logo.webp",
    )


def _cream_logo_from_mask(max_w: int, max_h: int) -> QPixmap:
    """Логотип на капле: маска из референса (крем на чёрном → прозрачный фон)."""
    for path in _logo_mask_paths():
        if not path.is_file():
            continue
        pix = load_pixmap(path)
        if pix.isNull():
            continue
        if path.suffix.lower() == ".webp":
            return _tint_logo_cream(_fit_logo_pixmap(pix, max_w, max_h), CREAM)
        img = pix.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        scaled = img.scaled(
            max_w,
            max_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        for y in range(scaled.height()):
            for x in range(scaled.width()):
                c = scaled.pixelColor(x, y)
                if c.red() < 40 and c.green() < 40 and c.blue() < 40:
                    c.setAlpha(0)
                else:
                    c.setAlpha(255)
                scaled.setPixelColor(x, y, c)
        return QPixmap.fromImage(scaled)
    return QPixmap()


def _fit_logo_pixmap(pix: QPixmap, max_w: int, max_h: int) -> QPixmap:
    if pix.isNull() or max_w <= 0 or max_h <= 0:
        return QPixmap()
    w, h = pix.width(), pix.height()
    if w <= 0 or h <= 0:
        return QPixmap()
    scale_f = min(max_w / w, max_h / h)
    tw = max(1, int(w * scale_f))
    th = max(1, int(h * scale_f))
    return scale_pixmap(pix, tw, th)


_ADMIN_TAP_COUNT = 4
_ADMIN_TAP_WINDOW_MS = 2500


class LogoDrop(QWidget):
    """logo-drop / BerryDrop: капля + логотип (catalog__bar, cart-empty)."""

    admin_requested = pyqtSignal()

    def __init__(
        self,
        width: int,
        height: int | None = None,
        *,
        fill: str | None = None,
        edge: str | None = None,
        logo_tint: str | None = None,
        opacity: float = 1.0,
        admin_taps: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._vw = width
        self._fill = fill or STRAWBERRY
        self._edge = edge or STRAWBERRY_EDGE
        self._logo_tint = logo_tint or CREAM
        self._opacity = max(0.0, min(1.0, opacity))
        self._admin_taps_enabled = admin_taps
        self._tap_count = 0
        self._tap_reset = QTimer(self)
        self._tap_reset.setSingleShot(True)
        self._tap_reset.timeout.connect(self._reset_admin_taps)
        if admin_taps:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        h = height if height is not None else max(1, round(width * 158 / 340))
        self.setFixedSize(width, h)

        pad_top = scale(6, width)
        avail_h = max(1, h - pad_top - scale(30, width))
        logo_inset = 0.86
        max_w = max(1, int(width * logo_inset))
        max_h = max(1, int(avail_h * logo_inset))

        self._pad_top = pad_top
        self._logo = QPixmap()
        self._ref_pixmap = QPixmap()
        logo_path = ROOT / "assets" / "kolomna" / "logo.webp"
        if logo_path.is_file():
            pix = load_pixmap(logo_path)
            if not pix.isNull():
                self._logo = _tint_logo_cream(
                    _fit_logo_pixmap(pix, max_w, max_h), self._logo_tint
                )
        if self._logo.isNull():
            self._logo = _cream_logo_from_mask(max_w, max_h)

    def _reset_admin_taps(self) -> None:
        self._tap_count = 0

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if (
            self._admin_taps_enabled
            and event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):
            self._tap_count += 1
            self._tap_reset.start(_ADMIN_TAP_WINDOW_MS)
            if self._tap_count >= _ADMIN_TAP_COUNT:
                self._reset_admin_taps()
                self._tap_reset.stop()
                self.admin_requested.emit()
        super().mouseReleaseEvent(event)

    def set_ref_pixmap(self, pix: QPixmap) -> None:
        """Растр из ref-скриншота (pixel-compare / grab)."""
        self._ref_pixmap = pix
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._opacity < 1.0:
            painter.setOpacity(self._opacity)

        if not self._ref_pixmap.isNull():
            scaled = self._ref_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(0, 0, scaled)
            painter.end()
            return

        rect = QRectF(0, 0, self.width(), self.height())
        path = _logo_drop_path(rect)
        painter.fillPath(path, QColor(self._fill))
        edge_h = scale(6, self._vw)
        edge_rect = QRectF(0, self.height() - edge_h, self.width(), edge_h + 1)
        edge_path = QPainterPath()
        edge_path.addRect(edge_rect)
        painter.fillPath(path.intersected(edge_path), QColor(self._edge))

        if not self._logo.isNull():
            lx = (self.width() - self._logo.width()) // 2
            avail_h = self.height() - self._pad_top - scale(30, self._vw)
            ly = self._pad_top + max(0, (avail_h - self._logo.height()) // 2)
            painter.save()
            painter.setClipPath(path)
            painter.drawPixmap(lx, ly, self._logo)
            painter.restore()
        painter.end()


BerryDropLogo = LogoDrop


def BerryDrop(
    width: int,
    height: int | None = None,
    *,
    fill: str = STRAWBERRY,
    edge: str = STRAWBERRY_EDGE,
    logo_tint: str = CREAM,
    opacity: float = 1.0,
    parent=None,
) -> LogoDrop:
    """BerryDrop из референса — капля с настраиваемой заливкой."""
    return LogoDrop(
        width,
        height,
        fill=fill,
        edge=edge,
        logo_tint=logo_tint,
        opacity=opacity,
        parent=parent,
    )
