from __future__ import annotations



from PyQt6.QtCore import Qt, pyqtSignal

from PyQt6.QtWidgets import QSizePolicy



from src.core.cart import Cart

from src.core.config import Settings

from src.services.catalog_sync import CatalogStore

from src.ui import kolomna_strings as S

from src.ui.kolomna_prefs import KolomnaPrefs, load_kolomna_prefs

from src.ui.kolomna_tokens import CREAM, KolomnaMetrics

from src.ui.screens.base_screen import BaseScreen

from src.ui.widgets.kolomna_admin_modals import KolomnaAdminPanel, KolomnaAdminPinModal

from src.ui.widgets.kolomna_catalog_bar import KolomnaCatalogBar

from src.ui.widgets.kolomna_footbar import KolomnaFootBar

from src.ui.widgets.kolomna_fullbleed_grid import KolomnaFullbleedGrid

from src.ui.widgets.kolomna_info_modal import KolomnaInfoModal





class CategoriesScreen(BaseScreen):

    """Каталог fullbleed 2×2 — как catalogStyle: fullbleed в референсе."""



    category_selected = pyqtSignal(str)

    show_all_products = pyqtSignal()

    open_cart = pyqtSignal()

    prefs_changed = pyqtSignal(KolomnaPrefs)



    def __init__(self, catalog: CatalogStore, cart: Cart, settings: Settings) -> None:

        super().__init__()

        self._catalog = catalog

        self._cart = cart

        self._settings = settings

        self._width = settings.app.content_width

        vp_h = settings.app.content_height

        self._m = KolomnaMetrics.from_viewport(self._width, vp_h)

        self._prefs = load_kolomna_prefs()



        self.setObjectName("CategoriesScreen")

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet(f"background-color: {CREAM};")

        self.setFixedSize(self._width, vp_h)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)



        self._layout.setContentsMargins(0, 0, 0, 0)

        self._layout.setSpacing(0)



        self._bar = KolomnaCatalogBar(self._m)

        self._bar.info_clicked.connect(self._open_info)

        self._bar.admin_requested.connect(self._open_admin_pin)

        self._bar.lang_changed.connect(self._on_lang_changed)

        self._layout.addWidget(self._bar)



        self._grid = KolomnaFullbleedGrid(self._m)

        self._grid.tile_selected.connect(self.category_selected.emit)

        self._layout.addWidget(self._grid, stretch=1)



        self._footbar = KolomnaFootBar(self._m)

        self._footbar.hide()

        self._footbar.primary_clicked.connect(self.open_cart.emit)

        self._layout.addWidget(self._footbar)



        self._info_modal = KolomnaInfoModal(self._m, self._prefs.hours, parent=self)

        pin = settings.kiosk.admin_pin or "1111"
        # Референс Kolomna и старый дефолт конфига — 1111, не 1234.
        if settings.app.ui_theme == "kolomna" and pin == "1234":
            pin = "1111"

        self._admin_pin = KolomnaAdminPinModal(self._m, pin, parent=self)

        self._admin_panel = KolomnaAdminPanel(self._m, self._prefs, parent=self)

        self._admin_pin.pin_accepted.connect(self._admin_panel.show_modal)

        self._admin_panel.prefs_changed.connect(self._on_prefs_changed)



        catalog.updated.connect(self._refresh_hub)

        cart.changed.connect(self._refresh_cart)

        self._refresh_hub()

        self._refresh_cart()



    def showEvent(self, event) -> None:  # noqa: N802

        super().showEvent(event)

        self._refresh_cart()



    def _on_lang_changed(self, lang: str) -> None:
        pass

    def retranslate(self) -> None:
        self._bar.retranslate()
        self._refresh_hub()
        self._refresh_cart()
        self._info_modal.retranslate()
        if hasattr(self._admin_pin, "retranslate"):
            self._admin_pin.retranslate()
        if hasattr(self._admin_panel, "retranslate"):
            self._admin_panel.retranslate()



    def _open_info(self) -> None:

        self._info_modal.set_hours(self._prefs.hours)

        self._info_modal.show_modal()



    def _open_admin_pin(self) -> None:

        self._admin_pin.show_modal()



    def _on_prefs_changed(self, prefs: KolomnaPrefs) -> None:

        self._prefs = prefs

        self._info_modal.set_hours(prefs.hours)

        self.prefs_changed.emit(prefs)



    def _refresh_cart(self) -> None:

        count = self._cart.positions_count

        total = self._cart.total_display()

        if count > 0:

            self._footbar.set_primary(f"{S.CART} · {count}", sum_text=total)

            self._footbar.show()

        else:

            self._footbar.hide()



    def _refresh_hub(self) -> None:

        tiles = self._catalog.kolomna_hub_tiles()

        if tiles:

            self._grid.set_tiles(tiles)



    def resizeEvent(self, event) -> None:  # noqa: N802

        super().resizeEvent(event)

        for modal in (self._info_modal, self._admin_pin, self._admin_panel):

            if modal.isVisible():

                modal.setGeometry(0, 0, self.width(), self.height())


