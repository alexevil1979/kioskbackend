from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QWidget

from src.core.cart import Cart
from src.core.config import Settings
from src.models.product import Product
from src.services.catalog_sync import CatalogStore
from src.ui import kolomna_strings as S
from src.ui.katusha_hub_catalog import _category_sort_key
from src.ui.kolomna_catalog import KOLOMNA_TOURS_ID, hub_slot_index_for_category, kolomna_card_accent
from src.ui.kolomna_i18n import hub_label_for_slot
from src.ui.kolomna_fly_berry import fly_berry_to_cart, fly_pixmap_for_product
from src.ui.kolomna_prefs import load_kolomna_prefs
from src.ui.kolomna_tokens import CREAM, KolomnaMetrics
from src.ui.screens.base_screen import BaseScreen
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.widgets.kolomna_footbar import KolomnaFootBar
from src.ui.widgets.kolomna_prod_row import KolomnaProdRow
from src.ui.widgets.kolomna_product_overlay import KolomnaProductOverlay
from src.ui.widgets.kolomna_toast import KolomnaAddedToast
from src.ui.widgets.kolomna_topbar import KolomnaTopBar


class KolomnaMenuScreen(BaseScreen):
    go_cart = pyqtSignal()
    back_to_categories = pyqtSignal()

    def __init__(self, catalog: CatalogStore, cart: Cart, settings: Settings) -> None:
        super().__init__()
        self._catalog = catalog
        self._cart = cart
        self._settings = settings
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)
        self._category_id: str | None = None
        self._toast = KolomnaAddedToast(self._m, parent=self)

        self.setObjectName("KolomnaMenuScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top = KolomnaTopBar(self._m, show_back=True, show_lang=True)
        self._top.back_clicked.connect(self.back_to_categories.emit)
        self._top.cart_clicked.connect(self.go_cart.emit)
        self._layout.addWidget(self._top)

        from PyQt6.QtWidgets import QScrollArea

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {CREAM}; }}")
        enable_kinetic_scroll(self._scroll)

        self._list_host = QWidget()
        self._list_host.setStyleSheet(f"background: {CREAM};")
        self._list_lay = QVBoxLayout(self._list_host)
        pad = self._m.pad
        # menu-list: margin -pad + padding gap → отступ gap от края экрана
        self._list_lay.setContentsMargins(self._m.gap, self._m.gap, self._m.gap, self._m.gap)
        self._list_lay.setSpacing(self._m.gap)
        self._scroll.setWidget(self._list_host)
        self._layout.addWidget(self._scroll, stretch=1)

        self._footbar = KolomnaFootBar(self._m)
        self._footbar.hide()
        self._footbar.primary_clicked.connect(self.go_cart.emit)
        self._layout.addWidget(self._footbar)

        self._product_overlay = KolomnaProductOverlay(self._m, parent=self)
        self._product_overlay.confirmed.connect(self._on_product_confirm)
        self._product_overlay.closed.connect(self._on_product_overlay_closed)

        catalog.updated.connect(self._rebuild)
        cart.changed.connect(self._refresh_cart)
        self._refresh_cart()

    def open_category(self, category_id: str | None) -> None:
        self._category_id = str(category_id) if category_id else None
        self._rebuild()
        self._scroll.verticalScrollBar().setValue(0)

    def open_hub(self, hub_id: str | None) -> None:
        self.open_category(hub_id)

    def _category_title(self) -> str:
        if not self._category_id:
            return ""
        if self._category_id == KOLOMNA_TOURS_ID:
            return hub_label_for_slot(3)
        cats = sorted(self._catalog.categories, key=_category_sort_key)
        for i, c in enumerate(cats):
            if c.id == self._category_id:
                return hub_label_for_slot(i)
        for c in self._catalog.categories:
            if c.id == self._category_id:
                return c.name.strip()
        return ""

    def _category_accent(self) -> str:
        if not self._category_id:
            return kolomna_card_accent(0)
        cats = self._catalog.categories
        for i, c in enumerate(cats):
            if c.id == self._category_id:
                return kolomna_card_accent(i)
        return kolomna_card_accent(0)

    def _products(self) -> list[Product]:
        if not self._category_id:
            return []
        return [p for p in self._catalog.products_for_category(self._category_id) if p.in_stock]

    def _rebuild(self) -> None:
        title = self._category_title()
        accent = self._category_accent()
        self._top.set_title(title, accent=accent)

        while self._list_lay.count():
            item = self._list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for product in self._products():
            row = KolomnaProdRow(product, self._m)
            row.add_clicked.connect(self._quick_add)
            row.clicked.connect(self._open_product)
            self._list_lay.addWidget(row)

        self._list_lay.addStretch(1)

    def _product_by_id(self, product_id: str) -> Product | None:
        for p in self._products():
            if p.id == product_id:
                return p
        return None

    def _category_index(self) -> int:
        if not self._category_id:
            return 0
        return hub_slot_index_for_category(self._catalog.categories, self._category_id)

    def _is_berry_menu(self) -> bool:
        return bool(self._category_id) and self._category_id != KOLOMNA_TOURS_ID

    def _row_for_product(self, product_id: str) -> KolomnaProdRow | None:
        for i in range(self._list_lay.count()):
            item = self._list_lay.itemAt(i)
            if item is None:
                continue
            w = item.widget()
            if isinstance(w, KolomnaProdRow) and w.product_id == product_id:
                return w
        return None

    def _cart_fly_target(self) -> QWidget | None:
        if self._footbar.isVisible():
            return self._footbar._primary
        if self._top._cart_pill.isVisible():
            return self._top._cart_pill
        return None

    def _fly_berry(self, source: QWidget | None, product: Product) -> None:
        if not self._is_berry_menu():
            return
        pix = fly_pixmap_for_product(product, category_index=self._category_index())
        if pix.isNull():
            return
        cart_btn = self._cart_fly_target()

        def _done() -> None:
            target = self._cart_fly_target()
            if target is not None and hasattr(target, "bump"):
                target.bump()

        fly_berry_to_cart(
            self,
            start_widget=source,
            cart_button=cart_btn,
            pixmap=pix,
            viewport_width=self._m.width,
            on_finish=_done,
        )

    def _quick_add(self, product_id: str) -> None:
        product = self._product_by_id(product_id)
        row = self._row_for_product(product_id)
        if product:
            self._cart.add(product, 1)
            self._refresh_cart()
            self._fly_berry(row.media_widget() if row else None, product)
            self._flash_toast(S.ADDED_TOAST, bump=False)

    def _open_product(self, product_id: str) -> None:
        prefs = load_kolomna_prefs()
        if prefs.skip_product:
            self._quick_add(product_id)
            return
        product = self._product_by_id(product_id)
        if product:
            self._scroll.hide()
            self._footbar.hide()
            self._product_overlay.open_product(
                product,
                category_title=self._category_title(),
                accent=self._category_accent(),
            )

    def _on_product_overlay_closed(self) -> None:
        self._scroll.show()
        self._refresh_cart()

    def _on_product_confirm(self, product_id: str, qty: int) -> None:
        product = self._product_by_id(product_id)
        if product:
            src = self._product_overlay.fly_source()
            self._cart.add(product, qty)
            self._scroll.show()
            self._refresh_cart()
            self._fly_berry(src, product)
            self._flash_toast(S.ADDED_TOAST, bump=False)
            self._product_overlay.hide()

    def _flash_toast(self, text: str, *, bump: bool = True) -> None:
        bump_btn = None
        above = None
        if self._footbar.isVisible():
            above = self._footbar
            if bump:
                bump_btn = self._footbar._primary
        self._toast.flash(text, bump_btn=bump_btn, above=above)

    def _refresh_cart(self) -> None:
        count = self._cart.positions_count
        total = self._cart.total_display()
        self._top.update_cart(count, total)
        if count > 0:
            self._footbar.set_primary(f"{S.CART} · {count}", sum_text=total)
            self._footbar.show()
        else:
            self._footbar.hide()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._product_overlay.isVisible():
            self._product_overlay.setGeometry(0, 0, self.width(), self.height())

    def retranslate(self) -> None:
        self._top.retranslate()
        self._rebuild()
        self._refresh_cart()
        if self._product_overlay.isVisible():
            self._product_overlay.retranslate()
