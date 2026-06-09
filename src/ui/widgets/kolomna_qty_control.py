from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_shadow import draw_shadow_soft_ellipse
from src.ui.kolomna_tokens import CREAM, GREEN, KolomnaMetrics, scale


class _QtyCircleBtn(QWidget):
    """qty__btn — белый круг + box-shadow: var(--shadow-soft)."""

    clicked = pyqtSignal()

    def __init__(self, label: str, btn_sz: int, font_px: int, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._label = label
        self._m = metrics
        self._font_px = font_px
        self._btn_sz = btn_sz
        self._shadow_pad = scale(28, metrics.width)
        self._pressed = False
        self.setFixedSize(btn_sz, btn_sz + self._shadow_pad)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_enabled(self, enabled: bool) -> None:
        self.setEnabled(enabled)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():
            p.setOpacity(0.4)
        rect = QRectF(0, 0, self._btn_sz, self._btn_sz).adjusted(0.5, 0.5, -0.5, -0.5)
        vw = self._m.width
        if not self._pressed:
            draw_shadow_soft_ellipse(p, rect, vw)
        bg = QColor(CREAM if self._pressed else "#FFFFFF")
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(rect)
        p.setFont(kolomna_font(self._font_px, QFont.Weight.ExtraBold))
        p.setPen(QColor(GREEN))
        text_rect = QRectF(0, 0, self._btn_sz, self._btn_sz)
        p.drawText(text_rect.toRect(), Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
            if self.isEnabled() and self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class _QtyValueBadge(QLabel):
    """qty__val — число по центру (без фона, как в референсе)."""

    def __init__(
        self,
        font_px: int,
        min_w: int,
        btn_h: int,
        parent=None,
    ) -> None:
        super().__init__("1", parent)
        self.setMinimumWidth(min_w)
        self.setFixedHeight(btn_h)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(kolomna_font(font_px, QFont.Weight.Black))
        self.setStyleSheet(f"QLabel {{ background: transparent; color: {GREEN}; }}")


class KolomnaQtyControl(QWidget):
    value_changed = pyqtSignal(int)
    at_min = pyqtSignal()

    def __init__(
        self,
        metrics: KolomnaMetrics,
        *,
        compact: bool = False,
        min_value: int = 1,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._min = max(0, min_value)
        self._value = self._min
        self._m = metrics
        w = metrics.width
        pad = scale(4 if compact else 6, w)
        circle_shadow = scale(28, w)
        btn_sz = scale(64 if compact else 72, w)
        val_min_w = scale(56 if compact else 64, w)
        fs_btn = scale(34 if compact else 40, w)
        fs_val = scale(34, w) if compact else metrics.fs_h3

        lay = QHBoxLayout(self)
        lay.setContentsMargins(pad, pad, pad, pad)
        lay.setSpacing(0)

        self._dec = _QtyCircleBtn("−", btn_sz, fs_btn, metrics)
        self._val = _QtyValueBadge(fs_val, val_min_w, btn_sz)
        self._inc = _QtyCircleBtn("+", btn_sz, fs_btn, metrics)

        self._dec.clicked.connect(self._dec_value)
        self._inc.clicked.connect(self._inc_value)
        btn_block_h = btn_sz + circle_shadow
        # Круги ± и значение — по верхнему краю (тень уходит вниз в отступ pill).
        align = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        lay.addWidget(self._dec, alignment=align)
        lay.addWidget(self._val, alignment=align)
        lay.addWidget(self._inc, alignment=align)

        total_h = btn_block_h + pad * 2
        self.setFixedHeight(total_h)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._radius = (btn_sz + pad * 2) // 2
        self._btn_block_h = btn_block_h
        self._val.setText(str(self._value))
        self._dec.set_enabled(self._value > self._min)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self._btn_block_h)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(CREAM))
        p.drawRoundedRect(rect, self._radius, self._radius)
        p.end()
        super().paintEvent(event)

    def value(self) -> int:
        return self._value

    def set_value(self, value: int) -> None:
        self._value = max(self._min, value)
        self._val.setText(str(self._value))
        self._dec.set_enabled(self._value > self._min)

    def _dec_value(self) -> None:
        if self._value <= self._min:
            if self._min <= 0:
                return
            self.at_min.emit()
            return
        self.set_value(self._value - 1)
        self.value_changed.emit(self._value)

    def _inc_value(self) -> None:
        self.set_value(self._value + 1)
        self.value_changed.emit(self._value)
