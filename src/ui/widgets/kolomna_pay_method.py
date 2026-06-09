from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, GREEN, INK_30, INK_60, KolomnaMetrics, scale
from src.ui.widgets.kolomna_prod_row import _paint_card_shadow


class _PayMethodRadio(QWidget):
    """pay-method__radio — border 5px ink-30; is-on: green + inset white 9px."""

    _INACTIVE_RING = QColor(31, 77, 42, 56)  # --ink-30

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._active = False
        sz = scale(56, metrics.width)
        self.setFixedSize(sz, sz)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        vw = self._m.width
        border = scale(5, vw)
        inset = scale(9, vw)
        outer = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)

        if self._active:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(GREEN))
            p.drawEllipse(outer)
            inner = outer.adjusted(inset, inset, -inset, -inset)
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(inner)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(outer)
            pen = QPen(self._INACTIVE_RING)
            pen.setWidth(border)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            ring = outer.adjusted(border / 2, border / 2, -border / 2, -border / 2)
            p.drawEllipse(ring)
        p.end()


class KolomnaPayMethod(QWidget):
    selected = pyqtSignal(str)

    def __init__(
        self,
        method_id: str,
        mark: str,
        title: str,
        subtitle: str,
        metrics: KolomnaMetrics,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._method_id = method_id
        self._m = metrics
        self._active = False
        self._pressed = False
        self._radius = metrics.radius
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        card_h = scale(186, metrics.width)
        self._card_h = card_h
        self.setMinimumHeight(card_h + scale(20, metrics.width))

        self._card = QFrame(self)
        self._card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._card.setStyleSheet("QFrame { background: transparent; border: none; }")

        lay = QHBoxLayout(self._card)
        pad_v = scale(38, metrics.width)
        pad_h = scale(40, metrics.width)
        lay.setContentsMargins(pad_h, pad_v, pad_h, pad_v)
        lay.setSpacing(scale(32, metrics.width))

        self._mark = QLabel(mark)
        self._mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mark.setFixedSize(scale(110, metrics.width), scale(110, metrics.width))
        self._mark.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay.addWidget(self._mark)

        text_col = QVBoxLayout()
        text_col.setSpacing(scale(8, metrics.width))
        self._title_lbl = QLabel(title)
        self._title_lbl.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold))
        self._title_lbl.setStyleSheet(f"color: {GREEN}; background: transparent;")
        self._subtitle_lbl = QLabel(subtitle)
        self._subtitle_lbl.setWordWrap(True)
        self._subtitle_lbl.setFont(kolomna_font(metrics.fs_body, QFont.Weight.Medium))
        self._subtitle_lbl.setStyleSheet(f"color: {INK_60}; background: transparent;")
        text_col.addWidget(self._title_lbl)
        text_col.addWidget(self._subtitle_lbl)
        lay.addLayout(text_col, stretch=1)

        self._radio = _PayMethodRadio(metrics)
        lay.addWidget(self._radio, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._apply_style()
        self._sync_geometry()

    def set_text(self, title: str, subtitle: str) -> None:
        self._title_lbl.setText(title)
        self._subtitle_lbl.setText(subtitle)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._radio.set_active(active)
        self._apply_style()
        self.update()

    def _apply_style(self) -> None:
        m = self._m
        mark_bg = GREEN if self._active else CREAM
        mark_fg = CREAM if self._active else GREEN
        self._mark.setFont(kolomna_font(scale(40, m.width), QFont.Weight.Black))
        self._mark.setStyleSheet(
            f"QLabel {{ background: {mark_bg}; color: {mark_fg}; "
            f"border-radius: {scale(24, m.width)}px; }}"
        )

    def _shadow_bleed(self) -> int:
        return scale(20, self._m.width)

    def _sync_geometry(self) -> None:
        w = max(1, self.width())
        self._card.setGeometry(0, 0, w, self._card_h)
        self.setFixedHeight(self._card_h + self._shadow_bleed())

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(1, self.width())
        h = self._card_h
        r = float(self._radius)
        card_rect = QRectF(0, 0, w, h)
        _paint_card_shadow(p, card_rect, r, self._m)
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(card_rect, r, r)
        if self._active:
            pen = QPen(QColor(GREEN))
            pen.setWidth(scale(4, self._m.width))
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(card_rect, r, r)
        p.end()
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_geometry()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._sync_geometry()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.selected.emit(self._method_id)
        super().mouseReleaseEvent(event)
