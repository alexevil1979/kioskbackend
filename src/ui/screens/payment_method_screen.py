from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.payment_flow_styles import (
    add_payment_row,
    apply_payment_screen,
    layout_margins,
    mount_centered_content,
    style_amount,
    style_outline_button,
    style_primary_button,
    style_title,
)
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import outline_button, primary_button


class PaymentMethodScreen(BaseScreen):
    sbp_selected = pyqtSignal()
    card_selected = pyqtSignal()
    cancel = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        apply_payment_screen(self)
        self._layout.setContentsMargins(*layout_margins())
        self._layout.setSpacing(12)

        content = QVBoxLayout()

        title = QLabel("Оплата")
        style_title(title)
        add_payment_row(content, title)

        self._amount_label = QLabel("К оплате")
        style_amount(self._amount_label)
        add_payment_row(content, self._amount_label)

        content.addSpacing(8)

        btn_sbp = primary_button("СБП · по QR-коду")
        style_primary_button(btn_sbp)
        btn_sbp.clicked.connect(self.sbp_selected.emit)
        add_payment_row(content, btn_sbp)

        btn_card = primary_button("Банковская карта")
        style_primary_button(btn_card)
        btn_card.clicked.connect(self.card_selected.emit)
        add_payment_row(content, btn_card)

        btn_cancel = outline_button("Отмена")
        style_outline_button(btn_cancel)
        btn_cancel.clicked.connect(self.cancel.emit)
        add_payment_row(content, btn_cancel)

        mount_centered_content(self._layout, content)

    def set_amount(self, text: str) -> None:
        self._amount_label.setText(f"К оплате: {text}")
