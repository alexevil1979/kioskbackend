from __future__ import annotations

import time

from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen, QStaticText
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.ui import kolomna_strings as S
from src.ui.kolomna_breathe import (
    apply_pill_scale,
    breathe_scale_at,
    button_text_breathes,
    draw_static_text,
    font_for_breathe,
    start_breathe_timer,
)
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import fmt_price
from src.ui.kolomna_cta import cta_palette
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, scale

_BUMP_DURATION_MS = 400


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _cart_bump_scale(t: float) -> float:
    """cartBump .4s — амплитуда ×0.5 от референса (меньше раздвигает кнопку)."""
    if t >= 1.0:
        return 1.0
    if t <= 0.35:
        return 1.0 + 0.045 * _smoothstep(t / 0.35)
    if t <= 0.70:
        return 1.045 - 0.06 * _smoothstep((t - 0.35) / 0.35)
    return 0.985 + 0.015 * _smoothstep((t - 0.70) / 0.30)


def _foot_canvas(metrics: KolomnaMetrics) -> tuple[int, int, int, int]:
    """Единая высота нижних pill-кнопок (тень + отступ под breathe)."""
    w = metrics.width
    edge_pad = scale(20, w)
    shadow_bleed = scale(24, w)
    pill_h = scale(150, w)
    return edge_pad, shadow_bleed, pill_h, pill_h + edge_pad * 2 + shadow_bleed


def _draw_pill_shadows(p: QPainter, rect: QRectF, vw: int) -> None:
    r = rect.height() / 2.0
    for y_off, alpha in (
        (scale(10, vw), 18),
        (scale(14, vw), 30),
        (scale(18, vw), 22),
    ):
        sr = rect.translated(0, y_off)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(20, 56, 33, alpha))
        p.drawRoundedRect(sr, r, r)


class _FootPillBtn(QWidget):
    """screen__footbar .btn — pill (Qt не скругляет QPushButton)."""

    clicked = pyqtSignal()

    def __init__(
        self,
        metrics: KolomnaMetrics,
        *,
        ghost: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics
        self._ghost = ghost
        self._pressed = False
        self._text = ""
        self._st_cache: dict[str, QStaticText] = {}
        w = metrics.width
        self._edge_pad, self._shadow_bleed, self._btn_h, canvas_h = _foot_canvas(metrics)
        self._base_fs = scale(40, w)
        self._min_fs = scale(26, w)
        self._pad_x = scale(28, w)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(canvas_h)

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._st_cache.clear()
        super().resizeEvent(event)

    def _fit_font(self) -> QFont:
        weight = QFont.Weight.ExtraBold if self._ghost else QFont.Weight.Black
        avail = max(20, self.width() - self._pad_x * 2)
        lines = self._text.split("\n")
        fs = self._base_fs
        while fs >= self._min_fs:
            font = kolomna_font(fs, weight)
            fm = QFontMetrics(font)
            if all(fm.horizontalAdvance(line) <= avail for line in lines):
                return font
            fs -= 1
        return kolomna_font(self._min_fs, weight)

    def setText(self, text: str) -> None:  # noqa: N802
        self._text = text
        self._st_cache.clear()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        vw = self._m.width
        pill_h = float(self._btn_h)
        bx = self._edge_pad
        by = self._edge_pad
        rect = QRectF(bx + 1.5, by + 1.5, self.width() - bx * 2 - 3, pill_h - 3)
        r = rect.height() / 2.0

        if self._ghost:
            if self._pressed:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(GREEN))
                p.drawRoundedRect(rect, r, r)
                text_color = QColor(CREAM)
            else:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor("#FFFFFF"))
                p.drawRoundedRect(rect, r, r)
                pen = QPen(QColor(GREEN))
                pen.setWidth(max(2, scale(3, vw)))
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(rect, r, r)
                text_color = QColor(GREEN)
        else:
            pal = cta_palette()
            bg = QColor(pal.bg_active if self._pressed else pal.bg)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(bg)
            p.drawRoundedRect(rect, r, r)
            text_color = QColor(pal.fg)

        font = self._fit_font()
        p.setPen(text_color)
        draw_static_text(
            p,
            font,
            self._text,
            QRectF(bx, by, self.width() - bx * 2, pill_h),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            self._st_cache,
        )
        p.end()

    def refresh_cta(self) -> None:
        self.update()

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
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class PaySumPillBtn(QWidget):
    """screen__footbar .btn--primary: pill, тень, cartBump-анимация."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, label: str, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._pressed = False
        self._label_text = label
        self._sum_text = ""
        self._bump_scale = 1.0
        self._bump_t0 = 0.0
        self._breathe_t0 = time.perf_counter()
        self._breathe_enabled = True
        self._st_cache: dict[str, QStaticText] = {}
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick_anim)
        start_breathe_timer(self._anim_timer)
        w = metrics.width
        self._edge_pad, self._shadow_bleed, self._btn_h, canvas_h = _foot_canvas(metrics)
        self._pad_x = scale(56, w)
        self._fs = scale(50, w)
        self._min_fs = scale(30, w)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(canvas_h)

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._st_cache.clear()
        super().resizeEvent(event)

    def set_sum(self, text: str) -> None:
        self._sum_text = text
        self._st_cache.clear()
        self.update()

    def set_label(self, text: str) -> None:
        self._label_text = text
        self._st_cache.clear()
        self.update()

    def set_breathe(self, enabled: bool) -> None:
        self._breathe_enabled = enabled
        if enabled:
            self._breathe_t0 = time.perf_counter()

    def bump(self) -> None:
        """cartBump .4s ease — как .btn--primary.is-bump в референсе."""
        self._bump_t0 = time.perf_counter()
        self._bump_scale = 1.0

    def _breathe_scale_value(self) -> float:
        if not self._breathe_enabled or self._pressed:
            return 1.0
        return breathe_scale_at(self._breathe_t0)

    def _tick_anim(self) -> None:
        if self._bump_t0 > 0:
            t = (time.perf_counter() - self._bump_t0) * 1000.0 / _BUMP_DURATION_MS
            if t >= 1.0:
                self._bump_t0 = 0.0
                self._bump_scale = 1.0
            else:
                self._bump_scale = _cart_bump_scale(t)
        self.update()

    def _pill_scale(self) -> float:
        breathe = self._breathe_scale_value() if self._bump_t0 <= 0 else 1.0
        return breathe * self._bump_scale

    def _fit_font(self, text: str) -> QFont:
        avail = max(40, self.width() - self._pad_x * 2)
        fs = self._fs
        while fs >= self._min_fs:
            font = kolomna_font(fs, QFont.Weight.Black)
            if QFontMetrics(font).horizontalAdvance(text) <= avail:
                return font
            fs -= 1
        return kolomna_font(self._min_fs, QFont.Weight.Black)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            vw = self._m.width
            pill_h = float(self._btn_h)
            bx = self._edge_pad
            by = self._edge_pad
            cx = self.width() / 2.0
            cy = by + pill_h / 2.0
            rect = QRectF(bx + 1.5, by + 1.5, self.width() - bx * 2 - 3, pill_h - 3)
            r = rect.height() / 2.0
            pill_s = self._pill_scale()
            text_breathes = (
                self._breathe_enabled
                and not self._pressed
                and self._bump_t0 <= 0
                and button_text_breathes()
            )
            _draw_pill_shadows(p, rect, vw)

            scaled = apply_pill_scale(p, cx, cy, pill_s)

            pal = cta_palette()
            bg = QColor(pal.bg_active if self._pressed else pal.bg)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(bg)
            p.drawRoundedRect(rect, r, r)
            if scaled:
                p.restore()

            if text_breathes:
                scaled = apply_pill_scale(p, cx, cy, pill_s)

            font_l = font_for_breathe(self._fit_font(self._label_text), text_breathes)
            pad = self._pad_x
            inner_l = bx + pad
            inner_r = self.width() - bx - pad
            text_rect = QRectF(inner_l, by, max(1.0, inner_r - inner_l), pill_h)
            p.setPen(QColor(pal.fg))
            if self._sum_text:
                font_s = font_for_breathe(self._fit_font(self._sum_text), text_breathes)
                draw_static_text(
                    p, font_l, self._label_text, text_rect,
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    self._st_cache,
                )
                draw_static_text(
                    p, font_s, self._sum_text, text_rect,
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                    self._st_cache,
                )
            else:
                draw_static_text(
                    p, font_l, self._label_text, text_rect,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                    self._st_cache,
                )
            if text_breathes and scaled:
                p.restore()
        finally:
            if p.isActive():
                p.end()

    def refresh_cta(self) -> None:
        self.update()

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
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class KolomnaCartFootBar(QFrame):
    checkout_clicked = pyqtSignal()
    keep_shopping_clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self.setObjectName("KolomnaCartFootBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        border = max(1, scale(2, metrics.width))
        self.setStyleSheet(
            f"QFrame#KolomnaCartFootBar {{ background: {CREAM}; border: none; "
            f"border-top: {border}px solid {CREAM_DEEP}; }}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(metrics.pad, scale(30, metrics.width), metrics.pad, scale(48, metrics.width))
        lay.setSpacing(scale(26, metrics.width))

        self._label = QLabel()
        self._label.setFont(kolomna_font(metrics.fs_lead, QFont.Weight.Bold))
        self._label.setStyleSheet(f"color: {INK_60}; background: transparent; border: none;")
        self._sum = QLabel()
        self._sum.setFont(kolomna_font(metrics.fs_display, QFont.Weight.Black))
        self._sum.setStyleSheet(
            f"color: {GREEN}; background: transparent; border: none; letter-spacing: -1px;"
        )
        lay.addWidget(self._label)
        lay.addWidget(self._sum)

        btns = QHBoxLayout()
        btns.setSpacing(scale(20, metrics.width))
        btns.setContentsMargins(0, 0, 0, scale(24, metrics.width))
        btns.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._ghost = _FootPillBtn(metrics, ghost=True)
        self._ghost.clicked.connect(self.keep_shopping_clicked.emit)
        btns.addWidget(self._ghost, stretch=10)

        self._primary = PaySumPillBtn(metrics, "")
        self._primary.set_breathe(True)
        self._primary.clicked.connect(self.checkout_clicked.emit)
        btns.addWidget(self._primary, stretch=14)

        lay.addLayout(btns)

    def set_labels(self, total_label: str, total_value: float, ghost: str, primary: str) -> None:
        self._label.setText(total_label)
        self._sum.setText(f"{fmt_price(total_value)}\u00a0{S.CUR}")
        self._ghost.setText(ghost)
        self._primary.set_label(primary)
        self._primary.set_sum("")
