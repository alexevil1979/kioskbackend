"""Toast «Добавлено в корзину» (.toast в design-system)."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QWidget

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, GREEN, KolomnaMetrics, scale

_SHADOW = QColor(20, 56, 33, 102)


class KolomnaAddedToast(QWidget):
    """Зелёная pill-плашка над кнопкой корзины (референс .toast)."""

    BOTTOM_REF = 210

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        w = metrics.width
        self._text = ""
        self._pad_v = scale(24, w)
        self._pad_h = scale(46, w)
        self._shadow_bleed = scale(24, w)
        self._pill_rect = QRectF()
        self._opacity = 1.0
        self._slide_y = 0.0
        self._anim_ms = 0

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick_in)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def _pill_font(self) -> QFont:
        return kolomna_font(self._m.fs_lead, QFont.Weight.ExtraBold)

    def _measure(self) -> None:
        fm = QFontMetrics(self._pill_font())
        tw = fm.horizontalAdvance(self._text)
        th = fm.height()
        pill_w = tw + self._pad_h * 2
        pill_h = th + self._pad_v * 2
        total_w = pill_w
        pill_x = 0
        total_h = pill_h + self._shadow_bleed
        self._pill_rect = QRectF(pill_x, 0, pill_w, pill_h)
        self.setFixedSize(total_w, total_h)

    def _position(self, *, above: QWidget | None = None) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        gap = scale(28, self._m.width)
        if above is not None and above.isVisible():
            anchor_top = above.mapTo(parent, above.rect().topLeft()).y()
            pill_bottom = anchor_top - gap
        else:
            pill_bottom = parent.height() - scale(self.BOTTOM_REF, self._m.width)
        y = pill_bottom - int(self._pill_rect.bottom())
        x = (parent.width() - self.width()) // 2
        self.setGeometry(x, max(0, y), self.width(), self.height())

    def flash(
        self,
        text: str,
        *,
        bump_btn: QWidget | None = None,
        above: QWidget | None = None,
    ) -> None:
        self._text = text
        self._measure()
        self._position(above=above)
        self._opacity = 0.0
        self._slide_y = float(scale(22, self._m.width))
        self._anim_ms = 0
        self.show()
        self.raise_()
        self._anim_timer.start(16)
        self._hide_timer.start(1600)
        if bump_btn is not None and hasattr(bump_btn, "bump"):
            bump_btn.bump()

    def _tick_in(self) -> None:
        self._anim_ms += 16
        t = min(1.0, self._anim_ms / 250.0)
        ease = t * t * (3.0 - 2.0 * t)
        self._opacity = ease
        self._slide_y = float(scale(22, self._m.width)) * (1.0 - ease)
        self.update()
        if t >= 1.0:
            self._anim_timer.stop()

    def paintEvent(self, event) -> None:  # noqa: N802
        if not self._text:
            return
        p = QPainter(self)
        p.setOpacity(self._opacity)
        p.translate(0, self._slide_y)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self._pill_rect
        radius = rect.height() / 2.0
        vw = self._m.width

        shadow_y = rect.bottom() + scale(8, vw)
        shadow_rect = QRectF(
            rect.left() + scale(8, vw),
            shadow_y,
            rect.width() - scale(16, vw),
            scale(28, vw),
        )
        p.setPen(Qt.PenStyle.NoPen)
        for i, alpha in ((0, 28), (1, 20), (2, 12)):
            spread = scale(6 + i * 4, vw)
            sr = shadow_rect.adjusted(-spread, -spread / 2, spread, spread)
            p.setBrush(QColor(_SHADOW.red(), _SHADOW.green(), _SHADOW.blue(), alpha))
            p.drawEllipse(sr)

        p.setBrush(QColor(GREEN))
        p.drawRoundedRect(rect, radius, radius)

        p.setPen(QColor(CREAM))
        p.setFont(self._pill_font())
        p.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), self._text)
