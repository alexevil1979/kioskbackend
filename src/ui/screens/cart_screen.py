from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal

from src.ui.image_utils import load_pixmap, scale_pixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from src.core.cart import Cart, CartLine
from src.core.config import Settings
from src.ui.layout_metrics import LayoutMetrics
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import danger_button, outline_button, primary_button, secondary_button


class CartScreen(BaseScreen):
    continue_shopping = pyqtSignal()
    pay = pyqtSignal()

    def __init__(self, cart: Cart, settings: Settings | None = None) -> None:
        super().__init__()
        self._cart = cart
        self._portrait = (
            LayoutMetrics.from_app_config(settings.app).is_portrait if settings else False
        )

        title = QLabel("Корзина")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter if self._portrait else Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._list_host = QWidget()
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setSpacing(12)
        scroll.setWidget(self._list_host)
        self._layout.addWidget(scroll, stretch=1)

        self._total_label = QLabel()
        fs = 36 if self._portrait else 32
        self._total_label.setStyleSheet(
            f"font-size:{fs}px;font-weight:700;color:#2D5016;"
        )
        self._total_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter if self._portrait else Qt.AlignmentFlag.AlignLeft
        )
        self._layout.addWidget(self._total_label)

        if self._portrait:
            self._btn_pay = primary_button("Оплатить")
            self._btn_pay.setMinimumHeight(80)
            self._btn_pay.clicked.connect(self.pay.emit)
            self._layout.addWidget(self._btn_pay)
            btn_back = secondary_button("Продолжить выбор")
            btn_back.setMinimumHeight(64)
            btn_back.clicked.connect(self.continue_shopping.emit)
            self._layout.addWidget(btn_back)
        else:
            actions = QHBoxLayout()
            btn_back = secondary_button("Продолжить выбор")
            btn_back.clicked.connect(self.continue_shopping.emit)
            actions.addWidget(btn_back)
            self._btn_pay = primary_button("Оплатить")
            self._btn_pay.setMinimumWidth(280)
            self._btn_pay.clicked.connect(self.pay.emit)
            actions.addWidget(self._btn_pay)
            self._layout.addLayout(actions)

        cart.changed.connect(self._rebuild)

    def _rebuild(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for line in self._cart.lines:
            self._list_layout.addWidget(self._row_widget(line))

        if not self._cart.lines:
            empty = QLabel("Корзина пуста")
            empty.setObjectName("Subtitle")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)

        self._total_label.setText(f"Итого: {self._cart.total_display()}")
        self._btn_pay.setEnabled(self._cart.positions_count > 0)

    def _row_widget(self, line: CartLine) -> QFrame:
        frame = QFrame()
        frame.setObjectName("CartRow")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        if line.product.image_local:
            pix = load_pixmap(line.product.image_local)
            if not pix.isNull():
                thumb = QLabel()
                thumb.setFixedSize(88, 88)
                thumb.setPixmap(scale_pixmap(pix, 84, 84))
                thumb.setStyleSheet("border-radius:12px;")
                layout.addWidget(thumb)

        info = QVBoxLayout()
        name = QLabel(line.product.name)
        name.setStyleSheet("font-size:22px;font-weight:600;")
        info.addWidget(name)
        unit_price = QLabel(f"{line.product.price_display} / {line.product.unit}")
        unit_price.setStyleSheet("font-size:18px;color:#5C4A32;")
        info.addWidget(unit_price)
        layout.addLayout(info, stretch=1)

        qty_row = QHBoxLayout()
        btn_m = outline_button("−")
        btn_m.setFixedSize(48, 48)
        btn_m.clicked.connect(lambda: self._change_qty(line.product.id, line.quantity - 1))
        lbl = QLabel(str(line.quantity))
        lbl.setStyleSheet("font-size:22px;min-width:36px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_p = outline_button("+")
        btn_p.setFixedSize(48, 48)
        btn_p.clicked.connect(lambda: self._change_qty(line.product.id, line.quantity + 1))
        qty_row.addWidget(btn_m)
        qty_row.addWidget(lbl)
        qty_row.addWidget(btn_p)
        layout.addLayout(qty_row)

        line_total = QLabel(f"{line.line_total:.0f} ₽" if line.line_total == int(line.line_total) else f"{line.line_total:.2f} ₽")
        line_total.setStyleSheet("font-size:24px;font-weight:700;min-width:100px;")
        line_total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(line_total)

        btn_del = danger_button("✕")
        btn_del.setFixedSize(48, 48)
        btn_del.clicked.connect(lambda: self._cart.remove(line.product.id))
        layout.addWidget(btn_del)

        return frame

    def _change_qty(self, product_id: str, qty: int) -> None:
        if qty <= 0:
            self._cart.remove(product_id)
        else:
            self._cart.set_quantity(product_id, qty)
