from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout

from src.ui.payment_flow_styles import (
    QR_PLACEHOLDER_STYLE,
    add_payment_row,
    apply_payment_screen,
    layout_margins,
    make_qr_card,
    mount_centered_content,
    style_cancel_button,
    style_subtitle,
    style_timer,
    style_title,
)
from src.ui.qr_render import render_qr_pixmap
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import outline_button

logger = logging.getLogger(__name__)

QR_INNER = 268


class PaymentSbpScreen(BaseScreen):
    cancel = pyqtSignal()
    paid = pyqtSignal()
    failed = pyqtSignal()

    def __init__(self, timeout_sec: int = 120) -> None:
        super().__init__()
        self._default_timeout_sec = timeout_sec
        self._remaining = timeout_sec
        self._payment_id = ""

        apply_payment_screen(self)
        self._layout.setContentsMargins(*layout_margins())
        self._layout.setSpacing(12)

        content = QVBoxLayout()

        title = QLabel("Отсканируйте QR-код для оплаты")
        style_title(title)
        add_payment_row(content, title)

        self._qr_card = make_qr_card()
        card_layout = QVBoxLayout(self._qr_card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._qr_label = QLabel()
        self._qr_label.setFixedSize(QR_INNER, QR_INNER)
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setStyleSheet("background:transparent;")
        card_layout.addWidget(self._qr_label)
        self._qr_card.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        content.addWidget(self._qr_card, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._timer_label = QLabel()
        style_timer(self._timer_label)
        add_payment_row(content, self._timer_label)

        hint = QLabel("Отсканируйте QR в приложении банка")
        style_subtitle(hint)
        add_payment_row(content, hint)

        btn_cancel = outline_button("Отмена")
        style_cancel_button(btn_cancel)
        btn_cancel.clicked.connect(self.cancel.emit)
        add_payment_row(content, btn_cancel)

        mount_centered_content(self._layout, content)

        self._countdown = QTimer(self)
        self._countdown.timeout.connect(self._tick)

    def start_payment(
        self,
        qr_payload: str,
        payment_id: str,
        *,
        qr_image_b64: str = "",
        timeout_sec: int | None = None,
        total_rub: float = 0,
    ) -> None:
        self._payment_id = payment_id
        self._last_payload = qr_payload
        self._qr_label.setStyleSheet("background:transparent;")
        limit = timeout_sec if timeout_sec is not None else self._default_timeout_sec
        self._remaining = max(30, int(limit))

        pix = render_qr_pixmap(
            payload=qr_payload,
            image_b64=qr_image_b64,
            size=QR_INNER,
        )
        if pix is not None:
            self._qr_label.setPixmap(pix)
        else:
            self._qr_label.clear()
            self._qr_label.setText("QR не удалось\nотобразить")
            self._qr_label.setStyleSheet(QR_PLACEHOLDER_STYLE)
            logger.error("СБП: не удалось отрисовать QR (payload %s символов)", len(qr_payload or ""))

        self._update_timer_label()
        self._countdown.start(1000)

    def stop(self) -> None:
        self._countdown.stop()

    def _tick(self) -> None:
        self._remaining -= 1
        self._update_timer_label()
        if self._remaining <= 0:
            self._countdown.stop()
            self.failed.emit()

    def _update_timer_label(self) -> None:
        m, s = divmod(max(0, self._remaining), 60)
        self._timer_label.setText(f"Ожидание оплаты: {m:02d}:{s:02d}")
