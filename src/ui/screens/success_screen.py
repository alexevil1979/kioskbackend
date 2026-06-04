from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.payment_flow_styles import (
    add_payment_row,
    apply_payment_screen,
    layout_margins,
    mount_centered_content,
    style_icon,
    style_subtitle,
    style_title,
)
from src.ui.screens.base_screen import BaseScreen


class SuccessScreen(BaseScreen):
    def __init__(self) -> None:
        super().__init__()
        apply_payment_screen(self)
        self._layout.setContentsMargins(*layout_margins())
        self._layout.setSpacing(12)

        layout = QVBoxLayout()

        icon = QLabel("✓")
        style_icon(icon, ok=True)
        add_payment_row(layout, icon)

        title = QLabel("Спасибо! Заберите чек.")
        style_title(title)
        add_payment_row(layout, title)

        self._countdown = QLabel("Возврат в меню через несколько секунд…")
        style_subtitle(self._countdown)
        add_payment_row(layout, self._countdown)

        mount_centered_content(self._layout, layout)

    def set_countdown_text(self, text: str) -> None:
        self._countdown.setText(text)
