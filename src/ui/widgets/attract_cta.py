from __future__ import annotations

import time

from PyQt6.QtCore import QEasingCurve, QLineF, QPropertyAnimation, Qt, QRectF, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen, QStaticText
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.ui.kolomna_breathe import (
    apply_pill_scale,
    breathe_pad,
    breathe_scale_at,
    button_text_breathes,
    draw_static_text,
    font_for_breathe,
    start_breathe_timer,
)
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_shadow import draw_shadow_soft_pill
from src.ui.kolomna_tokens import CREAM, GREEN, scale

# ---------------------------------------------------------------------------
# Заставка: стрелка ↑ (attract__hand) — подстройка по вертикали (база 1080px).
# Меняйте значения ниже; на экране они масштабируются через scale(..., viewport_width).
# ---------------------------------------------------------------------------
# Y вершины стрелки внутри виджета _AttractHand (до анимации handBob, bobOffset=0).
ATTRACT_HAND_TIP_ORIGIN_Y_PX = 22
# Отступ сверху у блока «кнопка + стрелка» (CSS: .attract__cta-wrap margin-top).
ATTRACT_CTA_WRAP_MARGIN_TOP_PX = 8
# Зазор между кнопкой CTA и стрелкой (CSS: .attract__cta-wrap gap).
ATTRACT_CTA_TO_HAND_GAP_PX = 22
# Доп. зазор под тень кнопки (только PyQt, в HTML нет).
ATTRACT_HAND_EXTRA_GAP_PX = 30
# Амплитуда покачивания handBob вверх-вниз (px при 1080).
ATTRACT_HAND_BOB_PX = 16


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


def _cta_layout(text: str, viewport_width: int, fs: int, pad_v: int, pad_h: int, border: int) -> tuple:
    fs, pad_h, font = _fit_cta_font(text, viewport_width, fs, pad_h, border)
    fm = QFontMetrics(font)
    inner_w = fm.horizontalAdvance(text) + pad_h * 2
    inner_h = fm.height() + pad_v * 2
    pill_w = inner_w + border
    pill_h = inner_h + border
    pulse_pad = breathe_pad(max(pill_w, pill_h)) + border
    inner = QRectF(
        pulse_pad + border / 2,
        pulse_pad + border / 2,
        pill_w,
        pill_h,
    )
    size = (int(pill_w + 2 * pulse_pad), int(pill_h + 2 * pulse_pad))
    return fs, pad_h, font, inner, pulse_pad, size


class _AttractCtaPaint(QWidget):
    """
    attract__cta: одна строка, широкая pill, border 9px, shadow-card.
    btnBreathe — та же синусоида, что у корзины.
    """

    def __init__(self, text: str, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        self._text = text
        self._vw = viewport_width
        self._pad_v = scale(40, viewport_width)
        pad_h = scale(78, viewport_width)
        self._border = max(2, scale(9, viewport_width))
        self._breathe_t0 = time.perf_counter()
        self._st_cache: dict[str, QStaticText] = {}
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self.update)
        start_breathe_timer(self._anim_timer)

        fs = scale(46, viewport_width)
        self._fs, self._pad_h, self._font, self._inner, self._pulse_pad, size = _cta_layout(
            text, viewport_width, fs, self._pad_v, pad_h, self._border
        )
        self.setFixedSize(size[0], size[1])

    def start_animation(self) -> None:
        if not self._anim_timer.isActive():
            self._breathe_t0 = time.perf_counter()
            start_breathe_timer(self._anim_timer)

    def stop_animation(self) -> None:
        self._anim_timer.stop()
        self.update()

    def set_text(self, text: str) -> None:
        self._text = text
        self._st_cache.clear()
        fs = scale(46, self._vw)
        pad_h = scale(78, self._vw)
        self._fs, self._pad_h, self._font, self._inner, self._pulse_pad, size = _cta_layout(
            text, self._vw, fs, self._pad_v, pad_h, self._border
        )
        self.setFixedSize(size[0], size[1])
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self._inner)
        radius = rect.height() / 2
        draw_shadow_soft_pill(painter, rect, radius, self._vw)

        cx, cy = self.width() / 2, self.height() / 2
        pill_s = breathe_scale_at(self._breathe_t0)
        text_breathes = button_text_breathes()
        scaled = apply_pill_scale(painter, cx, cy, pill_s)

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
        if scaled:
            painter.restore()

        if text_breathes:
            scaled = apply_pill_scale(painter, cx, cy, pill_s)

        font = font_for_breathe(self._font, text_breathes)
        painter.setPen(QColor(CREAM))
        draw_static_text(
            painter,
            font,
            self._text,
            rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            self._st_cache,
        )
        if text_breathes and scaled:
            painter.restore()
        painter.end()

    def refresh_cta(self) -> None:
        self.update()


class _AttractHand(QWidget):
    """attract__hand — стрелка ↑, handBob 1.6s."""

    def __init__(self, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        self._vw = viewport_width
        self._arrow_h = scale(60, viewport_width)
        self._stroke = max(2, scale(4, viewport_width))
        self._bob_offset = 0.0
        self._tip_origin_y = scale(ATTRACT_HAND_TIP_ORIGIN_Y_PX, viewport_width)
        bob_px = scale(ATTRACT_HAND_BOB_PX, viewport_width)
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
        top = self._bob_offset + self._tip_origin_y
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
        painter.end()


class AttractCtaBlock(QWidget):
    """attract__cta-wrap: gap 22px между CTA и стрелкой."""

    def __init__(self, text: str, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        shadow_room = scale(28, viewport_width)
        hand_gap = scale(ATTRACT_CTA_TO_HAND_GAP_PX + ATTRACT_HAND_EXTRA_GAP_PX, viewport_width)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            shadow_room,
            scale(ATTRACT_CTA_WRAP_MARGIN_TOP_PX, viewport_width),
            shadow_room,
            0,
        )
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._cta = _AttractCtaPaint(text, viewport_width)
        lay.addWidget(self._cta, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(hand_gap)

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

    def refresh_cta(self) -> None:
        self._cta.refresh_cta()


AttractCtaHost = AttractCtaBlock
