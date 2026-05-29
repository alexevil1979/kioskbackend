from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from src.ui.widgets.buttons import primary_button, secondary_button


class IdleWarningOverlay(QWidget):
    stay = pyqtSignal()
    leave = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Overlay")
        self.hide()

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("DialogCard")
        card.setFixedSize(600, 320)
        card_layout = QVBoxLayout(card)

        title = QLabel("Вы ещё здесь?")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        sub = QLabel("Сессия будет сброшена через 10 секунд")
        sub.setObjectName("Subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(sub)

        btn_stay = primary_button("Да, продолжаю")
        btn_stay.clicked.connect(self._on_stay)
        card_layout.addWidget(btn_stay)

        btn_leave = secondary_button("Начать заново")
        btn_leave.clicked.connect(self.leave.emit)
        card_layout.addWidget(btn_leave)

        outer.addWidget(card)

    def _on_stay(self) -> None:
        self.hide()
        self.stay.emit()

    def show_overlay(self) -> None:
        self.setGeometry(self.parent().rect())
        self.raise_()
        self.show()
