from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.core.config import ROOT
from src.ui.image_utils import load_pixmap, scale_pixmap


class KatushaHeader(QFrame):
    """Шапка каталога как в reference/katusha-miniapp/index.html."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("AppHeader")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 10)
        outer.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        logo = QLabel()
        logo.setFixedSize(40, 40)
        icon_path = ROOT / "assets" / "branding" / "katusha_icon.png"
        if icon_path.is_file():
            pix = load_pixmap(icon_path)
            if not pix.isNull():
                logo.setPixmap(scale_pixmap(pix, 40, 40))
                logo.setStyleSheet("border-radius: 12px;")
        logo.setScaledContents(True)
        brand_row.addWidget(logo)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("Катюша")
        title.setObjectName("BrandTitle")
        sub = QLabel("Фермерский маркет")
        sub.setObjectName("BrandSub")
        titles.addWidget(title)
        titles.addWidget(sub)
        brand_row.addLayout(titles, stretch=1)
        outer.addLayout(brand_row)

        search = QFrame()
        search.setObjectName("SearchBar")
        search_lay = QHBoxLayout(search)
        search_lay.setContentsMargins(14, 10, 14, 10)
        search_lay.setSpacing(8)
        icon = QLabel("🔍")
        icon.setStyleSheet("font-size: 16px;")
        placeholder = QLabel("Поиск продуктов…")
        placeholder.setObjectName("SearchPlaceholder")
        search_lay.addWidget(icon)
        search_lay.addWidget(placeholder, stretch=1)
        outer.addWidget(search)
