from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.core.cart import Cart
from src.core.config import Settings
from src.services.catalog_sync import CatalogStore
from src.ui import kolomna_strings as S
from src.ui.kolomna_cta import cta_palette
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import n_items_label
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, scale
from src.ui.screens.base_screen import BaseScreen
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.widgets.kolomna_cart_footbar import KolomnaCartFootBar
from src.ui.widgets.kolomna_cart_row import KolomnaCartRow
from src.ui.widgets.kolomna_logo import BerryDrop
from src.ui.widgets.kolomna_topbar import KolomnaTopBar


class _CartEmptyMenuBtn(QWidget):
    """btn btn--primary btn--lg — «В меню» (цвет из ctaColor, как в референсе)."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, text: str, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._text = text
        self._pressed = False
        w = metrics.width
        self._h = scale(104, w)
        self._pad_x = scale(56, w)
        self._font = kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold)
        fm = QFontMetrics(self._font)
        self.setFixedHeight(self._h)
        self.setMinimumWidth(fm.horizontalAdvance(text) + self._pad_x * 2)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(1, 1, self.width() - 2, self._h - 2)
        r = rect.height() / 2.0
        pal = cta_palette()
        bg = QColor(pal.bg_active if self._pressed else pal.bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, r, r)
        p.setFont(self._font)
        p.setPen(QColor(pal.fg))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._text)
        p.end()

    def refresh_cta(self) -> None:
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class KolomnaCartScreen(BaseScreen):
    continue_shopping = pyqtSignal()
    pay = pyqtSignal()

    def __init__(self, cart: Cart, catalog: CatalogStore, settings: Settings) -> None:
        super().__init__()
        self._cart = cart
        self._catalog = catalog
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)
        self._empty_panel: QWidget | None = None

        self.setObjectName("KolomnaCartScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top = KolomnaTopBar(self._m, show_back=True, show_lang=True)
        self._top.set_title(S.CART_TITLE, accent=GREEN)
        self._top.back_clicked.connect(self.continue_shopping.emit)
        self._layout.addWidget(self._top)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {CREAM}; }}")
        enable_kinetic_scroll(self._scroll)

        self._host = QWidget()
        self._host.setStyleSheet(f"background: {CREAM};")
        self._list = QVBoxLayout(self._host)
        self._list.setContentsMargins(self._m.pad, self._m.pad, self._m.pad, self._m.pad)
        self._list.setSpacing(scale(20, self._m.width))
        self._scroll.setWidget(self._host)
        self._layout.addWidget(self._scroll, stretch=1)

        self._footbar = KolomnaCartFootBar(self._m)
        self._footbar.hide()
        self._footbar.checkout_clicked.connect(self.pay.emit)
        self._footbar.keep_shopping_clicked.connect(self.continue_shopping.emit)
        self._layout.addWidget(self._footbar)

        cart.changed.connect(self._rebuild)
        catalog.updated.connect(self._rebuild)
        self._rebuild()

    def _viewport_main_height(self) -> int:
        return max(1, self._scroll.viewport().height())

    def _sync_empty_height(self) -> None:
        if self._empty_panel is None:
            return
        vh = self._viewport_main_height()
        self._host.setMinimumHeight(vh)
        self._empty_panel.setMinimumHeight(vh)

    def _build_empty_panel(self) -> QWidget:
        """cart-empty: центр экрана, кремовая капля, t-h2 + t-lead, btn--primary btn--lg."""
        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(panel)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(scale(26, self._m.width))

        drop_w = scale(260, self._m.width)
        drop_h = scale(122, self._m.width)
        drop = BerryDrop(
            drop_w,
            drop_h,
            fill=CREAM_DEEP,
            edge=CREAM_DEEP,
            opacity=0.9,
        )
        lay.addWidget(drop, alignment=Qt.AlignmentFlag.AlignHCenter)

        title = QLabel(S.CART_EMPTY)
        title.setFont(kolomna_font(self._m.fs_h2, QFont.Weight.ExtraBold))
        title.setStyleSheet(f"color: {GREEN}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        sub = QLabel(S.CART_EMPTY_SUB)
        sub.setFont(kolomna_font(self._m.fs_lead, QFont.Weight.Medium))
        sub.setStyleSheet(f"color: {INK_60}; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)

        btn = _CartEmptyMenuBtn(self._m, S.TO_MENU)
        btn.clicked.connect(self.continue_shopping.emit)
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        return panel

    def _rebuild(self) -> None:
        self._cart.sync_products_from_catalog(self._catalog)
        while self._list.count():
            item = self._list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._empty_panel = None

        lines = self._cart.lines
        if not lines:
            self._list.setContentsMargins(0, 0, 0, 0)
            self._empty_panel = self._build_empty_panel()
            self._list.addWidget(self._empty_panel, 1)
            self._footbar.hide()
            QTimer.singleShot(0, self._sync_empty_height)
            return

        self._list.setContentsMargins(self._m.pad, self._m.pad, self._m.pad, self._m.pad)
        self._host.setMinimumHeight(0)
        for line in lines:
            row = KolomnaCartRow(line, self._m)
            row.quantity_changed.connect(lambda p, v: self._cart.set_quantity(p, v))
            row.remove_clicked.connect(self._cart.remove)
            self._list.addWidget(row)

        self._list.addStretch(1)
        label = f"{S.TOTAL} · {n_items_label(self._cart.item_count)}"
        self._footbar.set_labels(label, self._cart.total_rub, S.KEEP_SHOPPING, S.CHECKOUT)
        self._footbar.show()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        QTimer.singleShot(0, self._sync_empty_height)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._empty_panel is not None:
            self._sync_empty_height()

    def retranslate(self) -> None:
        self._top.set_title(S.CART_TITLE, accent=GREEN)
        self._top.retranslate()
        self._rebuild()
