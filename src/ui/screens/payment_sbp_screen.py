from __future__ import annotations

from io import BytesIO

import qrcode
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout

from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import danger_button


class PaymentSbpScreen(BaseScreen):
    cancel = pyqtSignal()
    paid = pyqtSignal()
    failed = pyqtSignal()

    def __init__(self, timeout_sec: int = 120) -> None:
        super().__init__()
        self._timeout_sec = timeout_sec
        self._remaining = timeout_sec
        self._payment_id = ""

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Оплата по СБП")
        title.setObjectName("ScreenTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._qr_label = QLabel()
        self._qr_label.setFixedSize(400, 400)
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._qr_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self._timer_label = QLabel()
        self._timer_label.setStyleSheet("font-size:24px;")
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._timer_label)

        hint = QLabel("Отсканируйте QR в приложении банка")
        hint.setObjectName("Subtitle")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        btn_cancel = danger_button("Отмена")
        btn_cancel.clicked.connect(self.cancel.emit)
        layout.addWidget(btn_cancel, alignment=Qt.AlignmentFlag.AlignCenter)

        self._layout.addStretch()
        self._layout.addLayout(layout)
        self._layout.addStretch()

        self._countdown = QTimer(self)
        self._countdown.timeout.connect(self._tick)

    def start_payment(self, qr_payload: str, payment_id: str) -> None:
        self._payment_id = payment_id
        self._remaining = self._timeout_sec
        self._show_qr(qr_payload)
        self._update_timer_label()
        self._countdown.start(1000)

    def stop(self) -> None:
        self._countdown.stop()

    def _show_qr(self, payload: str) -> None:
        img = qrcode.make(payload)
        buf = BytesIO()
        img.save(buf, format="PNG")
        qimg = QImage.fromData(buf.getvalue())
        self._qr_label.setPixmap(QPixmap.fromImage(qimg).scaled(380, 380, Qt.AspectRatioMode.KeepAspectRatio))

    def _tick(self) -> None:
        self._remaining -= 1
        self._update_timer_label()
        if self._remaining <= 0:
            self._countdown.stop()
            self.failed.emit()

    def _update_timer_label(self) -> None:
        m, s = divmod(max(0, self._remaining), 60)
        self._timer_label.setText(f"Ожидание оплаты: {m:02d}:{s:02d}")
