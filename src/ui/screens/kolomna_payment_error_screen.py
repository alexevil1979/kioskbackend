from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.config import Settings
from src.core.payment_error_message import CONTACT_LINE
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, GREEN, INK_60, KolomnaMetrics, STRAWBERRY, scale
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.kolomna_cart_footbar import PaySumPillBtn, _FootPillBtn


class KolomnaPaymentErrorScreen(BaseScreen):
    retry = pyqtSignal()
    go_payment = pyqtSignal()
    to_menu = pyqtSignal()

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)
        self._detail = ""
        self._phone = ""
        self._order_id = ""

        self.setObjectName("KolomnaPaymentErrorScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner = QWidget()
        inner.setMaximumWidth(scale(860, w))
        lay = QVBoxLayout(inner)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(scale(28, w))

        self._icon = QLabel("!")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setFont(kolomna_font(scale(96, w), QFont.Weight.Black))
        self._icon.setStyleSheet(f"color: {STRAWBERRY}; background: transparent;")

        self._title = QLabel(S.PAY_ERROR_TITLE)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setWordWrap(True)
        self._title.setFont(kolomna_font(self._m.fs_h1, QFont.Weight.Black))
        self._title.setStyleSheet(f"color: {STRAWBERRY}; background: transparent;")

        self._detail_lbl = QLabel()
        self._detail_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_lbl.setWordWrap(True)
        self._detail_lbl.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Medium))
        self._detail_lbl.setStyleSheet(f"color: {INK_60}; background: transparent;")
        self._detail_lbl.hide()

        self._contact = QLabel(S.PAY_ERROR_CONTACT)
        self._contact.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._contact.setWordWrap(True)
        self._contact.setFont(kolomna_font(self._m.fs_lead, QFont.Weight.Medium))
        self._contact.setStyleSheet(f"color: {INK_60}; background: transparent;")

        self._phone_lbl = QLabel()
        self._phone_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._phone_lbl.setFont(kolomna_font(self._m.fs_h2, QFont.Weight.Black))
        self._phone_lbl.setStyleSheet(f"color: {GREEN}; background: transparent;")

        order_box = QWidget()
        order_box.setStyleSheet(
            f"QWidget {{ background: {GREEN}; border-radius: {self._m.radius_lg}px; }}"
        )
        order_lay = QVBoxLayout(order_box)
        order_lay.setContentsMargins(scale(56, w), scale(28, w), scale(56, w), scale(28, w))
        order_lay.setSpacing(scale(8, w))
        self._order_caption = QLabel(S.ORDER_NO)
        self._order_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._order_caption.setFont(kolomna_font(scale(28, w), QFont.Weight.Bold))
        self._order_caption.setStyleSheet(
            f"color: {CREAM}; background: transparent; opacity: 0.85; "
            f"letter-spacing: {scale(3, w)}px;"
        )
        self._order_no = QLabel()
        self._order_no.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._order_no.setFont(kolomna_font(scale(88, w), QFont.Weight.Black))
        self._order_no.setStyleSheet(f"color: {CREAM}; background: transparent;")
        order_lay.addWidget(self._order_caption)
        order_lay.addWidget(self._order_no)
        self._order_box = order_box

        btn_w = scale(760, w)
        btns = QWidget()
        btns.setStyleSheet("background: transparent;")
        btns_lay = QVBoxLayout(btns)
        btns_lay.setContentsMargins(0, 0, 0, 0)
        btns_lay.setSpacing(scale(8, w))

        self._pay_btn = PaySumPillBtn(self._m, S.CHECKOUT)
        self._pay_btn.setMinimumWidth(btn_w)
        self._pay_btn.clicked.connect(self.go_payment.emit)

        self._retry_btn = PaySumPillBtn(self._m, S.PAY_ERROR_RETRY)
        self._retry_btn.setMinimumWidth(btn_w)
        self._retry_btn.clicked.connect(self.retry.emit)

        self._menu_btn = _FootPillBtn(self._m, ghost=True)
        self._menu_btn.setMinimumWidth(btn_w)
        self._menu_btn.setText(S.PAY_ERROR_MENU)
        self._menu_btn.clicked.connect(self.to_menu.emit)

        btns_lay.addWidget(self._pay_btn)
        btns_lay.addWidget(self._retry_btn)
        btns_lay.addWidget(self._menu_btn)

        lay.addWidget(self._icon, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._detail_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._contact, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._phone_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._order_box, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(scale(4, w))
        lay.addWidget(btns, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._layout.addWidget(inner)

    def set_content(
        self,
        *,
        detail: str | None = None,
        phone: str = "",
        order_id: str = "",
    ) -> None:
        self._detail = (detail or "").strip()
        self._phone = phone.strip()
        self._order_id = order_id.strip()
        self._apply_content()

    def _apply_content(self) -> None:
        if self._detail and self._detail != CONTACT_LINE and self._detail != S.PAY_ERROR_CONTACT:
            self._detail_lbl.setText(self._detail)
            self._detail_lbl.show()
        else:
            self._detail_lbl.hide()
        self._phone_lbl.setText(self._phone)
        self._phone_lbl.setVisible(bool(self._phone))
        if self._order_id:
            self._order_no.setText(f"№\u00a0{self._order_id}")
            self._order_box.show()
        else:
            self._order_box.hide()

    def refresh_cta(self) -> None:
        self._pay_btn.refresh_cta()
        self._retry_btn.refresh_cta()
        self._menu_btn.refresh_cta()

    def retranslate(self) -> None:
        self._title.setText(S.PAY_ERROR_TITLE)
        self._contact.setText(S.PAY_ERROR_CONTACT)
        self._order_caption.setText(S.ORDER_NO)
        self._pay_btn.set_label(S.CHECKOUT)
        self._retry_btn.set_label(S.PAY_ERROR_RETRY)
        self._menu_btn.setText(S.PAY_ERROR_MENU)
        self._apply_content()
