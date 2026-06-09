from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
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


def _pin_key_button(
    metrics: KolomnaMetrics,
    label: str,
    *,
    is_back: bool,
    on_click,
) -> QPushButton:
    w = metrics.width
    key_h = scale(110, w)
    key_r = metrics.radius
    key_fs = scale(42 if is_back else 48, w)

    btn = QPushButton("\u232b" if is_back else label)
    btn.setMinimumHeight(key_h)
    btn.setMaximumHeight(key_h)
    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if is_back:
        btn.setFont(_pin_backspace_font(key_fs))
    else:
        btn.setFont(kolomna_font(key_fs, QFont.Weight.ExtraBold))
    btn.setStyleSheet(
        f"QPushButton {{ background: #FFFFFF; color: {GREEN}; border: none; "
        f"border-radius: {key_r}px; font-size: {key_fs}px; font-weight: 800; "
        f"min-height: {key_h}px; max-height: {key_h}px; padding: 0; }}"
        f"QPushButton:pressed {{ background: {CREAM_DEEP}; }}"
    )
    key_shadow = QGraphicsDropShadowEffect(btn)
    key_shadow.setBlurRadius(scale(28, w))
    key_shadow.setOffset(0, scale(12, w))
    key_shadow.setColor(QColor(20, 56, 33, 102))
    btn.setGraphicsEffect(key_shadow)
    btn.clicked.connect(on_click)
    return btn


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
        pad = QGridLayout(pad_host)
        pad.setSpacing(scale(22, metrics.width))
        pad.setContentsMargins(0, 0, 0, scale(22, metrics.width))
        for col in range(3):
            pad.setColumnStretch(col, 1)
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "⌫"]
        key_h = scale(110, metrics.width)
        key_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for i, k in enumerate(keys):
            if not k:
                spacer = QWidget()
                spacer.setFixedHeight(key_h)
                spacer.setSizePolicy(key_policy)
                spacer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                spacer.setStyleSheet("background: transparent;")
                pad.addWidget(spacer, i // 3, i % 3)
                continue
            is_back = k == "⌫"
            btn = _pin_key_button(
                metrics,
                k,
                is_back=is_back,
                on_click=self._back if is_back else (lambda checked=False, d=k: self._push(d)),
            )
            pad.addWidget(btn, i // 3, i % 3)
        bl.addWidget(pad_host, alignment=Qt.AlignmentFlag.AlignHCenter)

        cancel_h = scale(104, metrics.width)
        cancel_ph = scale(56, metrics.width)
        self._cancel = QPushButton(S.ADMIN_CANCEL)
        self._cancel.setObjectName("KolomnaAdminCancel")
        self._cancel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel.setFixedHeight(cancel_h)
        self._cancel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._cancel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._cancel.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold))
        self._cancel.setStyleSheet(
            f"QPushButton#KolomnaAdminCancel {{ background: transparent; color: {GREEN}; "
            f"border: 3px solid {GREEN}; border-radius: 999px; "
            f"padding: 0 {cancel_ph}px; margin: 0; "
            f"font-size: {metrics.fs_h3}px; font-weight: 800; "
            f"min-height: {cancel_h}px; max-height: {cancel_h}px; }}"
            f"QPushButton#KolomnaAdminCancel:pressed {{ background: {GREEN}; color: {CREAM}; }}"
        )
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
        self._cancel.setText(S.ADMIN_CANCEL)
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
