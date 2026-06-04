from __future__ import annotations

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.core.config import Settings
from src.services.catalog_sync import CatalogStore
from src.ui.katusha_hub_tokens import HUB_SCROLL_H, NAV_HEIGHT, PAGE_PAD, Y_HEADER, Y_TITLE
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.bottom_nav_bar import BottomNavBar
from src.ui.widgets.categories_hub_block import CategoriesScrollContent
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.widgets.miniapp_header import MiniAppHeader


class CategoriesScreen(BaseScreen):
    category_selected = pyqtSignal(str)
    show_all_products = pyqtSignal()
    open_cart = pyqtSignal()

    def __init__(self, catalog: CatalogStore, settings: Settings) -> None:
        super().__init__()
        self._catalog = catalog
        self._width = settings.app.viewport_width
        vp_h = settings.app.viewport_height
        self._scroll_h = HUB_SCROLL_H

        self.setObjectName("CategoriesScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.setFixedSize(self._width, vp_h)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumSize(QSize(self._width, vp_h))
        self.setMaximumSize(QSize(self._width, vp_h))

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._body = QWidget()
        self._body.setObjectName("CategoriesBody")

        body_lay = QVBoxLayout(self._body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        self._header = MiniAppHeader()
        body_lay.addWidget(self._header)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("CategoriesScroll")
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setStyleSheet(
            "QScrollArea#CategoriesScroll { background: #FFFFFF; border: none; }"
        )
        vp = self._scroll.viewport()
        vp.setStyleSheet("background: #FFFFFF;")
        vp.setAutoFillBackground(True)
        self._scroll.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        self._scroll_content = CategoriesScrollContent()
        self._scroll.setWidget(self._scroll_content)
        self._scroll_content.category_selected.connect(self.category_selected.emit)
        enable_kinetic_scroll(self._scroll)

        # 182 + 652 + 79 = 913; контент короче — белое поле, без лишнего скролла
        self._scroll.setFixedHeight(HUB_SCROLL_H)
        body_lay.addWidget(self._scroll)

        btn_all = QPushButton(self._body)
        btn_all.setObjectName("HeaderAllHit")
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_all.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_all.clicked.connect(self.show_all_products.emit)
        btn_all.setGeometry(self._width - PAGE_PAD - 48, Y_TITLE, 48, 22)
        btn_all.setStyleSheet("background: transparent; border: none;")
        btn_all.raise_()

        self._placeholder = QLabel("Категории загружаются…", self._body)
        self._placeholder.setObjectName("Subtitle")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setGeometry(0, Y_HEADER, self._width, self._scroll_h)
        self._placeholder.hide()

        nav_wrap = QWidget()
        nav_wrap.setObjectName("BottomNavWrap")
        nav_wrap.setFixedHeight(NAV_HEIGHT)
        nav_lay = QVBoxLayout(nav_wrap)
        nav_lay.setContentsMargins(0, 0, 0, 0)
        self._bottom_nav = BottomNavBar()
        self._bottom_nav.set_active("catalog")
        self._bottom_nav.cart_clicked.connect(self.open_cart.emit)
        self._bottom_nav.catalog_clicked.connect(self._refresh_hub)
        nav_lay.addWidget(self._bottom_nav)

        self._layout.addWidget(self._body, stretch=1)
        self._layout.addWidget(nav_wrap)

        catalog.updated.connect(self._refresh_hub)
        self._refresh_hub()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._scroll_to_top()

    def _scroll_to_top(self) -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.minimum())

    def _refresh_hub(self) -> None:
        summaries = self._catalog.category_summaries()
        if summaries:
            self._placeholder.hide()
            self._scroll.show()
            self._scroll_content.set_summaries(summaries)
            self._scroll_content.show()
            self._scroll.updateGeometry()
            self._scroll_to_top()
        else:
            self._scroll.hide()
            self._placeholder.show()
