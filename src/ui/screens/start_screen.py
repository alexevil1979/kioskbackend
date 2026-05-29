from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import primary_button


class StartScreen(BaseScreen):
    tapped = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Ферма")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Свежие продукты с нашей фермы")
        sub.setObjectName("Subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        hint = QLabel("Нажмите, чтобы начать")
        hint.setStyleSheet("font-size:28px;margin-top:48px;color:#5C4A32;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        btn = primary_button("Начать покупки")
        btn.setMinimumSize(400, 80)
        btn.clicked.connect(self.tapped.emit)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()
        self._layout.addLayout(layout)
        self._layout.addStretch()
