from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.config import ROOT, Settings
from src.ui.layout_metrics import LayoutMetrics
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import primary_button


class StartScreen(BaseScreen):
    tapped = pyqtSignal()

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__()
        portrait = False
        if settings:
            portrait = LayoutMetrics.from_app_config(settings.app).is_portrait

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24 if portrait else 16)

        hero_path = ROOT / "assets" / "branding" / "farm_hero.jpg"
        if hero_path.exists():
            hero = QLabel()
            hero.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pix = QPixmap(str(hero_path))
            max_w = 900 if portrait else 700
            hero.setPixmap(
                pix.scaledToWidth(max_w, Qt.TransformationMode.SmoothTransformation)
            )
            layout.addWidget(hero)
        else:
            title = QLabel("Ферма")
            title.setObjectName("ScreenTitle")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

        sub = QLabel("Свежие продукты\nс нашей фермы" if portrait else "Свежие продукты с нашей фермы")
        sub.setObjectName("Subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        hint = QLabel("Нажмите, чтобы начать")
        hint.setStyleSheet(
            f"font-size:{32 if portrait else 28}px;margin-top:24px;color:#5C4A32;"
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        btn = primary_button("Начать покупки")
        if portrait:
            btn.setMinimumSize(520, 96)
        else:
            btn.setMinimumSize(400, 80)
        btn.clicked.connect(self.tapped.emit)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch(1 if portrait else 0)
        self._layout.addLayout(layout)
        self._layout.addStretch(1)
