from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import fmt_price
from src.ui.kolomna_cta import cta_palette
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, scale

_BREATHE_CYCLE_MS = 1800
_BREATHE_SCALE = 0.028


def _foot_canvas(metrics: KolomnaMetrics) -> tuple[int, int, int, int]:
    """Единая высота нижних pill-кнопок (тень + отступ под breathe)."""
    w = metrics.width
    edge_pad = scale(20, w)
    shadow_bleed = scale(24, w)
    pill_h = scale(150, w)
    return edge_pad, shadow_bleed, pill_h, pill_h + edge_pad * 2 + shadow_bleed


def _vcenter_baseline(fm: QFontMetrics, top: float, height: float) -> float:
    cy = top + height / 2.0
    return cy + (fm.ascent() - fm.descent()) / 2.0


def _breathe_scale(breathe_ms: int) -> float:
    """btnBreathe 1.8s ease-in-out infinite — scale(1) ↔ scale(1.028)."""
    phase = (breathe_ms % _BREATHE_CYCLE_MS) / _BREATHE_CYCLE_MS
    t = phase * 2.0 if phase <= 0.5 else (1.0 - phase) * 2.0
    ease = t * t * (3.0 - 2.0 * t)
    return 1.0 + _BREATHE_SCALE * ease


def _paint_pill_scale(p: QPainter, cx: float, cy: float, s: float) -> None:
    if abs(s - 1.0) > 0.001:
        p.translate(cx, cy)
        p.scale(s, s)
        p.translate(-cx, -cy)


class _FootPillBtn(QWidget):
    """screen__footbar .btn — pill (Qt не скругляет QPushButton)."""

    clicked = pyqtSignal()

    def __init__(
        self,
        metrics: KolomnaMetrics,
        *,
        ghost: bool = False,
        breathe: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics
        self._ghost = ghost
        self._breathe = breathe and not ghost
        self._pressed = False
        self._text = ""
        self._breathe_ms = 0
        w = metrics.width
        self._edge_pad, self._shadow_bleed, self._btn_h, canvas_h = _foot_canvas(metrics)
        self._base_fs = scale(40, w)
        self._min_fs = scale(26, w)
        self._pad_x = scale(28, w)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(canvas_h)
        if self._breathe:
            self._anim_timer = QTimer(self)
            self._anim_timer.timeout.connect(self._tick_breathe)
            self._anim_timer.start(16)

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
        self.update()

    def _tick_breathe(self) -> None:
        self._breathe_ms += 16
        self.update()

    def _current_scale(self) -> float:
        if not self._breathe or self._pressed:
            return 1.0
        return _breathe_scale(self._breathe_ms)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        vw = self._m.width
        pill_h = float(self._btn_h)
        bx = self._edge_pad
        by = self._edge_pad
        cx = self.width() / 2.0
        cy = by + pill_h / 2.0
        _paint_pill_scale(p, cx, cy, self._current_scale())
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
            if not self._ghost:
                for y_off, alpha in (
                    (scale(10, vw), 18),
                    (scale(14, vw), 30),
                    (scale(18, vw), 22),
                ):
                    sr = rect.translated(0, y_off)
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(QColor(20, 56, 33, alpha))
                    p.drawRoundedRect(sr, r, r)
            pal = cta_palette()
            bg = QColor(pal.bg_active if self._pressed else pal.bg)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(bg)
            p.drawRoundedRect(rect, r, r)
            text_color = QColor(pal.fg)

        font = self._fit_font()
        p.setFont(font)
        p.setPen(text_color)
        p.drawText(
            QRectF(bx, by, self.width() - bx * 2, pill_h),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            self._text,
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
        self._bump_ms = 0
        self._breathe_ms = 0
        self._breathe_enabled = True
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick_anim)
        self._anim_timer.start(16)
        w = metrics.width
        self._edge_pad, self._shadow_bleed, self._btn_h, canvas_h = _foot_canvas(metrics)
        self._pad_x = scale(56, w)
        self._fs = scale(50, w)
        self._min_fs = scale(30, w)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(canvas_h)

    def set_sum(self, text: str) -> None:
        self._sum_text = text
        self.update()

    def set_label(self, text: str) -> None:
        self._label_text = text
        self.update()

    def set_breathe(self, enabled: bool) -> None:
        self._breathe_enabled = enabled
        if not enabled:
            self._breathe_ms = 0

    def bump(self) -> None:
        """cartBump .4s ease — как .btn--primary.is-bump в референсе."""
        self._bump_ms = 0
        self._bump_scale = 1.0

    def _breathe_scale(self) -> float:
        if not self._breathe_enabled or self._pressed:
            return 1.0
        return _breathe_scale(self._breathe_ms)

    def _tick_anim(self) -> None:
        self._breathe_ms += 16
        if self._bump_ms > 0:
            self._bump_ms += 16
            t = self._bump_ms / 400.0
            if t >= 1.0:
                self._bump_ms = 0
                self._bump_scale = 1.0
            elif t <= 0.35:
                self._bump_scale = 1.0 + 0.09 * (t / 0.35)
            elif t <= 0.70:
                self._bump_scale = 1.09 - 0.12 * ((t - 0.35) / 0.35)
            else:
                self._bump_scale = 0.97 + 0.03 * ((t - 0.70) / 0.30)
        self.update()

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
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        vw = self._m.width
        pill_h = float(self._btn_h)
        bx = self._edge_pad
        by = self._edge_pad
        cx = self.width() / 2.0
        cy = by + pill_h / 2.0
        s = (self._breathe_scale() if self._bump_ms <= 0 else 1.0) * self._bump_scale
        if abs(s - 1.0) > 0.001:
            _paint_pill_scale(p, cx, cy, s)

        rect = QRectF(bx + 1.5, by + 1.5, self.width() - bx * 2 - 3, pill_h - 3)
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

        pal = cta_palette()
        bg = QColor(pal.bg_active if self._pressed else pal.bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, r, r)

        font_l = self._fit_font(self._label_text)
        font_s = self._fit_font(self._sum_text)
        pad = self._pad_x
        fm_l = QFontMetrics(font_l)
        fm_s = QFontMetrics(font_s)
        baseline_l = _vcenter_baseline(fm_l, by, pill_h)
        baseline_s = _vcenter_baseline(fm_s, by, pill_h)
        inner_l = bx + pad
        inner_r = self.width() - bx - pad
        p.setPen(QColor(pal.fg))
        p.setFont(font_l)
        p.drawText(int(inner_l), int(baseline_l), self._label_text)
        p.setFont(font_s)
        p.drawText(int(inner_r - fm_s.horizontalAdvance(self._sum_text)), int(baseline_s), self._sum_text)
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

        self._primary = _FootPillBtn(metrics, ghost=False, breathe=True)
        self._primary.clicked.connect(self.checkout_clicked.emit)
        btns.addWidget(self._primary, stretch=14)

        lay.addLayout(btns)

    def set_labels(self, total_label: str, total_value: float, ghost: str, primary: str) -> None:
        self._label.setText(total_label)
        self._sum.setText(f"{fmt_price(total_value)}\u00a0{S.CUR}")
        self._ghost.setText(ghost)
        self._primary.setText(primary)
