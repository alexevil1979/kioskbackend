from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.payment_flow_styles import (
    add_payment_row,
    apply_payment_screen,
    layout_margins,
    mount_centered_content,
    style_cancel_button,
    style_subtitle,
    style_title,
)
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import outline_button


class PaymentCardScreen(BaseScreen):
    cancel = pyqtSignal()
    completed = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        apply_payment_screen(self)
        self._layout.setContentsMargins(*layout_margins())
        self._layout.setSpacing(12)

        content = QVBoxLayout()

        self._title = QLabel("Оплата картой")
        style_title(self._title)
        add_payment_row(content, self._title)

        self._hint = QLabel(
            "Следуйте инструкции на терминале,\n"
            "приложите карту или телефон"
        )
        style_subtitle(self._hint)
        add_payment_row(content, self._hint)

        self._status = QLabel("Ожидание терминала…")
        style_subtitle(self._status)
        add_payment_row(content, self._status)

        btn_cancel = outline_button("Отмена")
        style_cancel_button(btn_cancel)
        btn_cancel.clicked.connect(self.cancel.emit)
        add_payment_row(content, btn_cancel)

        mount_centered_content(self._layout, content)

        self._mock_timer = QTimer(self)
        self._mock_timer.setSingleShot(True)
        self._mock_timer.timeout.connect(lambda: self.completed.emit(True))

    def set_instruction(self, title: str, hint: str, status: str = "") -> None:
        self._title.setText(title)
        self._hint.setText(hint)
        if status:
            self._status.setText(status)

    def start_waiting(self, *, mock_auto_success: bool = True) -> None:
        if not self._status.text():
            self._status.setText("Ожидание терминала…")
        if mock_auto_success:
            self._mock_timer.start(5000)
        else:
            self._mock_timer.stop()

    def stop(self) -> None:
        self._mock_timer.stop()
