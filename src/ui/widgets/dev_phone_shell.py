from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.config import AppConfig


class DevPhoneShell(QWidget):
    """Оболочка для теста: полоса «Закрыть» + вертикальная область как у mini app."""

    close_requested = pyqtSignal()

    def __init__(self, app_cfg: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DevOuter")

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 4, 8, 8)
        root.setSpacing(4)

        bar = QHBoxLayout()
        bar.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setObjectName("DevCloseBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close_requested.emit)
        bar.addWidget(close_btn)
        root.addLayout(bar)

        self._phone = QFrame()
        self._phone.setObjectName("PhoneViewport")
        self._phone.setFixedSize(app_cfg.viewport_width, app_cfg.viewport_height)

        phone_lay = QVBoxLayout(self._phone)
        phone_lay.setContentsMargins(0, 0, 0, 0)
        phone_lay.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("Root")
        phone_lay.addWidget(self.stack)

        root.addWidget(self._phone, alignment=Qt.AlignmentFlag.AlignHCenter)

    @property
    def phone_frame(self) -> QFrame:
        return self._phone
