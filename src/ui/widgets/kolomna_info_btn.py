from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QWidget

from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, GREEN, KolomnaMetrics, scale

_HOLD_MS = 1200


class _InfoIcon(QWidget):
    """catalog__info-ic: зелёный круг + «i» по центру (Georgia italic)."""

    def __init__(self, size: int, font_px: int, parent=None) -> None:
        super().__init__(parent)
        self._font_px = font_px
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(GREEN))
        p.drawEllipse(0, 0, self.width(), self.height())
        font = QFont("Georgia", -1, QFont.Weight.Black)
        font.setPixelSize(self._font_px)
        font.setItalic(True)
        p.setFont(font)
        p.setPen(QColor(CREAM))
        # небольшой сдвиг вправо — оптическое центрирование курсивной «i»
        rect = self.rect().adjusted(1, 0, 0, 0)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "i")


class KolomnaInfoButton(QWidget):
    """catalog__info: короткое нажатие — инфо; удержание 1.2с — админка."""

    clicked = pyqtSignal()
    admin_requested = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        m = metrics
        self._m = m
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        ic_sz = scale(56, m.width)
        pad_v = scale(12, m.width)
        pad_l = scale(12, m.width)
        pad_r = scale(30, m.width)
        gap = scale(16, m.width)
        fs_ic = scale(32, m.width)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(pad_l, pad_v, pad_r, pad_v)
        lay.setSpacing(gap)

        ic = _InfoIcon(ic_sz, fs_ic)

        self._tx = QLabel(S.INFO)
        self._tx.setFont(kolomna_font(m.fs_body, QFont.Weight.ExtraBold))
        self._tx.setStyleSheet(f"color: {GREEN}; background: transparent;")

        lay.addWidget(ic)
        lay.addWidget(self._tx)

        fm = QFontMetrics(self._tx.font())
        total_w = pad_l + ic_sz + gap + fm.horizontalAdvance(self._tx.text()) + pad_r
        btn_h = max(m.tap_min, ic_sz + pad_v * 2)
        self.setFixedSize(total_w, btn_h)
        self._radius = btn_h // 2
        self._pressed = False

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(scale(28, m.width))
        shadow.setOffset(0, scale(12, m.width))
        shadow.setColor(QColor(20, 56, 33, 102))
        self.setGraphicsEffect(shadow)

        self._held = False
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._on_hold)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        r = float(self._radius)
        bg = QColor(CREAM if self._pressed else "#FFFFFF")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, r, r)
        p.end()
        super().paintEvent(event)

    def _on_hold(self) -> None:
        self._held = True
        self.admin_requested.emit()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._held = False
            self._hold_timer.start(_HOLD_MS)
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._hold_timer.stop()
        self._pressed = False
        self.update()
        if event.button() == Qt.MouseButton.LeftButton and not self._held:
            self.clicked.emit()
        self._held = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not self.rect().contains(event.position().toPoint()):
            self._hold_timer.stop()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._hold_timer.stop()
        super().leaveEvent(event)

    def retranslate(self) -> None:
        self._tx.setText(S.INFO)
        fm = QFontMetrics(self._tx.font())
        m = self._m
        pad_l = scale(12, m.width)
        pad_r = scale(30, m.width)
        ic_sz = scale(56, m.width)
        gap = scale(16, m.width)
        pad_v = scale(12, m.width)
        total_w = pad_l + ic_sz + gap + fm.horizontalAdvance(S.INFO) + pad_r
        btn_h = max(m.tap_min, ic_sz + pad_v * 2)
        self.setFixedSize(total_w, btn_h)
