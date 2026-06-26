from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.ui import kolomna_strings as S
from src.ui.kolomna_chrome import chrome_pill_height, chrome_row_height
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_shadow import draw_shadow_soft_pill, shadow_soft_bleed
from src.ui.kolomna_tokens import CREAM, GREEN, INK_60, KolomnaMetrics, scale

_HOLD_MS = 1200
_INFO_OFFLINE = "#B0B0B0"


class _InfoIcon(QWidget):
    """catalog__info-ic: круг + «i» — зелёный при доступном API, серый без связи."""

    def __init__(self, size: int, font_px: int, parent=None) -> None:
        super().__init__(parent)
        self._font_px = font_px
        self._online = True
        self.setFixedSize(size, size)

    def set_online(self, online: bool) -> None:
        if online == self._online:
            return
        self._online = online
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(GREEN if self._online else _INFO_OFFLINE))
        p.drawEllipse(0, 0, self.width(), self.height())
        font = QFont("Georgia", -1, QFont.Weight.Black)
        font.setPixelSize(self._font_px)
        font.setItalic(True)
        p.setFont(font)
        p.setPen(QColor(CREAM if self._online else "#FFFFFF"))
        rect = self.rect().adjusted(1, 0, 0, 0)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "i")
        p.end()


class _InfoPill(QWidget):
    def __init__(self, radius: int, parent=None) -> None:
        super().__init__(parent)
        self._radius = radius
        self._pressed = False

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = float(self._radius)
        draw_shadow_soft_pill(p, rect, r, max(1, self.width()))
        bg = QColor(CREAM if self._pressed else "#FFFFFF")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, self._radius, self._radius)
        p.end()


class KolomnaInfoButton(QWidget):
    """catalog__info: короткое нажатие — инфо; удержание 1.2с — админка."""

    clicked = pyqtSignal()
    admin_requested = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._held = False
        self._online = False
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._on_hold)

        self._build_layout()

    def _build_layout(self) -> None:
        m = self._m
        w = m.width
        pad_l = scale(12, w)
        pad_r = scale(30, w)
        gap = scale(16, w)
        ic_sz = scale(56, w)
        fs_ic = scale(32, w)

        self._tx = QLabel(S.INFO)
        self._tx.setFont(kolomna_font(m.fs_body, QFont.Weight.ExtraBold))

        fm = QFontMetrics(self._tx.font())
        pill_w = pad_l + ic_sz + gap + fm.horizontalAdvance(self._tx.text()) + pad_r
        pill_h = chrome_pill_height(w)
        radius = pill_h // 2

        bleed_l, bleed_t, bleed_r, bleed_b = shadow_soft_bleed(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(bleed_l, bleed_t, bleed_r, bleed_b)
        outer.setSpacing(0)

        self._pill = _InfoPill(radius)
        self._pill.setFixedSize(pill_w, pill_h)

        lay = QHBoxLayout(self._pill)
        lay.setContentsMargins(pad_l, 0, pad_r, 0)
        lay.setSpacing(gap)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self._icon = _InfoIcon(ic_sz, fs_ic)
        self._icon.set_online(self._online)
        lay.addWidget(self._icon)
        lay.addWidget(self._tx, alignment=Qt.AlignmentFlag.AlignVCenter)

        outer.addWidget(self._pill)
        self.setFixedSize(pill_w + bleed_l + bleed_r, chrome_row_height(w))
        self._tx.setStyleSheet(
            f"color: {INK_60 if not self._online else GREEN}; background: transparent;"
        )

    def _on_hold(self) -> None:
        self._held = True
        self.admin_requested.emit()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._pill.geometry().contains(
            event.position().toPoint()
        ):
            self._held = False
            self._hold_timer.start(_HOLD_MS)
            self._pill._pressed = True
            self._pill.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._hold_timer.stop()
        self._pill._pressed = False
        self._pill.update()
        if event.button() == Qt.MouseButton.LeftButton and not self._held:
            if self._pill.geometry().contains(event.position().toPoint()):
                self.clicked.emit()
        self._held = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not self._pill.geometry().contains(event.position().toPoint()):
            self._hold_timer.stop()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._hold_timer.stop()
        super().leaveEvent(event)

    def set_api_online(self, online: bool) -> None:
        self._online = online
        self._icon.set_online(online)
        text_color = GREEN if online else INK_60
        self._tx.setStyleSheet(f"color: {text_color}; background: transparent;")

    def retranslate(self) -> None:
        self._tx.setText(S.INFO)
        m = self._m
        w = m.width
        pad_l = scale(12, w)
        pad_r = scale(30, w)
        gap = scale(16, w)
        ic_sz = scale(56, w)
        fm = QFontMetrics(self._tx.font())
        pill_w = pad_l + ic_sz + gap + fm.horizontalAdvance(S.INFO) + pad_r
        pill_h = chrome_pill_height(w)
        self._pill.setFixedSize(pill_w, pill_h)
        bleed_l, bleed_t, bleed_r, bleed_b = shadow_soft_bleed(w)
        self.setFixedSize(pill_w + bleed_l + bleed_r, chrome_row_height(w))
