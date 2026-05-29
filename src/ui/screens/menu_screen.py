from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.cart import Cart
from src.core.config import Settings
from src.services.catalog_sync import CatalogStore
from src.ui.layout_metrics import LayoutMetrics
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.bottom_bar import CartBottomBar
from src.ui.widgets.product_card import ProductCard


class MenuScreen(BaseScreen):
    go_cart = pyqtSignal()
    restart = pyqtSignal()

    def __init__(self, catalog: CatalogStore, cart: Cart, settings: Settings) -> None:
        super().__init__()
        self._catalog = catalog
        self._cart = cart
        self._metrics = LayoutMetrics.from_app_config(settings.app)
        self._current_category: str | None = None
        self._cards: dict[str, ProductCard] = {}

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        top = QFrame()
        top.setObjectName("TopBar")
        top.setFixedHeight(self._metrics.category_bar_height)
        top_outer = QVBoxLayout(top)
        top_outer.setContentsMargins(12, 8, 12, 8)

        cat_scroll = QScrollArea()
        cat_scroll.setWidgetResizable(True)
        cat_scroll.setFixedHeight(self._metrics.category_bar_height - 16)
        cat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        cat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        cat_scroll.setStyleSheet("background: transparent; border: none;")

        cat_host = QWidget()
        self._cat_layout = QHBoxLayout(cat_host)
        self._cat_layout.setSpacing(12)
        self._cat_layout.setContentsMargins(4, 4, 4, 4)
        cat_scroll.setWidget(cat_host)
        top_outer.addWidget(cat_scroll)

        self._cat_group = QButtonGroup(self)
        self._cat_group.setExclusive(True)
        self._layout.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._grid_host = QWidget()
        self._grid = QGridLayout(self._grid_host)
        spacing = 16 if self._metrics.is_portrait else 20
        margin = 16 if self._metrics.is_portrait else 24
        self._grid.setSpacing(spacing)
        self._grid.setContentsMargins(margin, margin, margin, margin)
        scroll.setWidget(self._grid_host)
        self._layout.addWidget(scroll, stretch=1)

        self._bottom = CartBottomBar(portrait=self._metrics.is_portrait)
        self._bottom.setFixedHeight(self._metrics.bottom_bar_height)
        self._bottom.go_cart.connect(self.go_cart.emit)
        self._bottom.restart.connect(self.restart.emit)
        self._layout.addWidget(self._bottom)

        catalog.updated.connect(self._rebuild_categories)
        cart.changed.connect(self._refresh_cart_ui)
        self._rebuild_categories()

    def _rebuild_categories(self) -> None:
        while self._cat_layout.count():
            item = self._cat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cats = self._catalog.categories
        if not cats:
            return

        all_btn = QPushButton("Все")
        all_btn.setObjectName("CategoryBtn")
        all_btn.setCheckable(True)
        all_btn.setChecked(self._current_category is None)
        all_btn.clicked.connect(lambda: self._select_category(None))
        self._cat_group.addButton(all_btn)
        self._cat_layout.addWidget(all_btn)

        for cat in cats:
            btn = QPushButton(cat.name)
            btn.setObjectName("CategoryBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, cid=cat.id: self._select_category(cid))
            if self._current_category == cat.id:
                btn.setChecked(True)
            self._cat_group.addButton(btn)
            self._cat_layout.addWidget(btn)

        self._cat_layout.addStretch()
        self._rebuild_products()

    def _select_category(self, category_id: str | None) -> None:
        self._current_category = category_id
        self._rebuild_products()

    def _rebuild_products(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()

        products = self._catalog.products_for_category(self._current_category)
        cols = self._metrics.product_grid_columns
        for i, product in enumerate(products):
            qty = self._cart.quantity_of(product.id)
            card = ProductCard(
                product,
                qty,
                image_height=self._metrics.product_image_height,
                portrait=self._metrics.is_portrait,
            )
            card.add_clicked.connect(self._on_add)
            card.quantity_changed.connect(self._on_qty)
            self._cards[product.id] = card
            row, col = divmod(i, cols)
            self._grid.addWidget(card, row, col)

        self._refresh_cart_ui()

    def _on_add(self, product_id: str) -> None:
        p = self._catalog.product_by_id(product_id)
        if p:
            self._cart.add(p, 1)
            if product_id in self._cards:
                self._cards[product_id].set_quantity(self._cart.quantity_of(product_id))

    def _on_qty(self, product_id: str, qty: int) -> None:
        if qty == 0:
            self._cart.remove(product_id)
        else:
            p = self._catalog.product_by_id(product_id)
            if p:
                self._cart.set_quantity(product_id, qty)
        if product_id in self._cards:
            self._cards[product_id].set_quantity(self._cart.quantity_of(product_id))

    def _refresh_cart_ui(self) -> None:
        self._bottom.update_summary(self._cart.positions_count, self._cart.total_display())
        for pid, card in self._cards.items():
            card.set_quantity(self._cart.quantity_of(pid))
