from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.payment_flow_styles import (
    add_payment_row,
    apply_payment_screen,
    layout_margins,
    mount_centered_content,
    style_icon,
    style_primary_button,
    style_secondary_button,
    style_subtitle,
    style_title,
)
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import primary_button, secondary_button


class PaymentErrorScreen(BaseScreen):
    retry = pyqtSignal()
    to_menu = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        apply_payment_screen(self)
        self._layout.setContentsMargins(*layout_margins())
        self._layout.setSpacing(12)

        self._default_message = (
            "Попробуйте ещё раз или выберите другой способ оплаты."
        )
        self._msg_label: QLabel | None = None
        self._build(
            "Оплата не прошла",
            self._default_message,
            show_retry=True,
        )

    def set_message(self, message: str | None = None) -> None:
        if self._msg_label is not None:
            self._msg_label.setText(message or self._default_message)

    def _build(self, title_text: str, message: str, *, show_retry: bool) -> None:
        layout = QVBoxLayout()

        icon = QLabel("!")
        style_icon(icon, ok=False)
        add_payment_row(layout, icon)

        title = QLabel(title_text)
        style_title(title, error=True)
        add_payment_row(layout, title)

        msg = QLabel(message)
        style_subtitle(msg)
        self._msg_label = msg
        add_payment_row(layout, msg)

        layout.addSpacing(8)

        if show_retry:
            btn_retry = primary_button("Попробовать снова")
            style_primary_button(btn_retry)
            btn_retry.clicked.connect(self.retry.emit)
            add_payment_row(layout, btn_retry)

        btn_menu = secondary_button("В главное меню")
        style_secondary_button(btn_menu)
        btn_menu.clicked.connect(self.to_menu.emit)
        add_payment_row(layout, btn_menu)

        mount_centered_content(self._layout, layout)


class OfflineScreen(BaseScreen):
    retry = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        apply_payment_screen(self)
        self._layout.setContentsMargins(*layout_margins())
        self._layout.setSpacing(12)

        layout = QVBoxLayout()

        icon = QLabel("◎")
        style_icon(icon, ok=False)
        add_payment_row(layout, icon)

        title = QLabel("Нет связи")
        style_title(title, error=True)
        add_payment_row(layout, title)

        msg = QLabel(
            "Оплата временно недоступна.\nПроверьте подключение к интернету."
        )
        style_subtitle(msg)
        add_payment_row(layout, msg)

        layout.addSpacing(8)

        btn = primary_button("Повторить")
        style_primary_button(btn)
        btn.clicked.connect(self.retry.emit)
        add_payment_row(layout, btn)

        mount_centered_content(self._layout, layout)
