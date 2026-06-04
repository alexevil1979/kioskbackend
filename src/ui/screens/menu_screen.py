from __future__ import annotations

from PyQt6.QtCore import QEvent, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QPainterPath, QRegion
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.core.cart import Cart
from src.core.config import Settings
from src.services.catalog_sync import CatalogStore
from src.ui.layout_metrics import LayoutMetrics
from src.ui.katusha_hub_catalog import MISC_HUB_ID, MISC_TITLE
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.bottom_bar import CartBottomBar
from src.ui.widgets.product_card import ProductCard


_HEADER_TITLE_STYLE = (
    "color:#121D2E;background:transparent;"
    "font-family:'Unbounded','Inter',ui-sans-serif,sans-serif;"
    "font-size:13px;font-weight:700;"
)
_HEADER_COUNT_STYLE = (
    "color:#A0A8B4;background:transparent;"
    "font-family:'Inter',ui-sans-serif,sans-serif;"
    "font-size:11px;font-weight:700;"
)


def _positions_label(count: int) -> str:
    n = count
    if n % 10 == 1 and n % 100 != 11:
        word = "позиция"
    elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        word = "позиции"
    else:
        word = "позиций"
    return f"{n} {word}"


class CollapsibleSelect(QFrame):
    def __init__(self, title: str, options: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CatalogSelect")
        self._expanded = False
        self._selected = options[0] if options else title
        self._options: list[str] = options[:]

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._head = QFrame()
        self._head.setObjectName("CatalogSelectHead")
        self._head.setCursor(Qt.CursorShape.PointingHandCursor)
        head_lay = QHBoxLayout(self._head)
        head_lay.setContentsMargins(14, 0, 14, 0)
        head_lay.setSpacing(8)
        self._head_text = QLabel()
        self._head_text.setObjectName("CatalogSelectHeadText")
        self._head_arrow = QLabel("⌄")
        self._head_arrow.setObjectName("CatalogSelectHeadArrow")
        self._head_arrow.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        head_lay.addWidget(self._head_text, stretch=1)
        head_lay.addWidget(self._head_arrow)
        lay.addWidget(self._head)

        self._popup: QWidget | None = None
        self._body_lay: QVBoxLayout | None = None

        self.set_options(options or [title])

    @property
    def value(self) -> str:
        return self._selected

    def set_options(self, options: list[str]) -> None:
        self._options = options[:]
        if not self._options:
            self._options = [self._selected]
        if self._selected not in self._options:
            self._selected = self._options[0]
        self._rebuild_popup()
        self._sync_head()

    def _sync_head(self) -> None:
        self._head_text.setText(self._selected.upper())
        self._head_arrow.setText("⌃" if self._expanded else "⌄")

    def _choose(self, text: str) -> None:
        self._selected = text
        self._collapse()
        self._sync_head()

    def _toggle(self) -> None:
        if self._expanded:
            self._collapse()
        else:
            self._expand()
        self._sync_head()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            if self._head.geometry().contains(event.position().toPoint()):
                self._toggle()
        super().mouseReleaseEvent(event)

    def _rebuild_popup(self) -> None:
        if self._popup is None:
            return
        if self._body_lay is None:
            return
        while self._body_lay.count():
            item = self._body_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for text in self._options:
            btn = QPushButton(text.upper())
            btn.setObjectName("CatalogSelectOption")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda _checked=False, t=text: self._choose(t))
            self._body_lay.addWidget(btn)

    def _ensure_popup(self) -> None:
        if self._popup is not None:
            return
        host = self.window()
        popup = QWidget(host)
        popup.setObjectName("CatalogSelectBody")
        popup.setWindowFlag(Qt.WindowType.Widget, True)
        popup.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        popup.hide()
        lay = QVBoxLayout(popup)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._popup = popup
        self._body_lay = lay
        self._rebuild_popup()

    def _expand(self) -> None:
        self._ensure_popup()
        if self._popup is None:
            return
        host = self.window()
        top_left = self.mapTo(host, QPoint(0, self.height() + 4))
        option_h = 40
        popup_h = option_h * max(1, len(self._options))
        self._popup.setGeometry(top_left.x(), top_left.y(), self.width(), popup_h)
        self._popup.raise_()
        self._popup.show()
        self._expanded = True
        self._sync_head()
        self.window().installEventFilter(self)

    def _collapse(self) -> None:
        self._expanded = False
        if self._popup is not None:
            self._popup.hide()
        self._sync_head()
        self.window().removeEventFilter(self)

    def eventFilter(self, watched, event) -> bool:  # noqa: N802
        if not self._expanded or self._popup is None:
            return False
        if watched is self.window() and event.type() == QEvent.Type.MouseButtonPress:
            pos = event.position().toPoint()
            in_head = self._head.geometry().contains(self.mapFrom(self.window(), pos))
            in_popup = self._popup.geometry().contains(pos)
            if not in_head and not in_popup:
                self._collapse()
        if watched is self.window() and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Move,
        ):
            self._collapse()
        return False


class MenuScreen(BaseScreen):
    go_cart = pyqtSignal()
    back_to_categories = pyqtSignal()

    def __init__(self, catalog: CatalogStore, cart: Cart, settings: Settings) -> None:
        super().__init__()
        self.setObjectName("MenuScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget#MenuScreen { background:#FFFFFF; }")
        self._catalog = catalog
        self._cart = cart
        self._settings = settings
        self._metrics = LayoutMetrics.from_app_config(settings.app)
        self._current_category: str | None = None
        self._current_hub: str | None = None
        self._cards: dict[str, ProductCard] = {}
        self._row_heights: list[int] = []

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._header = QFrame()
        self._header.setObjectName("CategoryCatalogHeader")
        head_lay = QVBoxLayout(self._header)
        head_lay.setContentsMargins(4, 12, 4, 10)
        head_lay.setSpacing(10)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        btn_back = QPushButton("‹")
        btn_back.setObjectName("CategoryBackBtn")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_back.clicked.connect(self.back_to_categories.emit)
        self._title = QLabel("")
        self._title.setObjectName("CategoryHeaderTitle")
        self._count = QLabel("")
        self._count.setObjectName("CategoryHeaderCount")
        top.addWidget(btn_back)
        top.addWidget(self._title, stretch=1)
        top.addWidget(self._count)
        head_lay.addLayout(top)

        search = QFrame()
        search.setObjectName("CategorySearchBar")
        search_lay = QHBoxLayout(search)
        search_lay.setContentsMargins(14, 0, 14, 0)
        search_lay.setSpacing(8)
        icon = QLabel("⌕")
        icon.setObjectName("CategorySearchIcon")
        ph = QLabel("Поиск в категории...")
        ph.setObjectName("CategorySearchPlaceholder")
        search_lay.addWidget(icon)
        search_lay.addWidget(ph, stretch=1)
        head_lay.addWidget(search)
        self._layout.addWidget(self._header)

        self._filters = QFrame()
        self._filters.setObjectName("CatalogFilters")
        filters_lay = QVBoxLayout(self._filters)
        filters_lay.setContentsMargins(4, 12, 4, 12)
        filters_lay.setSpacing(8)
        self._producer_select = CollapsibleSelect(
            "Все производители",
            ["Все производители", "Питомник «Loveberry»"],
        )
        self._sort_select = CollapsibleSelect(
            "Сначала новые",
            ["Сначала новые", "Доступные к продаже"],
        )
        filters_lay.addWidget(self._producer_select)
        filters_lay.addWidget(self._sort_select)
        self._layout.addWidget(self._filters)

        self._scroll = QScrollArea()
        self._scroll.setObjectName("MenuProductsScroll")
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet(
            "QScrollArea#MenuProductsScroll { border:none; background:#FFFFFF; }"
        )
        vp = self._scroll.viewport()
        vp.setStyleSheet("background:#FFFFFF;")
        vp.setAutoFillBackground(True)
        enable_kinetic_scroll(self._scroll)

        self._grid_host = QWidget()
        self._grid_host.setObjectName("MenuProductsGridHost")
        self._grid_pad = (8, 8, 8, 16)
        self._scroll.setWidget(self._grid_host)
        self._layout.addWidget(self._scroll, stretch=1)

        self._bottom = CartBottomBar(compact=self._metrics.phone_layout)
        self._bottom.setFixedHeight(self._metrics.bottom_bar_height)
        self._bottom.go_cart.connect(self.go_cart.emit)
        self._layout.addWidget(self._bottom)

        catalog.updated.connect(self._rebuild_categories)
        cart.changed.connect(self._refresh_cart_ui)
        self._rebuild_categories()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._scroll_to_top()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._cards and self._row_heights:
            self._sync_grid_host_size(self._row_heights)

    def _scroll_to_top(self) -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.minimum())

    def _grid_metrics(self) -> tuple[int, int, int, int, int, int]:
        """cols, card_w, card_h, gap, pad_l, pad_t."""
        cols = self._metrics.product_grid_columns
        card_w = self._metrics.product_image_size
        card_h = ProductCard.card_height_for(
            card_w, phone_layout=self._metrics.phone_layout
        )
        gap = self._metrics.grid_gap
        pad_l, pad_t, _pad_r, _pad_b = self._grid_pad
        return cols, card_w, card_h, gap, pad_l, pad_t

    def _sync_grid_host_size(self, row_heights: list[int]) -> None:
        _pad_l, pad_t, _pad_r, pad_b = self._grid_pad
        gap = self._metrics.grid_gap
        if not row_heights:
            height = pad_t + pad_b
        else:
            height = (
                pad_t
                + pad_b
                + sum(row_heights)
                + max(0, len(row_heights) - 1) * gap
            )
        width = self._scroll.viewport().width()
        if width <= 0:
            width = self._metrics.width
        self._grid_host.setFixedSize(width, height)
        self._scroll.updateGeometry()

    def _rebuild_categories(self) -> None:
        cats = self._catalog.categories
        if not cats:
            return

        if self._current_category is None and not self._current_hub:
            self._current_category = cats[0].id

        self._rebuild_products()

    def open_hub(self, hub_id: str | None) -> None:
        """Открыть товары категории-хаба (berry, honey, …)."""
        self._current_hub = str(hub_id) if hub_id is not None else None
        self._current_category = None
        self._refresh_category_header()
        self._rebuild_categories()
        self._scroll_to_top()

    def open_category(self, category_id: str | None) -> None:
        self._current_hub = None
        self._current_category = (
            str(category_id) if category_id is not None else None
        )
        self._refresh_category_header()
        self._rebuild_categories()
        self._scroll_to_top()

    def _select_category(self, category_id: str | None) -> None:
        self._current_category = category_id
        self._rebuild_products()

    def _active_list_id(self) -> str | None:
        if self._current_hub:
            return self._current_hub
        return self._current_category

    def _title_for_list(self, list_id: str | None) -> str:
        if list_id is None:
            return "ВСЕ ТОВАРЫ"
        key = str(list_id)
        if key == MISC_HUB_ID:
            return MISC_TITLE
        for cat in self._catalog.categories:
            if str(cat.id) == key:
                return cat.name.upper()
        product = next(
            (p for p in self._catalog.products if str(p.category_id) == key),
            None,
        )
        if product and product.category_name:
            return product.category_name.upper()
        return "КАТАЛОГ"

    def _refresh_category_header(self) -> None:
        list_id = self._active_list_id()
        if self._current_hub:
            products = self._catalog.products_for_hub(self._current_hub)
        else:
            products = self._catalog.products_for_category(self._current_category)
        self._update_category_header(len(products))

    def _update_category_header(self, product_count: int) -> None:
        list_id = self._active_list_id()
        title = self._title_for_list(list_id)
        self._title.setText(title)
        self._title.setToolTip(title)
        self._count.setText(_positions_label(product_count))
        self._title.update()
        self._header.update()

    def _rebuild_products(self) -> None:
        for card in self._cards.values():
            card.hide()
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()

        if self._current_hub:
            products = self._catalog.products_for_hub(self._current_hub)
        else:
            products = self._catalog.products_for_category(self._current_category)
        if self._sort_select.value.lower().startswith("доступные"):
            products = [p for p in products if p.in_stock]
        self._update_category_header(len(products))

        cols, card_w, _card_h, gap, pad_l, pad_t = self._grid_metrics()
        row_cards: list[list[ProductCard]] = []
        for i, product in enumerate(products):
            qty = self._cart.quantity_of(product.id)
            card = ProductCard(
                product,
                qty,
                image_size=card_w,
                phone_layout=self._metrics.phone_layout,
            )
            card.card_clicked.connect(self._open_product_detail)
            card.quantity_changed.connect(self._on_qty)
            self._cards[product.id] = card
            row_idx = i // cols
            while len(row_cards) <= row_idx:
                row_cards.append([])
            row_cards[row_idx].append(card)

        self._row_heights = []
        y = pad_t
        for row_idx, cards_in_row in enumerate(row_cards):
            name_slot_h = max(c.measure_name_slot_height() for c in cards_in_row)
            row_h = 0
            for card in cards_in_row:
                row_h = max(row_h, card.apply_row_layout(name_slot_h))
            self._row_heights.append(row_h)
            for col_idx, card in enumerate(cards_in_row):
                x = pad_l + col_idx * (card_w + gap)
                card.setParent(self._grid_host)
                card.setGeometry(x, y, card_w, row_h)
                card.show()
            y += row_h + gap

        self._sync_grid_host_size(self._row_heights)
        self._refresh_cart_ui()

    def _on_add(self, product_id: str) -> None:
        p = self._catalog.product_by_id(product_id)
        if p:
            self._cart.add(p, 1)
            if product_id in self._cards:
                self._cards[product_id].set_quantity(self._cart.quantity_of(product_id))

    def _open_product_detail(self, product_id: str) -> None:
        product = self._catalog.product_by_id(product_id)
        if not product:
            return
        dlg = QDialog(self)
        dlg.setObjectName("ProductDetailDialog")
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setModal(True)
        top_left = self.mapToGlobal(QPoint(0, 0))
        dlg.setGeometry(top_left.x(), top_left.y(), self.width(), self.height())
        dlg.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        root = QVBoxLayout(dlg)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        overlay = QFrame()
        overlay.setObjectName("ProductDetailOverlay")
        overlay_lay = QVBoxLayout(overlay)
        overlay_lay.setContentsMargins(0, 0, 0, 0)
        overlay_lay.setSpacing(0)

        card = QFrame()
        card.setObjectName("ProductDetailCard")
        card.setFixedSize(dlg.width(), dlg.height())
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)
        overlay_lay.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(overlay)

        hero = QFrame()
        hero.setObjectName("ProductDetailHero")
        hero_h = 365
        hero.setFixedHeight(hero_h)
        hero_grid = QGridLayout(hero)
        hero_grid.setContentsMargins(0, 0, 0, 0)

        photo = QLabel(hero)
        photo.setObjectName("ProductDetailImage")
        photo.setFixedSize(card.width(), hero_h)
        photo.setStyleSheet("border-radius: 20px;")
        if product.image_local:
            from src.ui.image_utils import load_pixmap, scale_pixmap_cover

            pix = load_pixmap(product.image_local)
            if not pix.isNull():
                photo.setPixmap(scale_pixmap_cover(pix, card.width(), hero_h))
        clip_path = QPainterPath()
        clip_path.addRoundedRect(0, 0, photo.width(), photo.height(), 20, 20)
        photo.setMask(QRegion(clip_path.toFillPolygon().toPolygon()))
        hero_grid.addWidget(photo, 0, 0)

        hero_controls = QHBoxLayout()
        hero_controls.setContentsMargins(16, 18, 16, 0)
        btn_close = QPushButton("‹")
        btn_close.setObjectName("ProductDetailRoundBtn")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_close.clicked.connect(dlg.accept)
        btn_like = QPushButton("♥")
        btn_like.setObjectName("ProductDetailLikeBtn")
        btn_like.setCheckable(True)
        btn_like.setChecked(False)
        btn_like.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_like.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        hero_controls.addWidget(btn_close)
        hero_controls.addStretch(1)
        hero_controls.addWidget(btn_like)
        hero_grid.addLayout(hero_controls, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        card_lay.addWidget(hero)

        body = QWidget()
        body.setObjectName("ProductDetailBody")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(18, 32, 18, 16)
        body_lay.setSpacing(14)

        meta = QHBoxLayout()
        meta.setContentsMargins(0, 0, 0, 0)
        meta.setSpacing(8)
        cat_name = product.category_name or self._title_for_list(product.category_id)
        category = QLabel(cat_name.upper())
        category.setObjectName("ProductDetailCategoryPill")
        category.setStyleSheet(
            "background:#35C46A;color:#FFF;border-radius:7px;padding:5px 10px;"
            "font-family:Unbounded,Segoe UI,sans-serif;font-size:10px;font-weight:700;"
        )
        article = QLabel(f"АРТ. {product.id}")
        article.setObjectName("ProductDetailArticle")
        article.setStyleSheet(
            "color:#A3AAB6;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:10px;font-weight:700;"
        )
        meta.addWidget(category)
        meta.addStretch(1)
        meta.addWidget(article)
        body_lay.addLayout(meta)

        name = QLabel(product.name)
        name.setWordWrap(True)
        name.setObjectName("ProductDetailName")
        name.setStyleSheet(
            "color:#05070B;font-family:Inter,Segoe UI,sans-serif;"
            "font-size:22px;font-weight:700;background:transparent;"
        )
        body_lay.addWidget(name)

        price_row = QHBoxLayout()
        price_row.setContentsMargins(0, 0, 0, 0)
        price_row.setSpacing(8)
        price = QLabel(product.price_display)
        price.setObjectName("ProductDetailPrice")
        price.setStyleSheet(
            "color:#05070B;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:28px;font-weight:700;font-style:italic;background:transparent;"
        )
        unit = QLabel(f"/ {product.unit}")
        unit.setObjectName("ProductDetailUnit")
        unit.setStyleSheet(
            "color:#A0A8B4;font-family:Inter,Segoe UI,sans-serif;"
            "font-size:20px;font-weight:700;background:transparent;"
        )
        price_row.addWidget(price)
        price_row.addWidget(unit)
        price_row.addStretch(1)
        body_lay.addLayout(price_row)

        details = QFrame()
        details.setObjectName("ProductDetailInfoCard")
        details.setStyleSheet("background:#FFF;border:1px solid #ECEFF3;border-radius:16px;")
        details_lay = QVBoxLayout(details)
        details_lay.setContentsMargins(16, 12, 16, 12)
        details_lay.setSpacing(10)
        details_title = QLabel("ДЕТАЛИ ТОВАРА")
        details_title.setObjectName("ProductDetailBlockTitle")
        details_title.setStyleSheet(
            "color:#A0A8B4;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:10px;font-weight:700;letter-spacing:0.04em;background:transparent;"
        )
        details_value = QLabel(f"Единица:  <b>{product.unit}</b>")
        details_value.setObjectName("ProductDetailText")
        details_value.setStyleSheet(
            "color:#344054;font-family:Inter,Segoe UI,sans-serif;"
            "font-size:13px;font-weight:600;background:transparent;"
        )
        details_lay.addWidget(details_title)
        details_lay.addWidget(details_value)
        body_lay.addWidget(details)

        producer_title = QLabel("ПРОИЗВОДИТЕЛЬ")
        producer_title.setObjectName("ProductDetailBlockTitle")
        producer_title.setStyleSheet(
            "color:#A0A8B4;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:10px;font-weight:700;letter-spacing:0.04em;background:transparent;"
        )
        body_lay.addWidget(producer_title)
        producer = QFrame()
        producer.setObjectName("ProductDetailInfoCard")
        producer.setStyleSheet("background:#FFF;border:1px solid #ECEFF3;border-radius:16px;")
        producer_lay = QHBoxLayout(producer)
        producer_lay.setContentsMargins(12, 8, 12, 8)
        producer_lay.setSpacing(8)
        producer_name = QLabel(product.producer_name or "Питомник «LoveBerry»")
        producer_name.setObjectName("ProductDetailProducer")
        producer_name.setStyleSheet(
            "color:#344054;font-family:Inter,Segoe UI,sans-serif;"
            "font-size:12px;font-weight:600;background:transparent;"
        )
        verified = QLabel("✓ ПРОВЕРЕН")
        verified.setObjectName("ProductDetailVerified")
        verified.setStyleSheet(
            "background:#35C46A;color:#FFF;border-radius:8px;padding:3px 7px;"
            "font-family:Unbounded,Segoe UI,sans-serif;font-size:8px;font-weight:700;"
        )
        verified.setFixedHeight(18)
        producer_lay.addWidget(producer_name, stretch=1)
        producer_lay.addWidget(verified, alignment=Qt.AlignmentFlag.AlignRight)
        body_lay.addWidget(producer)

        about_title = QLabel("О ПРОДУКТЕ")
        about_title.setObjectName("ProductDetailSectionTitle")
        about_title.setStyleSheet(
            "color:#A0A8B4;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:11px;font-weight:700;background:transparent;"
        )
        body_lay.addWidget(about_title)
        desc = QLabel(product.description or "Описание товара скоро появится.")
        desc.setWordWrap(True)
        desc.setObjectName("ProductDetailDescription")
        desc.setStyleSheet(
            "color:#344054;font-family:Inter,Segoe UI,sans-serif;"
            "font-size:14px;font-weight:600;background:transparent;"
        )
        body_lay.addWidget(desc)
        body_lay.addStretch(1)
        body_scroll = QScrollArea()
        body_scroll.setObjectName("ProductDetailScroll")
        body_scroll.setWidgetResizable(True)
        body_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        body_scroll.setStyleSheet(
            "QScrollArea#ProductDetailScroll { border:none; background:#FFFFFF; }"
            "QScrollArea#ProductDetailScroll QScrollBar:vertical { width:0px; margin:0; }"
            "QScrollArea#ProductDetailScroll QScrollBar::handle:vertical,"
            "QScrollArea#ProductDetailScroll QScrollBar::add-line:vertical,"
            "QScrollArea#ProductDetailScroll QScrollBar::sub-line:vertical { background:transparent; height:0px; }"
        )
        body_scroll.setWidget(body)
        card_lay.addWidget(body_scroll, stretch=1)

        bottom = QFrame()
        bottom.setObjectName("ProductDetailBottomBar")
        bottom.setFixedHeight(76)
        bottom_lay = QHBoxLayout(bottom)
        bottom_lay.setContentsMargins(8, 8, 8, 8)
        bottom_lay.setSpacing(8)
        qty = QFrame()
        qty.setObjectName("ProductDetailQty")
        qty.setFixedSize(108, 52)
        qty.setStyleSheet("background:#F4F5F7;border:none;border-radius:14px;")
        qty_lay = QHBoxLayout(qty)
        qty_lay.setContentsMargins(12, 0, 12, 0)
        qty_lay.setSpacing(16)
        qty_minus = QLabel("−")
        qty_minus.setObjectName("ProductDetailQtyBtn")
        qty_minus.setStyleSheet(
            "color:#1B2537;font-family:Inter,Segoe UI,sans-serif;"
            "font-size:22px;font-weight:500;background:transparent;"
        )
        qty_num = QLabel("1")
        qty_num.setObjectName("ProductDetailQtyNum")
        qty_num.setStyleSheet(
            "color:#111827;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:18px;font-weight:700;background:transparent;"
        )
        qty_plus = QLabel("+")
        qty_plus.setObjectName("ProductDetailQtyBtn")
        qty_plus.setStyleSheet(
            "color:#1B2537;font-family:Inter,Segoe UI,sans-serif;"
            "font-size:22px;font-weight:500;background:transparent;"
        )
        qty_lay.addWidget(qty_minus)
        qty_lay.addWidget(qty_num)
        qty_lay.addWidget(qty_plus)
        cta = QFrame()
        cta.setObjectName("ProductDetailCta")
        cta.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        cta.setFixedHeight(52)
        cta.setStyleSheet("background:#9BDEAF;border:none;border-radius:14px;")
        cta_lay = QHBoxLayout(cta)
        cta_lay.setContentsMargins(14, 0, 14, 0)
        cta_lay.setSpacing(8)
        label_text = "СКОРО"
        if self._settings.catalog.purchase_test_mode:
            label_text = "В корзину"
        cta_left = QLabel(label_text)
        cta_left.setObjectName("ProductDetailCtaText")
        cta_left.setStyleSheet(
            "color:#FFFFFF;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:12px;font-weight:700;background:transparent;"
        )
        cta_right = QLabel(product.price_display)
        cta_right.setObjectName("ProductDetailCtaText")
        cta_right.setStyleSheet(
            "color:#FFFFFF;font-family:Unbounded,Segoe UI,sans-serif;"
            "font-size:12px;font-weight:700;background:transparent;"
        )
        cta_lay.addWidget(cta_left)
        cta_lay.addStretch(1)
        cta_lay.addWidget(cta_right)
        bottom_lay.addWidget(qty)
        bottom_lay.addWidget(cta, stretch=1)

        if self._settings.catalog.purchase_test_mode:
            def _on_cta_click(event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._cart.add(product, 1)
                    self._refresh_cart_ui()
                    dlg.accept()
                return QFrame.mousePressEvent(cta, event)

            cta.mousePressEvent = _on_cta_click  # type: ignore[assignment]
        card_lay.addWidget(bottom)

        dlg.exec()

    def _on_qty(self, product_id: str, qty: int) -> None:
        if qty == 0:
            self._cart.remove(product_id)
        else:
            p = self._catalog.product_by_id(product_id)
            if p:
                current = self._cart.quantity_of(product_id)
                if current == 0:
                    self._cart.add(p, qty)
                else:
                    self._cart.set_quantity(product_id, qty)
        if product_id in self._cards:
            self._cards[product_id].set_quantity(self._cart.quantity_of(product_id))

    def _refresh_cart_ui(self) -> None:
        total_qty = sum(line.quantity for line in self._cart.lines)
        self._bottom.update_summary(total_qty, self._cart.total_display())
        for pid, card in self._cards.items():
            card.set_quantity(self._cart.quantity_of(pid))
