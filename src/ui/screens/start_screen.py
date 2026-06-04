from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.core.config import ROOT, Settings
from src.ui.image_utils import load_pixmap, scale_pixmap
from src.ui.layout_metrics import LayoutMetrics
from src.ui.screens.base_screen import BaseScreen

_FONT_UNBOUNDED = "'Unbounded', ui-sans-serif, system-ui, sans-serif"
_FONT_INTER = "'Inter', ui-sans-serif, system-ui, sans-serif"


class StartScreen(BaseScreen):
    tapped = pyqtSignal()

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__()
        metrics = (
            LayoutMetrics.from_app_config(settings.app) if settings else None
        )
        phone = metrics.phone_layout if metrics else True
        portrait = metrics.is_portrait if metrics else False

        self.setObjectName("StartScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget#StartScreen { background-color: #FFFFFF; }")

        if phone:
            self._layout.setContentsMargins(16, 16, 16, 16)
        else:
            self._layout.setContentsMargins(24, 24, 24, 24)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24 if portrait else 16)

        brand = QHBoxLayout()
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setSpacing(16)
        logo = QLabel()
        logo.setFixedSize(80 if portrait else 64, 80 if portrait else 64)
        icon_path = ROOT / "assets" / "branding" / "katusha_icon.png"
        if icon_path.is_file():
            pix = load_pixmap(icon_path)
            if not pix.isNull():
                logo.setPixmap(scale_pixmap(pix, logo.width(), logo.height()))
        logo.setScaledContents(True)
        logo.setStyleSheet("background: transparent; border: none;")
        brand.addWidget(logo)
        titles = QVBoxLayout()
        titles.setSpacing(4)
        title = QLabel("Катюша")
        title.setObjectName("BrandTitle")
        title.setStyleSheet(
            f"QLabel#BrandTitle {{ font-family: {_FONT_UNBOUNDED}; font-size: 18px; "
            "font-weight: 700; color: #111827; background: transparent; }"
        )
        sub = QLabel("Фермерский маркет")
        sub.setObjectName("BrandSub")
        sub.setStyleSheet(
            f"QLabel#BrandSub {{ font-family: {_FONT_INTER}; font-size: 12px; "
            "font-weight: 400; color: #6B7280; background: transparent; }"
        )
        titles.addWidget(title)
        titles.addWidget(sub)
        brand.addLayout(titles)
        layout.addLayout(brand)

        hint = QLabel("Нажмите, чтобы начать")
        hint.setObjectName("Subtitle")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(
            f"QLabel#Subtitle {{ font-family: {_FONT_INTER}; font-size: 15px; "
            "font-weight: 400; color: #6B7280; background: transparent; }"
        )
        layout.addWidget(hint)

        btn_w = 360
        if metrics:
            btn_w = max(280, metrics.width - metrics.page_padding * 2)

        btn = QPushButton("Начать покупки")
        btn.setObjectName("PrimaryBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setMinimumHeight(56 if phone else 72)
        btn.setMaximumHeight(56 if phone else 72)
        btn.setMinimumWidth(btn_w)
        btn.setMaximumWidth(btn_w)
        btn.setStyleSheet(
            f"QPushButton#PrimaryBtn {{ background-color: #3CB85D; color: #000000; "
            f"border: none; border-radius: 16px; font-family: {_FONT_UNBOUNDED}; "
            "font-size: 14px; font-weight: 700; padding: 12px 24px; }"
            "QPushButton#PrimaryBtn:pressed { background-color: #35A653; }"
        )
        btn.clicked.connect(self.tapped.emit)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        if portrait:
            self._layout.addStretch(1)
        self._layout.addLayout(layout)
        if portrait:
            self._layout.addStretch(1)
