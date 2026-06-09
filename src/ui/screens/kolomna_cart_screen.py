from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from src.core.cart import Cart
from src.core.config import Settings
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import n_items_label
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, scale
from src.ui.screens.base_screen import BaseScreen
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.widgets.kolomna_cart_footbar import KolomnaCartFootBar
from src.ui.widgets.kolomna_cart_row import KolomnaCartRow
from src.ui.widgets.kolomna_logo import LogoDrop
from src.ui.widgets.kolomna_topbar import KolomnaTopBar


class KolomnaCartScreen(BaseScreen):
    continue_shopping = pyqtSignal()
    pay = pyqtSignal()

    def __init__(self, cart: Cart, settings: Settings) -> None:
        super().__init__()
        self._cart = cart
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)

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

    def _rebuild(self) -> None:
        while self._list.count():
            item = self._list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        lines = self._cart.lines
        if not lines:
            empty = QWidget()
            el = QVBoxLayout(empty)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.setSpacing(scale(26, self._m.width))
            logo = LogoDrop(scale(260, self._m.width), scale(122, self._m.width))
            logo.setStyleSheet("background: transparent; opacity: 0.9;")
            el.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
            title = QLabel(S.CART_EMPTY)
            title.setFont(kolomna_font(self._m.fs_h2, QFont.Weight.Black))
            title.setStyleSheet(f"color: {GREEN}; background: transparent;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub = QLabel(S.CART_EMPTY_SUB)
            sub.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Medium))
            sub.setStyleSheet(f"color: {INK_60}; background: transparent;")
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn = QPushButton(S.TO_MENU)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(self._m.footbar_btn_h)
            btn.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Black))
            btn.setStyleSheet(
                f"QPushButton {{ background: {GREEN}; color: {CREAM}; border: none; "
                f"border-radius: 999px; padding: 0 {scale(48, self._m.width)}px; }}"
            )
            btn.clicked.connect(self.continue_shopping.emit)
            el.addWidget(title)
            el.addWidget(sub)
            el.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            self._list.addStretch(1)
            self._list.addWidget(empty)
            self._list.addStretch(1)
            self._footbar.hide()
            return

        for line in lines:
            row = KolomnaCartRow(line, self._m)
            pid = line.product.id
            row.quantity_changed.connect(lambda p, v: self._cart.set_quantity(p, v))
            row.remove_clicked.connect(self._cart.remove)
            self._list.addWidget(row)

        self._list.addStretch(1)
        label = f"{S.TOTAL} · {n_items_label(self._cart.item_count)}"
        self._footbar.set_labels(label, self._cart.total_rub, S.KEEP_SHOPPING, S.CHECKOUT)
        self._footbar.show()

    def retranslate(self) -> None:
        self._top.set_title(S.CART_TITLE, accent=GREEN)
        self._top.retranslate()
        self._rebuild()
