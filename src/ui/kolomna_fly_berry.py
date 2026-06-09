"""Анимация «ягода в корзину» (flyBerryToCart в референсе)."""

from __future__ import annotations

from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPixmap, QTransform
from PyQt6.QtWidgets import QLabel, QWidget

from src.models.product import Product
from src.ui.image_utils import scale_pixmap
from src.ui.kolomna_catalog import hub_berry_pixmap
from src.ui.kolomna_tokens import scale

_DURATION_MS = 620


def fly_pixmap_for_product(product: Product, *, category_index: int = 0) -> QPixmap:
    """Картинка ягоды раздела (pic/berry-*.webp), не фото товара."""
    del product  # референс: c.img категории, не product photo
    return hub_berry_pixmap(category_index)


def _widget_center_in(widget: QWidget, parent: QWidget) -> QPointF:
    center = widget.rect().center()
    mapped = widget.mapTo(parent, center)
    return QPointF(float(mapped.x()), float(mapped.y()))


def _cubic_bezier(t: float, p1: float, p2: float, p3: float, p4: float) -> float:
    u = 1.0 - t
    return (
        u * u * u * p1
        + 3 * u * u * t * p2
        + 3 * u * t * t * p3
        + t * t * t * p4
    )


def _frame(t: float, dx: float, dy: float, lift: float) -> tuple[float, float, float, float, float]:
    if t <= 0.5:
        u = t / 0.5
        tx = dx * 0.5 * u
        ty = (dy * 0.5 - lift) * u
        sc = 1.0 + (0.8 - 1.0) * u
        rot = -12.0 * u
        op = 1.0
    else:
        u = (t - 0.5) / 0.5
        tx = dx * 0.5 + (dx - dx * 0.5) * u
        ty = (dy * 0.5 - lift) + (dy - (dy * 0.5 - lift)) * u
        sc = 0.8 + (0.18 - 0.8) * u
        rot = -12.0 + (8.0 - (-12.0)) * u
        op = 1.0 + (0.35 - 1.0) * u
    return tx, ty, sc, rot, op


def _rotate_pixmap(pix: QPixmap, angle_deg: float) -> QPixmap:
    if pix.isNull() or abs(angle_deg) < 0.01:
        return pix
    transform = QTransform().rotate(angle_deg)
    return pix.transformed(transform, Qt.TransformationMode.SmoothTransformation)


class _FlyingBerry(QLabel):
    def __init__(
        self,
        parent: QWidget,
        base_pix: QPixmap,
        base_size: int,
        start: QPointF,
        end: QPointF,
        viewport_width: int,
        on_finish,
    ) -> None:
        super().__init__(parent)
        self._base = base_pix
        self._base_size = base_size
        self._start = start
        self._end = end
        self._vw = viewport_width
        self._on_finish = on_finish
        self._ms = 0
        self._opacity = 1.0
        self._shown = QPixmap()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent; border: none;")
        self.raise_()
        self.show()

        dx = end.x() - start.x()
        dy = end.y() - start.y()
        self._dx = dx
        self._dy = dy
        self._lift = min(float(scale(260, viewport_width)), abs(dy) * 0.4 + float(scale(120, viewport_width)))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self) -> None:
        self._ms += 16
        t = min(1.0, self._ms / _DURATION_MS)
        eased = _cubic_bezier(t, 0.0, 0.05, 0.6, 1.0)
        tx, ty, sc, rot, op = _frame(eased, self._dx, self._dy, self._lift)
        self._opacity = op
        size = max(8, int(self._base_size * sc))
        scaled = scale_pixmap(self._base, size, size)
        self._shown = _rotate_pixmap(scaled, rot)
        self.setFixedSize(self._shown.size())
        x = int(self._start.x() + tx - self._shown.width() / 2)
        y = int(self._start.y() + ty - self._shown.height() / 2)
        self.move(x, y)
        self.update()
        if t >= 1.0:
            self._timer.stop()
            self.deleteLater()
            if self._on_finish:
                self._on_finish()

    def paintEvent(self, event) -> None:  # noqa: N802
        if not hasattr(self, "_shown") or self._shown.isNull():
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.setOpacity(getattr(self, "_opacity", 1.0))
        p.drawPixmap(0, 0, self._shown)
        p.end()


def fly_berry_to_cart(
    parent: QWidget,
    *,
    start_widget: QWidget | None,
    cart_button: QWidget | None,
    pixmap: QPixmap,
    viewport_width: int,
    on_finish=None,
) -> None:
    """Полёт ягоды от виджета-источника к кнопке корзины."""
    if pixmap.isNull() or parent is None:
        if on_finish:
            on_finish()
        return

    if start_widget is not None and start_widget.isVisible():
        start = _widget_center_in(start_widget, parent)
        src_sz = min(start_widget.width(), start_widget.height())
    else:
        start = QPointF(parent.width() / 2.0, parent.height() * 0.35)
        src_sz = scale(300, viewport_width)

    if cart_button is not None and cart_button.isVisible():
        end = _widget_center_in(cart_button, parent)
    else:
        end = QPointF(parent.width() / 2.0, parent.height() - float(scale(180, viewport_width)))

    lo = scale(200, viewport_width)
    hi = scale(440, viewport_width)
    size = max(lo, min(hi, src_sz))

    _FlyingBerry(parent, pixmap, size, start, end, viewport_width, on_finish)
