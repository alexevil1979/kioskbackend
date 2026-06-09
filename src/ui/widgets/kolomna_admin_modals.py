from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_30, KolomnaMetrics, STRAWBERRY, scale


def _pin_backspace_font(px: int) -> QFont:
    """Глиф ⌫ как в offline-референсе (Segoe UI Symbol / fallback)."""
    for family in ("Segoe UI Symbol", "Segoe UI", "Arial Unicode MS", "Montserrat"):
        if family in QFontDatabase.families():
            font = QFont(family)
            font.setPixelSize(px)
            return font
    return kolomna_font(px, QFont.Weight.ExtraBold)


def _paint_pin_key_shadow(p: QPainter, rect: QRectF, radius: float, vw: int) -> None:
    """box-shadow: var(--shadow-soft) — с запасом по бокам (колонки 1/3 и 3/3)."""
    for y_off, alpha, spread in (
        (scale(10, vw), 18, scale(6, vw)),
        (scale(14, vw), 30, scale(10, vw)),
        (scale(18, vw), 22, scale(14, vw)),
    ):
        sr = rect.adjusted(-spread, 0, spread, 0).translated(0, y_off)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(20, 56, 33, alpha))
        p.drawRoundedRect(sr, radius + spread * 0.25, radius + spread * 0.25)


class _PinKeyBtn(QWidget):
    """pin-key: белая клавиша + shadow-soft (рисуем в paintEvent, без обрезки по краям сетки)."""

    clicked = pyqtSignal()

    def __init__(
        self,
        metrics: KolomnaMetrics,
        label: str,
        *,
        is_back: bool,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics
        self._label = "\u232b" if is_back else label
        self._is_back = is_back
        self._pressed = False
        w = metrics.width
        self._key_h = scale(110, w)
        self._bleed = scale(28, w)
        self._shadow_b = scale(32, w)
        key_fs = scale(42 if is_back else 48, w)
        self._font = _pin_backspace_font(key_fs) if is_back else kolomna_font(key_fs, QFont.Weight.ExtraBold)
        self._radius = float(metrics.radius)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self._key_h + self._shadow_b)
        self.setMinimumWidth(self._bleed * 2 + scale(48, w))

    def _key_rect(self) -> QRectF:
        return QRectF(
            float(self._bleed),
            0.5,
            max(1.0, self.width() - 2 * self._bleed - 1),
            float(self._key_h) - 1,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = self._key_rect()
        r = self._radius
        vw = self._m.width
        if not self._pressed:
            _paint_pin_key_shadow(p, rect, r, vw)
        bg = QColor(CREAM_DEEP if self._pressed else "#FFFFFF")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, r, r)
        p.setFont(self._font)
        p.setPen(QColor(GREEN))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()

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


class _PinCancelBtn(QWidget):
    """btn btn--ghost btn--lg — pill с корректным скруглением."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, text: str, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._text = text
        self._pressed = False
        w = metrics.width
        self._h = scale(104, w)
        self._pad_h = scale(56, w)
        self._border = max(2, scale(3, w))
        self._font = kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold)
        fm = QFontMetrics(self._font)
        self.setFixedSize(fm.horizontalAdvance(text) + self._pad_h * 2, self._h)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        r = rect.height() / 2.0
        if self._pressed:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(GREEN))
            p.drawRoundedRect(rect, r, r)
            fg = QColor(CREAM)
        else:
            pen = QPen(QColor(GREEN))
            pen.setWidth(self._border)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(rect, r, r)
            fg = QColor(GREEN)
        p.setFont(self._font)
        p.setPen(fg)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._text)
        p.end()

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

    def set_text(self, text: str) -> None:
        self._text = text
        fm = QFontMetrics(self._font)
        self.setFixedSize(fm.horizontalAdvance(text) + self._pad_h * 2, self._h)
        self.update()


class KolomnaAdminPinModal(QWidget):
    pin_accepted = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, pin: str, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._pin = pin
        self._val = ""
        self._err = False
        self.setVisible(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(20, 56, 33, 0.6);")

        pad_outer = scale(70, metrics.width)
        avail_w = max(1, metrics.width - 2 * pad_outer)
        box_w = min(scale(680, metrics.width), avail_w)
        pad_w = min(scale(460, metrics.width), box_w - 2 * scale(64, metrics.width))
        pad64 = scale(64, metrics.width)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(pad_outer, pad_outer, pad_outer, pad_outer)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._box = QWidget()
        self._box.setObjectName("KolomnaAdminPinBox")
        self._box.setFixedWidth(box_w)
        self._box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self._box.setStyleSheet(
            f"QWidget#KolomnaAdminPinBox {{ background: {CREAM}; "
            f"border-radius: {metrics.radius_lg}px; }}"
        )
        box_shadow = QGraphicsDropShadowEffect(self._box)
        box_shadow.setBlurRadius(scale(60, metrics.width))
        box_shadow.setOffset(0, scale(24, metrics.width))
        box_shadow.setColor(QColor(20, 56, 33, 102))
        self._box.setGraphicsEffect(box_shadow)

        bl = QVBoxLayout(self._box)
        bl.setContentsMargins(pad64, pad64, pad64, pad64)
        bl.setSpacing(scale(6, metrics.width))
        bl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._eyebrow = QLabel(S.ADMIN_ACCESS.upper())
        self._eyebrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._eyebrow.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        self._eyebrow.setStyleSheet(
            f"color: {GREEN}; background: transparent; "
            f"font-size: {metrics.fs_label}px; font-weight: 800; letter-spacing: 0.14em;"
        )
        bl.addWidget(self._eyebrow)

        self._title = QLabel(S.ADMIN_PIN_PROMPT)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setFont(kolomna_font(metrics.fs_h2, QFont.Weight.ExtraBold))
        self._title.setStyleSheet(
            f"color: {GREEN}; background: transparent; "
            f"font-size: {metrics.fs_h2}px; font-weight: 800; "
            f"letter-spacing: -0.02em; line-height: 105%; margin: 0; padding: 0;"
        )
        bl.addWidget(self._title)

        self._dots_host = QWidget()
        self._dots_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._dots_host.setStyleSheet("background: transparent;")
        dots_row = QHBoxLayout(self._dots_host)
        dots_row.setContentsMargins(0, scale(30, metrics.width), 0, scale(4, metrics.width))
        dots_row.setSpacing(scale(26, metrics.width))
        dots_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dots: list[QLabel] = []
        dot_sz = scale(30, metrics.width)
        for _ in range(4):
            d = QLabel()
            d.setFixedSize(dot_sz, dot_sz)
            self._dots.append(d)
            dots_row.addWidget(d)
        bl.addWidget(self._dots_host)

        self._msg = QLabel("\u00a0")
        self._msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg.setFixedHeight(scale(38, metrics.width))
        self._msg.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        self._msg.setStyleSheet(
            f"color: {STRAWBERRY}; background: transparent; margin: 0; padding: 0; "
            f"font-size: {metrics.fs_label}px; font-weight: 800;"
        )
        bl.addWidget(self._msg)

        pad_host = QWidget()
        pad_host.setFixedWidth(pad_w)
        pad_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        pad_host.setStyleSheet("background: transparent;")
        key_bleed = scale(28, metrics.width)
        pad_host.setFixedWidth(pad_w + key_bleed * 2)
        pad = QGridLayout(pad_host)
        pad.setSpacing(scale(22, metrics.width))
        pad.setContentsMargins(key_bleed, 0, key_bleed, scale(22, metrics.width))
        for col in range(3):
            pad.setColumnStretch(col, 1)
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"]
        key_h = scale(110, metrics.width)
        key_shadow_b = scale(32, metrics.width)
        key_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for i, k in enumerate(keys):
            if not k:
                spacer = QWidget()
                spacer.setFixedHeight(key_h + key_shadow_b)
                spacer.setSizePolicy(key_policy)
                spacer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                spacer.setStyleSheet("background: transparent;")
                pad.addWidget(spacer, i // 3, i % 3)
                continue
            is_back = k == "⌫"
            btn = _PinKeyBtn(metrics, k, is_back=is_back)
            if is_back:
                btn.clicked.connect(self._back)
            else:
                btn.clicked.connect(lambda d=k: self._push(d))
            pad.addWidget(btn, i // 3, i % 3)
        bl.addWidget(pad_host, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._cancel = _PinCancelBtn(metrics, S.ADMIN_CANCEL)
        self._cancel.clicked.connect(self.hide)
        bl.addWidget(self._cancel, alignment=Qt.AlignmentFlag.AlignHCenter)

        outer.addWidget(self._box, alignment=Qt.AlignmentFlag.AlignCenter)
        self._box.adjustSize()
        self._sync_dots()

    @staticmethod
    def _lbl(text: str, m: KolomnaMetrics, px: int, color: str, bold: bool = False) -> QLabel:
        w = QLabel(text)
        w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weight = QFont.Weight.ExtraBold if bold else QFont.Weight.Bold
        w.setFont(kolomna_font(px, weight))
        w.setStyleSheet(f"color: {color}; background: transparent;")
        return w

    def _sync_dots(self) -> None:
        m = self._m
        dot_sz = scale(30, m.width)
        r = dot_sz // 2
        on_color = STRAWBERRY if self._err else GREEN
        border_w = scale(4, m.width)
        for i, d in enumerate(self._dots):
            if i < len(self._val):
                d.setStyleSheet(
                    f"QLabel {{ background: {on_color}; border: {border_w}px solid {on_color}; "
                    f"border-radius: {r}px; }}"
                )
            else:
                d.setStyleSheet(
                    f"QLabel {{ background: transparent; border: {border_w}px solid {INK_30}; "
                    f"border-radius: {r}px; }}"
                )

    def _push(self, digit: str) -> None:
        if len(self._val) >= 4:
            return
        self._err = False
        self._msg.setText("\u00a0")
        self._val += digit
        self._sync_dots()
        if len(self._val) == 4:
            entered = self._val
            QTimer.singleShot(160, lambda: self._check(entered))

    def _check(self, entered: str) -> None:
        if entered == self._pin:
            self._val = ""
            self.hide()
            self.pin_accepted.emit()
            return
        self._err = True
        self._msg.setText(S.ADMIN_WRONG_PIN)
        self._sync_dots()
        QTimer.singleShot(650, self._clear)

    def _clear(self) -> None:
        self._val = ""
        self._err = False
        self._msg.setText("\u00a0")
        self._sync_dots()

    def _back(self) -> None:
        self._err = False
        self._msg.setText("\u00a0")
        self._val = self._val[:-1]
        self._sync_dots()

    def retranslate(self) -> None:
        self._eyebrow.setText(S.ADMIN_ACCESS.upper())
        self._title.setText(S.ADMIN_PIN_PROMPT)
        self._cancel.set_text(S.ADMIN_CANCEL)
        if self._err:
            self._msg.setText(S.ADMIN_WRONG_PIN)

    def show_modal(self) -> None:
        self._clear()
        self.setGeometry(0, 0, self.parentWidget().width(), self.parentWidget().height())
        self.raise_()
        self.show()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            top_left = self._box.mapTo(self, self._box.rect().topLeft())
            box_rect = self._box.rect()
            box_rect.moveTopLeft(top_left)
            if not box_rect.contains(pos):
                self.hide()
        super().mouseReleaseEvent(event)


from src.ui.widgets.kolomna_admin_panel import KolomnaAdminPanel  # noqa: F401
