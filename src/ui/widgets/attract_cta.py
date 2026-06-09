from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QLineF, QPropertyAnimation, Qt, QRectF, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QVBoxLayout, QWidget

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, GREEN, scale


def _fit_cta_font(text: str, viewport_width: int, fs: int, pad_h: int, border: int) -> tuple[int, int, QFont]:
    """Уместить одну строку в attract__inner (padding 90px с боков)."""
    max_w = viewport_width - scale(90, viewport_width) * 2
    font = kolomna_font(fs, QFont.Weight.Black)
    min_fs = scale(34, viewport_width)
    min_pad = scale(20, viewport_width)
    fm = QFontMetrics(font)
    while fm.horizontalAdvance(text) + pad_h * 2 + border > max_w:
        if pad_h > min_pad:
            pad_h -= 1
        elif fs > min_fs:
            fs -= 1
            font = kolomna_font(fs, QFont.Weight.Black)
        else:
            break
        fm = QFontMetrics(font)
    return fs, pad_h, font


class _AttractCtaPaint(QWidget):
    """
    attract__cta: одна строка, широкая pill, border 9px, shadow-card.
    ctaPulse 2.2s ease-in-out.
    """

    def __init__(self, text: str, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        self._text = text
        self._vw = viewport_width
        fs = scale(46, viewport_width)
        self._pad_v = scale(40, viewport_width)
        pad_h = scale(78, viewport_width)
        self._border = max(2, scale(9, viewport_width))
        self._pulse_scale = 1.0
        self._pulse_max = 1.045

        self._fs, self._pad_h, self._font = _fit_cta_font(
            text, viewport_width, fs, pad_h, self._border
        )
        fm = QFontMetrics(self._font)
        inner_w = fm.horizontalAdvance(text) + self._pad_h * 2
        inner_h = fm.height() + self._pad_v * 2
        pill_w = inner_w + self._border
        pill_h = inner_h + self._border
        # Запас под ctaPulse scale(1.045) — иначе pill обрезается по бокам
        self._pulse_pad = math.ceil(max(pill_w, pill_h) * (self._pulse_max - 1) / 2) + self._border
        self._inner = QRectF(
            self._pulse_pad + self._border / 2,
            self._pulse_pad + self._border / 2,
            pill_w,
            pill_h,
        )
        self.setFixedSize(
            int(pill_w + 2 * self._pulse_pad),
            int(pill_h + 2 * self._pulse_pad),
        )

        self._pulse_anim = QPropertyAnimation(self, b"pulseScale", self)
        self._pulse_anim.setDuration(2200)
        self._pulse_anim.setStartValue(1.0)
        self._pulse_anim.setKeyValueAt(0.5, 1.045)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(-1)

    @pyqtProperty(float)
    def pulseScale(self) -> float:
        return self._pulse_scale

    @pulseScale.setter
    def pulseScale(self, value: float) -> None:
        self._pulse_scale = value
        self.update()

    def start_animation(self) -> None:
        if self._pulse_anim.state() != QPropertyAnimation.State.Running:
            self._pulse_anim.start()

    def stop_animation(self) -> None:
        self._pulse_anim.stop()
        self.pulseScale = 1.0

    def set_text(self, text: str) -> None:
        self._text = text
        fs = scale(46, self._vw)
        pad_h = scale(78, self._vw)
        self._fs, self._pad_h, self._font = _fit_cta_font(
            text, self._vw, fs, pad_h, self._border
        )
        fm = QFontMetrics(self._font)
        inner_w = fm.horizontalAdvance(text) + self._pad_h * 2
        inner_h = fm.height() + self._pad_v * 2
        pill_w = inner_w + self._border
        pill_h = inner_h + self._border
        self._pulse_pad = math.ceil(max(pill_w, pill_h) * (self._pulse_max - 1) / 2) + self._border
        self._inner = QRectF(
            self._pulse_pad + self._border / 2,
            self._pulse_pad + self._border / 2,
            pill_w,
            pill_h,
        )
        self.setFixedSize(
            int(pill_w + 2 * self._pulse_pad),
            int(pill_h + 2 * self._pulse_pad),
        )
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        painter.translate(cx, cy)
        painter.scale(self._pulse_scale, self._pulse_scale)
        painter.translate(-cx, -cy)

        rect = QRectF(self._inner)
        radius = rect.height() / 2
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        inset = self._border * 0.55
        fill_rect = rect.adjusted(inset, inset, -inset, -inset)
        fill_path = QPainterPath()
        fill_path.addRoundedRect(fill_rect, max(1, radius - inset), max(1, radius - inset))
        painter.fillPath(fill_path, QColor(GREEN))

        pen = QPen(QColor("#FFFFFF"))
        pen.setWidth(self._border)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        painter.setPen(QColor(CREAM))
        painter.setFont(self._font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._text)


class _AttractHand(QWidget):
    """attract__hand — тонкая ↑ ~60px, handBob 1.6s (как в референсе)."""

    def __init__(self, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        self._vw = viewport_width
        self._arrow_h = scale(60, viewport_width)
        self._stroke = max(2, scale(4, viewport_width))
        self._bob_offset = 0.0
        bob_px = scale(16, viewport_width)
        self.setFixedSize(scale(32, viewport_width), self._arrow_h + bob_px)
        self._bob_anim = QPropertyAnimation(self, b"bobOffset", self)
        self._bob_anim.setDuration(1600)
        self._bob_anim.setStartValue(0.0)
        self._bob_anim.setKeyValueAt(0.5, -float(bob_px))
        self._bob_anim.setEndValue(0.0)
        self._bob_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._bob_anim.setLoopCount(-1)

    @pyqtProperty(float)
    def bobOffset(self) -> float:
        return self._bob_offset

    @bobOffset.setter
    def bobOffset(self, value: float) -> None:
        self._bob_offset = value
        self.update()

    def start_animation(self) -> None:
        if self._bob_anim.state() != QPropertyAnimation.State.Running:
            self._bob_anim.start()

    def stop_animation(self) -> None:
        self._bob_anim.stop()
        self.bobOffset = 0.0

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        vw = self._vw
        cx = self.width() / 2.0
        top = self._bob_offset + scale(2, vw)
        bottom = top + self._arrow_h - scale(4, vw)
        head_h = scale(18, vw)
        head_w = scale(11, vw)
        stem_top = top + head_h
        stem_len = (bottom - stem_top) * 0.8
        stem_bottom = stem_top + stem_len

        pen = QPen(QColor(GREEN))
        pen.setWidth(self._stroke)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(QLineF(cx, top, cx - head_w, stem_top))
        painter.drawLine(QLineF(cx, top, cx + head_w, stem_top))
        painter.drawLine(QLineF(cx, stem_top, cx, stem_bottom))


class AttractCtaBlock(QWidget):
    """attract__cta-wrap: gap 22px между CTA и стрелкой."""

    def __init__(self, text: str, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        gap = scale(22, viewport_width)
        shadow_room = scale(28, viewport_width)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(shadow_room, scale(8, viewport_width), shadow_room, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._cta = _AttractCtaPaint(text, viewport_width)
        shadow = QGraphicsDropShadowEffect(self._cta)
        shadow.setBlurRadius(scale(60, viewport_width))
        shadow.setOffset(0, scale(24, viewport_width))
        shadow.setColor(QColor(20, 56, 33, 102))
        self._cta.setGraphicsEffect(shadow)
        lay.addWidget(self._cta, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(gap + scale(30, viewport_width))

        self._hand = _AttractHand(viewport_width)
        lay.addWidget(self._hand, alignment=Qt.AlignmentFlag.AlignHCenter)

    def start_animations(self) -> None:
        self._cta.start_animation()
        self._hand.start_animation()

    def stop_animations(self) -> None:
        self._cta.stop_animation()
        self._hand.stop_animation()

    def set_text(self, text: str) -> None:
        self._cta.set_text(text)


AttractCtaHost = AttractCtaBlock
