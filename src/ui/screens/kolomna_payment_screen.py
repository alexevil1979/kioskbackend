from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget, QLabel

from src.core.config import Settings
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import fmt_price, n_items_label
from src.ui.kolomna_tokens import CREAM, GREEN, INK_60, KolomnaMetrics, STRAWBERRY, scale
from src.ui.screens.base_screen import BaseScreen
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.widgets.kolomna_cart_footbar import PaySumPillBtn
from src.ui.widgets.kolomna_pay_method import KolomnaPayMethod
from src.ui.widgets.kolomna_topbar import KolomnaTopBar


class KolomnaPaymentScreen(BaseScreen):
    pay_requested = pyqtSignal(str)
    cancel = pyqtSignal()

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)
        self._method = "sbp"
        self._total = 0.0
        self._count = 0

        self.setObjectName("KolomnaPaymentScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top = KolomnaTopBar(self._m, show_back=True, show_lang=True)
        self._top.set_title(S.PAY_TITLE, accent=GREEN)
        self._top.back_clicked.connect(self.cancel.emit)
        self._layout.addWidget(self._top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {CREAM}; }}")
        enable_kinetic_scroll(scroll)

        host = QWidget()
        host.setStyleSheet(f"background: {CREAM};")
        host_lay = QVBoxLayout(host)
        host_lay.setContentsMargins(self._m.pad, scale(24, w), self._m.pad, self._m.pad)
        host_lay.setSpacing(scale(24, w))

        self._eyebrow = QLabel(S.PAY_METHOD.upper())
        self._eyebrow.setFont(kolomna_font(self._m.fs_label, QFont.Weight.ExtraBold))
        self._eyebrow.setStyleSheet(
            f"color: {STRAWBERRY}; background: transparent; "
            f"letter-spacing: {scale(3, w)}px;"
        )
        host_lay.addWidget(self._eyebrow)

        methods = QWidget()
        methods.setStyleSheet("background: transparent;")
        methods_lay = QVBoxLayout(methods)
        methods_lay.setContentsMargins(0, scale(26, w), 0, 0)
        methods_lay.setSpacing(scale(24, w))

        self._sbp = KolomnaPayMethod("sbp", "QR", S.PAY_SBP, S.PAY_SBP_SUB, self._m)
        self._card = KolomnaPayMethod("card", "▭", S.PAY_CARD, S.PAY_CARD_SUB, self._m)
        self._sbp.selected.connect(self._set_method)
        self._card.selected.connect(self._set_method)
        methods_lay.addWidget(self._sbp)
        methods_lay.addWidget(self._card)
        host_lay.addWidget(methods)
        host_lay.addStretch(1)
        scroll.setWidget(host)
        self._layout.addWidget(scroll, stretch=1)

        foot = QFrame()
        foot.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        foot.setStyleSheet(f"QFrame {{ background: {CREAM}; border: none; }}")
        foot_lay = QVBoxLayout(foot)
        foot_lay.setContentsMargins(
            self._m.pad, scale(30, w), self._m.pad, scale(48, w) + scale(24, w)
        )
        foot_lay.setSpacing(scale(26, w))

        self._total_label = QLabel()
        self._total_label.setFont(kolomna_font(self._m.fs_lead, QFont.Weight.Bold))
        self._total_label.setStyleSheet(
            f"color: {INK_60}; background: transparent; border: none;"
        )
        self._total_sum = QLabel()
        self._total_sum.setFont(kolomna_font(scale(96, w), QFont.Weight.Black))
        self._total_sum.setStyleSheet(
            f"color: {GREEN}; background: transparent; border: none; letter-spacing: -1px;"
        )
        foot_lay.addWidget(self._total_label)
        foot_lay.addWidget(self._total_sum)

        self._pay_btn = PaySumPillBtn(self._m, S.PAY)
        self._pay_btn.set_breathe(True)
        self._pay_btn.clicked.connect(self._on_pay)
        foot_lay.addWidget(self._pay_btn)
        self._layout.addWidget(foot)

        self._set_method("sbp")

    def _set_method(self, method: str) -> None:
        self._method = method
        self._sbp.set_active(method == "sbp")
        self._card.set_active(method == "card")

    def set_summary(self, count: int, total_rub: float) -> None:
        self._count = count
        self._total = total_rub
        self._total_label.setText(f"{S.TOTAL} · {n_items_label(count)}")
        self._total_sum.setText(f"{fmt_price(total_rub)}\u00a0{S.CUR}")
        self._pay_btn.set_sum(f"{fmt_price(total_rub)}\u00a0{S.CUR}")
        self._pay_btn.bump()

    def _on_pay(self) -> None:
        self.pay_requested.emit(self._method)

    def retranslate(self) -> None:
        self._top.set_title(S.PAY_TITLE, accent=GREEN)
        self._top.retranslate()
        self._eyebrow.setText(S.PAY_METHOD.upper())
        self._sbp.set_text(S.PAY_SBP, S.PAY_SBP_SUB)
        self._card.set_text(S.PAY_CARD, S.PAY_CARD_SUB)
        self._pay_btn.set_label(S.PAY)
        self.set_summary(self._count, self._total)
