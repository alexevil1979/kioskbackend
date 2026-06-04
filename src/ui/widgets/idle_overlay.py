from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

_FONT_UNBOUNDED = "'Unbounded', ui-sans-serif, system-ui, sans-serif"
_FONT_INTER = "'Inter', ui-sans-serif, system-ui, sans-serif"


class IdleWarningOverlay(QWidget):
    stay = pyqtSignal()
    leave = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("IdleOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget#IdleOverlay { background: rgba(15, 17, 21, 0.75); }")
        self.hide()

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

    def set_countdown_seconds(self, seconds: int) -> None:
        self._subtitle.setText(f"Сессия будет сброшена через {max(1, seconds)} секунд")

    def _on_stay(self) -> None:
        self.hide()
        self.stay.emit()

    def show_overlay(self, countdown_seconds: int = 10) -> None:
        self.set_countdown_seconds(countdown_seconds)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.raise_()
        self.show()
