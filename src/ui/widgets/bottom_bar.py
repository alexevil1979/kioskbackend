from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from src.ui.widgets.buttons import primary_button


class CartBottomBar(QFrame):
    """Нижняя панель как в mini app: корзина + «Оформить»."""

    go_cart = pyqtSignal()

    def __init__(self, *, compact: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BottomBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "QFrame#BottomBar{background:#0B0F17;border:none;}"
            "QLabel#BottomBarText{color:#FFFFFF;font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
            "font-size:16px;font-weight:600;background:transparent;}"
            "QPushButton#CheckoutBtn{background:#35C46A;color:#051B0D;border:none;border-radius:16px;"
            "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;font-size:12px;font-weight:700;"
            "text-transform:uppercase;padding:0 26px;min-height:48px;max-height:48px;min-width:178px;}"
            "QPushButton#CheckoutBtn:pressed{background:#2FB05E;}"
            "QPushButton#CheckoutBtn:disabled{background:#35C46A;color:#051B0D;opacity:0.45;}"
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
        self._btn_checkout.setText("ОФОРМИТЬ")
        self._btn_checkout.clicked.connect(self.go_cart.emit)
        layout.addWidget(self._btn_checkout)

    def update_summary(self, item_count: int, total: str) -> None:
        self._summary.setText(
            'Корзина: '
            f'<span style="color:#3CB85D;font-family:Unbounded,ui-sans-serif,system-ui,sans-serif;'
            f'font-size:17px;font-weight:700;">{item_count}</span>'
            " · "
            f'<span style="color:#3CB85D;font-family:Unbounded,ui-sans-serif,system-ui,sans-serif;'
            f'font-size:17px;font-weight:700;">{total}</span>'
        )
        self._btn_checkout.setEnabled(item_count > 0)
