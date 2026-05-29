from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.core.config import ROOT, Settings
from src.ui.image_utils import load_pixmap, scale_pixmap
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
        layout.setSpacing(20 if portrait else 16)

        hero_path = ROOT / "assets" / "branding" / "farm_hero.jpg"
        if hero_path.is_file():
            pix = load_pixmap(hero_path)
            if not pix.isNull():
                hero = QLabel()
                hero.setAlignment(Qt.AlignmentFlag.AlignCenter)
                max_w = 960 if portrait else 700
                max_h = 420 if portrait else 320
                hero.setPixmap(scale_pixmap(pix, max_w, max_h))
                layout.addWidget(hero)
            else:
                layout.addWidget(self._title_label())
        else:
            layout.addWidget(self._title_label())

        sub = QLabel("Свежие продукты\nс нашей фермы")
        sub.setObjectName("Subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        hint = QLabel("Нажмите, чтобы начать")
        hint.setStyleSheet(
            f"font-size:{28 if portrait else 24}px;color:#5C4A32;"
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        btn = primary_button("Начать покупки")
        btn.setMinimumHeight(88 if portrait else 72)
        btn.setMinimumWidth(480 if portrait else 360)
        btn.clicked.connect(self.tapped.emit)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        if portrait:
            self._layout.addStretch(1)
        self._layout.addLayout(layout)
        if portrait:
            self._layout.addStretch(1)

    @staticmethod
    def _title_label() -> QLabel:
        title = QLabel("Ферма")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return title
