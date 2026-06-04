from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QStackedWidget, QVBoxLayout, QWidget

from src.core.config import AppConfig


class PhoneViewport(QFrame):
    """Фиксированная область mini app 499×913 — без растягивания QStackedWidget."""

    def __init__(self, app_cfg: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PhoneViewport")
        w, h = app_cfg.viewport_width, app_cfg.viewport_height
        self.setFixedSize(w, h)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("Root")
        lay.addWidget(self.stack)


class PhoneViewportHost(QWidget):
    """Центрирует PhoneViewport на экране киоска (1080×1920)."""

    def __init__(self, app_cfg: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PhoneViewportHost")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.phone = PhoneViewport(app_cfg)
        root.addWidget(self.phone, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
