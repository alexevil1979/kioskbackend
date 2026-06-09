from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from src.ui.widgets.buttons import primary_button


class CartBottomBar(QFrame):
    """Нижняя панель: корзина + CTA (стиль Kolomna footbar)."""

    go_cart = pyqtSignal()

    def __init__(self, *, compact: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BottomBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "QFrame#BottomBar{background:#F6EFD8;border:none;border-top:2px solid #ECE0BC;}"
            "QLabel#BottomBarText{color:#1F4D2A;font-family:'Montserrat',ui-sans-serif,system-ui,sans-serif;"
            "font-size:16px;font-weight:800;background:transparent;}"
            "QPushButton#CheckoutBtn{background:#1F4D2A;color:#F6EFD8;border:none;border-radius:999px;"
            "font-family:'Montserrat',ui-sans-serif,system-ui,sans-serif;font-size:13px;font-weight:800;"
            "padding:0 26px;min-height:48px;max-height:48px;min-width:178px;}"
            "QPushButton#CheckoutBtn:pressed{background:#143821;}"
            "QPushButton#CheckoutBtn:disabled{background:#1F4D2A;color:#F6EFD8;opacity:0.45;}"
        )

        layout = QHBoxLayout(self)
        pad_h = 16 if compact else 24
        layout.setContentsMargins(pad_h, 10, pad_h, 10)
        layout.setSpacing(12)

        self._summary = QLabel()
        self._summary.setObjectName("BottomBarText")
        self._summary.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self._summary, stretch=1)

        self._btn_checkout = primary_button("Оформить")
        self._btn_checkout.setObjectName("CheckoutBtn")
        self._btn_checkout.setText("Корзина")
        self._btn_checkout.clicked.connect(self.go_cart.emit)
        layout.addWidget(self._btn_checkout)

    def update_summary(self, item_count: int, total: str) -> None:
        self._summary.setText(
            f'Корзина: <span style="font-weight:900;">{item_count}</span>'
            f" · <span style=\"font-weight:900;\">{total}</span>"
        )
        self._btn_checkout.setEnabled(item_count > 0)
