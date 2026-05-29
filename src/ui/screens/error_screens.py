from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import primary_button, secondary_button


class PaymentErrorScreen(BaseScreen):
    retry = pyqtSignal()
    to_menu = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._build(
            "Оплата не прошла",
            "Попробуйте ещё раз или выберите другой способ оплаты.",
            show_retry=True,
        )

    def _build(self, title_text: str, message: str, *, show_retry: bool) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(title_text)
        title.setObjectName("ScreenTitle")
        title.setStyleSheet("color:#B84A3A;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        msg = QLabel(message)
        msg.setObjectName("Subtitle")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        layout.addWidget(msg)

        if show_retry:
            btn_retry = primary_button("Попробовать снова")
            btn_retry.clicked.connect(self.retry.emit)
            layout.addWidget(btn_retry, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_menu = secondary_button("В главное меню")
        btn_menu.clicked.connect(self.to_menu.emit)
        layout.addWidget(btn_menu, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()
        self._layout.addLayout(layout)
        self._layout.addStretch()


class OfflineScreen(BaseScreen):
    retry = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Нет связи")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        msg = QLabel("Оплата временно недоступна.\nПроверьте подключение к интернету.")
        msg.setObjectName("Subtitle")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        btn = primary_button("Повторить")
        btn.clicked.connect(self.retry.emit)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()
        self._layout.addLayout(layout)
        self._layout.addStretch()
