from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from src.core.config import Settings
from src.ui.kolomna_cta import cta_palette
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, GREEN, INK_60, KolomnaMetrics, scale

_FONT_UNBOUNDED = "'Unbounded', ui-sans-serif, system-ui, sans-serif"
_FONT_INTER = "'Inter', ui-sans-serif, system-ui, sans-serif"


class _IdlePillBtn(QWidget):
    clicked = pyqtSignal()

    def __init__(
        self,
        metrics: KolomnaMetrics,
        text: str,
        *,
        primary: bool,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics
        self._text = text
        self._primary = primary
        self._pressed = False
        w = metrics.width
        self._h = scale(104, w)
        self._pad_h = scale(40, w)
        self._border = max(2, scale(3, w))
        weight = QFont.Weight.Black if primary else QFont.Weight.ExtraBold
        self._font = kolomna_font(metrics.fs_h3, weight)
        fm = QFontMetrics(self._font)
        self.setFixedHeight(self._h)
        self.setMinimumWidth(fm.horizontalAdvance(text) + self._pad_h * 2)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        r = rect.height() / 2.0
        if self._primary:
            pal = cta_palette()
            bg = QColor(pal.bg_active if self._pressed else pal.bg)
            fg = QColor(pal.fg)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(bg)
            p.drawRoundedRect(rect, r, r)
        else:
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


class IdleWarningOverlay(QWidget):
    stay = pyqtSignal()
    leave = pyqtSignal()

    def __init__(self, parent: QWidget | None = None, *, settings: Settings | None = None) -> None:
        super().__init__(parent)
        self._kolomna = bool(settings and settings.app.ui_theme == "kolomna")
        self._m = (
            KolomnaMetrics.from_viewport(settings.app.content_width, settings.app.content_height)
            if self._kolomna and settings
            else None
        )
        self.setObjectName("IdleOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        if self._kolomna and self._m:
            self.setStyleSheet("QWidget#IdleOverlay { background: rgba(20, 56, 33, 0.6); }")
            self._build_kolomna()
        else:
            self.setStyleSheet("QWidget#IdleOverlay { background: rgba(15, 17, 21, 0.75); }")
            self._build_legacy()
        self.hide()
        if parent is not None:
            parent.installEventFilter(self)

    def _build_legacy(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("IdleDialogCard")
        card.setFixedWidth(340)
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setStyleSheet(
            "QFrame#IdleDialogCard { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 20px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 22, 20, 20)
        card_layout.setSpacing(14)

        title = QLabel("Вы ещё здесь?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-family: {_FONT_UNBOUNDED}; font-size: 18px; font-weight: 700; "
            "color: #111827; background: transparent;"
        )
        card_layout.addWidget(title)

        self._subtitle = QLabel("Сессия будет сброшена через 10 секунд")
        self._subtitle.setWordWrap(True)
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle.setStyleSheet(
            f"font-family: {_FONT_INTER}; font-size: 14px; font-weight: 500; "
            "color: #6B7280; background: transparent; padding: 0 4px;"
        )
        card_layout.addWidget(self._subtitle)

        btn_stay = QPushButton("Да, продолжаю")
        btn_stay.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_stay.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_stay.setMinimumHeight(48)
        btn_stay.setStyleSheet(
            f"QPushButton {{ background: #35C46A; color: #051B0D; border: none; border-radius: 14px; "
            f"font-family: {_FONT_UNBOUNDED}; font-size: 12px; font-weight: 700; padding: 0 16px; }}"
            "QPushButton:pressed { background: #2FB05E; }"
        )
        btn_stay.clicked.connect(self._on_stay)
        card_layout.addWidget(btn_stay)

        btn_leave = QPushButton("Начать заново")
        btn_leave.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_leave.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_leave.setMinimumHeight(48)
        btn_leave.setStyleSheet(
            f"QPushButton {{ background: #FFFFFF; color: #111827; border: 1px solid #D8DEE6; "
            f"border-radius: 14px; font-family: {_FONT_INTER}; font-size: 14px; font-weight: 600; "
            "padding: 0 16px; }"
            "QPushButton:pressed { background: #F3F4F6; }"
        )
        btn_leave.clicked.connect(self.leave.emit)
        card_layout.addWidget(btn_leave)

        outer.addWidget(card)

    def _build_kolomna(self) -> None:
        assert self._m is not None
        m = self._m
        pad_outer = scale(70, m.width)
        box_w = min(scale(680, m.width), max(1, m.width - 2 * pad_outer))
        pad64 = scale(64, m.width)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(pad_outer, pad_outer, pad_outer, pad_outer)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("IdleDialogCard")
        card.setFixedWidth(box_w)
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setStyleSheet(
            f"QFrame#IdleDialogCard {{ background: {CREAM}; "
            f"border: none; border-radius: {m.radius_lg}px; }}"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(pad64, pad64, pad64, pad64)
        card_layout.setSpacing(scale(26, m.width))
        card_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("Вы ещё здесь?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setFont(kolomna_font(m.fs_h2, QFont.Weight.ExtraBold))
        title.setStyleSheet(f"color: {GREEN}; background: transparent;")
        card_layout.addWidget(title)

        self._subtitle = QLabel("Сессия будет сброшена через 10 секунд")
        self._subtitle.setWordWrap(True)
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle.setFont(kolomna_font(m.fs_body, QFont.Weight.Medium))
        self._subtitle.setStyleSheet(f"color: {INK_60}; background: transparent;")
        card_layout.addWidget(self._subtitle)

        btn_stay = _IdlePillBtn(m, "Да, продолжаю", primary=True)
        btn_stay.clicked.connect(self._on_stay)
        card_layout.addWidget(btn_stay)

        btn_leave = _IdlePillBtn(m, "Начать заново", primary=False)
        btn_leave.clicked.connect(self.leave.emit)
        card_layout.addWidget(btn_leave)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_countdown_seconds(self, seconds: int) -> None:
        self._subtitle.setText(f"Сессия будет сброшена через {max(1, seconds)} секунд")

    def hide(self) -> None:  # noqa: A003
        super().hide()
        self.setGeometry(0, 0, 0, 0)

    def _on_stay(self) -> None:
        self.hide()
        self.stay.emit()

    def _sync_geometry(self) -> None:
        parent = self.parentWidget()
        if parent is not None:
            self.setGeometry(parent.rect())

    def eventFilter(self, watched, event) -> bool:  # noqa: N802
        if (
            watched is self.parentWidget()
            and event.type() == QEvent.Type.Resize
            and self.isVisible()
        ):
            self._sync_geometry()
        return False

    def show_overlay(self, countdown_seconds: int = 10) -> None:
        self.set_countdown_seconds(countdown_seconds)
        self._sync_geometry()
        self.show()
        self.raise_()

    def refresh_cta(self) -> None:
        if not self._kolomna:
            return
        for btn in self.findChildren(_IdlePillBtn):
            if btn._primary:  # noqa: SLF001
                btn.update()
