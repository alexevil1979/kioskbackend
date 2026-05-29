from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.screens.base_screen import BaseScreen


class SuccessScreen(BaseScreen):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("✓")
        icon.setStyleSheet("font-size:120px;color:#3D7C2E;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Спасибо! Заберите чек.")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._countdown = QLabel("Возврат в меню через несколько секунд…")
        self._countdown.setObjectName("Subtitle")
        self._countdown.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._countdown)

        self._layout.addStretch()
        self._layout.addLayout(layout)
        self._layout.addStretch()

    def set_countdown_text(self, text: str) -> None:
        self._countdown.setText(text)
