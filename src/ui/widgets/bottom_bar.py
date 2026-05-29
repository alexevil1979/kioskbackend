from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from src.ui.widgets.buttons import primary_button, secondary_button


class CartBottomBar(QFrame):
    go_cart = pyqtSignal()
    restart = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BottomBar")
        self.setFixedHeight(100)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 12, 32, 12)

        self._summary = QLabel("Корзина: 0 позиций • 0 ₽")
        self._summary.setObjectName("BottomBarText")
        layout.addWidget(self._summary, stretch=1)

        self._btn_restart = secondary_button("Начать заново")
        self._btn_restart.clicked.connect(self.restart.emit)
        layout.addWidget(self._btn_restart)

        self._btn_cart = primary_button("В корзину")
        self._btn_cart.setMinimumWidth(220)
        self._btn_cart.clicked.connect(self.go_cart.emit)
        layout.addWidget(self._btn_cart)

    def update_summary(self, positions: int, total: str) -> None:
        word = "позиций" if positions != 1 else "позиция"
        if positions in (2, 3, 4):
            word = "позиции"
        self._summary.setText(f"Корзина: {positions} {word} • {total}")
        self._btn_cart.setEnabled(positions > 0)
