from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import outline_button, primary_button


class PaymentMethodScreen(BaseScreen):
    sbp_selected = pyqtSignal()
    card_selected = pyqtSignal()
    cancel = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Способ оплаты")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(f"К оплате")
        sub.setObjectName("Subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._amount_label = sub
        layout.addWidget(sub)

        btn_sbp = primary_button("Оплатить по СБП")
        btn_sbp.setMinimumSize(500, 120)
        btn_sbp.clicked.connect(self.sbp_selected.emit)
        layout.addWidget(btn_sbp, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_card = primary_button("Оплатить картой")
        btn_card.setMinimumSize(500, 120)
        btn_card.clicked.connect(self.card_selected.emit)
        layout.addWidget(btn_card, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_cancel = outline_button("Отмена")
        btn_cancel.clicked.connect(self.cancel.emit)
        layout.addWidget(btn_cancel, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()
        self._layout.addLayout(layout)
        self._layout.addStretch()

    def set_amount(self, text: str) -> None:
        self._amount_label.setText(f"К оплате: {text}")
