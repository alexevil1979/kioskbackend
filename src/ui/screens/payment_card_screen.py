from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import danger_button


class PaymentCardScreen(BaseScreen):
    cancel = pyqtSignal()
    completed = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._title = QLabel("Оплата картой")
        self._title.setObjectName("ScreenTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title)

        self._hint = QLabel(
            "Следуйте инструкции на терминале,\n"
            "приложите карту или телефон"
        )
        self._hint.setStyleSheet("font-size:28px;color:#2C2416;")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._hint)

        self._status = QLabel("Ожидание терминала…")
        self._status.setObjectName("Subtitle")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status)

        btn_cancel = danger_button("Отмена")
        btn_cancel.clicked.connect(self.cancel.emit)
        layout.addWidget(btn_cancel, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()
        self._layout.addLayout(layout)
        self._layout.addStretch()

        # Mock: автозавершение через 5 сек в dev
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
