from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.models.product import Product
from src.ui.image_utils import load_pixmap, scale_pixmap
from src.ui.widgets.buttons import outline_button, primary_button


class ProductCard(QFrame):
    add_clicked = pyqtSignal(str)
    quantity_changed = pyqtSignal(str, int)

    def __init__(
        self,
        product: Product,
        qty: int = 0,
        *,
        image_height: int = 140,
        portrait: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ProductCard")
        self._product = product
        self._qty = qty
        self._image_height = image_height
        self._portrait = portrait
        self._card_width = 500 if portrait else 280
        self._step_btn = 64 if portrait else 56

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 14)

        self._photo = QLabel()
        self._photo.setFixedHeight(image_height)
        self._photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._photo.setStyleSheet("background:#E8E0D0;border-radius:16px;")
        self._photo.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._load_image()
        root.addWidget(self._photo)

        name = QLabel(product.name)
        name.setObjectName("ProductName")
        name.setWordWrap(True)
        name.setAlignment(
            Qt.AlignmentFlag.AlignHCenter if portrait else Qt.AlignmentFlag.AlignLeft
        )
        root.addWidget(name)

        price = QLabel(product.price_display)
        price.setObjectName("ProductPrice")
        price.setAlignment(
            Qt.AlignmentFlag.AlignHCenter if portrait else Qt.AlignmentFlag.AlignLeft
        )
        root.addWidget(price)

        if not product.in_stock:
            oos = QLabel("Нет в наличии")
            oos.setObjectName("OutOfStock")
            oos.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(oos)
            self.setEnabled(False)
            return

        s = self._step_btn
        self._btn_minus = outline_button("−")
        self._btn_minus.setFixedSize(s, s)
        self._btn_minus.clicked.connect(self._dec)

        self._lbl_qty = QLabel(str(qty))
        self._lbl_qty.setObjectName("ProductQty")
        self._lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_qty.setFixedSize(s, s)

        self._btn_plus = outline_button("+")
        self._btn_plus.setFixedSize(s, s)
        self._btn_plus.clicked.connect(self._inc)

        self._qty_row = QHBoxLayout()
        self._qty_row.setSpacing(16 if portrait else 12)
        self._qty_row.setContentsMargins(0, 0, 0, 0)
        self._qty_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_row.addWidget(self._btn_minus)
        self._qty_row.addWidget(self._lbl_qty)
        self._qty_row.addWidget(self._btn_plus)

        self._qty_host = QWidget()
        self._qty_host.setMinimumHeight(s)
        self._qty_host.setLayout(self._qty_row)
        root.addWidget(self._qty_host)

        self._btn_add = primary_button("Добавить")
        self._btn_add.setMinimumHeight(56 if portrait else 48)
        self._btn_add.clicked.connect(lambda: self.add_clicked.emit(product.id))
        root.addWidget(self._btn_add)

        self._update_qty_ui()

    def _load_image(self) -> None:
        path = self._product.image_local
        if not path:
            self._set_placeholder()
            return
        pix = load_pixmap(path)
        if pix.isNull():
            self._set_placeholder()
            return
        w = max(120, self._card_width - 28)
        h = max(80, self._image_height - 8)
        self._photo.setPixmap(scale_pixmap(pix, w, h))
        self._photo.setStyleSheet("border-radius:16px;")

    def _set_placeholder(self) -> None:
        self._photo.setPixmap(QPixmap())
        self._photo.setText("🌿")
        self._photo.setStyleSheet(
            "background:#E8E0D0;border-radius:16px;font-size:48px;"
        )

    def set_quantity(self, qty: int) -> None:
        self._qty = qty
        self._update_qty_ui()

    def _update_qty_ui(self) -> None:
        if not self._product.in_stock:
            return
        self._lbl_qty.setText(str(self._qty))
        in_cart = self._qty > 0
        self._qty_host.setVisible(in_cart)
        self._btn_add.setVisible(not in_cart)

    def _inc(self) -> None:
        if self._qty < self._product.stock:
            self.quantity_changed.emit(self._product.id, self._qty + 1)

    def _dec(self) -> None:
        if self._qty > 0:
            self.quantity_changed.emit(self._product.id, self._qty - 1)
