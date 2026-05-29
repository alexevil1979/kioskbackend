from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.product import Product
from src.ui.widgets.buttons import primary_button


class ProductCard(QFrame):
    add_clicked = pyqtSignal(str)
    quantity_changed = pyqtSignal(str, int)

    def __init__(self, product: Product, qty: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ProductCard")
        self._product = product
        self._qty = qty

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        self._photo = QLabel()
        self._photo.setFixedHeight(140)
        self._photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._photo.setStyleSheet("background:#E8E0D0;border-radius:12px;")
        self._load_image()
        layout.addWidget(self._photo)

        name = QLabel(product.name)
        name.setObjectName("ProductName")
        name.setWordWrap(True)
        layout.addWidget(name)

        price = QLabel(product.price_display)
        price.setObjectName("ProductPrice")
        layout.addWidget(price)

        if not product.in_stock:
            oos = QLabel("Нет в наличии")
            oos.setObjectName("OutOfStock")
            layout.addWidget(oos)
            self.setEnabled(False)
            return

        self._qty_row = QHBoxLayout()
        self._btn_minus = QPushButton("−")
        self._btn_minus.setFixedSize(52, 52)
        self._btn_minus.setObjectName("OutlineBtn")
        self._btn_minus.clicked.connect(self._dec)

        self._lbl_qty = QLabel(str(qty))
        self._lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_qty.setMinimumWidth(40)
        self._lbl_qty.setStyleSheet("font-size:22px;font-weight:700;")

        self._btn_plus = QPushButton("+")
        self._btn_plus.setFixedSize(52, 52)
        self._btn_plus.setObjectName("OutlineBtn")
        self._btn_plus.clicked.connect(self._inc)

        self._qty_row.addWidget(self._btn_minus)
        self._qty_row.addWidget(self._lbl_qty)
        self._qty_row.addWidget(self._btn_plus)
        layout.addLayout(self._qty_row)

        self._btn_add = primary_button("Добавить")
        self._btn_add.clicked.connect(lambda: self.add_clicked.emit(product.id))
        layout.addWidget(self._btn_add)

        self._update_qty_ui()

    def _load_image(self) -> None:
        path = self._product.image_local
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                self._photo.setPixmap(
                    pix.scaled(
                        200,
                        130,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                return
        self._photo.setText("🌿")

    def set_quantity(self, qty: int) -> None:
        self._qty = qty
        self._update_qty_ui()

    def _update_qty_ui(self) -> None:
        if not self._product.in_stock:
            return
        self._lbl_qty.setText(str(self._qty))
        visible = self._qty > 0
        self._btn_minus.setVisible(visible)
        self._lbl_qty.setVisible(visible)
        self._btn_add.setVisible(self._qty == 0)

    def _inc(self) -> None:
        if self._qty < self._product.stock:
            self.quantity_changed.emit(self._product.id, self._qty + 1)

    def _dec(self) -> None:
        if self._qty > 0:
            self.quantity_changed.emit(self._product.id, self._qty - 1)
