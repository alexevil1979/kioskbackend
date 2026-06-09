from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QFrame, QStackedWidget, QVBoxLayout, QWidget

from src.core.config import AppConfig


class DevPhoneShell(QWidget):
    """Dev-оболочка: окно 499×913, рабочая область на весь viewport."""

    close_requested = pyqtSignal()

    def __init__(self, app_cfg: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DevOuter")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(app_cfg.viewport_width, app_cfg.viewport_height)
        self.setStyleSheet("QWidget#DevOuter { background: #000000; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._phone = QFrame()
        self._phone.setObjectName("PhoneViewport")
        self._phone.setFixedSize(app_cfg.content_width, app_cfg.content_height)
        self._phone.setStyleSheet("QFrame#PhoneViewport { background: #F6EFD8; border: none; }")

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

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.close_requested.emit()
            return
        super().keyPressEvent(event)
