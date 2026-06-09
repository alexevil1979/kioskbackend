from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.config import Settings
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import fmt_price
from src.ui.kolomna_tokens import CREAM, GREEN, KolomnaMetrics, scale
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.kolomna_card_vis import KolomnaCardVis
from src.ui.widgets.kolomna_pay_due import KolomnaPayDueRow
from src.ui.widgets.kolomna_topbar import KolomnaTopBar


class KolomnaCardScreen(BaseScreen):
    cancel = pyqtSignal()
    completed = pyqtSignal(bool)

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)

        self.setObjectName("KolomnaCardScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top = KolomnaTopBar(self._m, show_back=True, show_lang=True)
        self._top.set_title(S.PAY_TITLE, accent=GREEN)
        self._top.back_clicked.connect(self.cancel.emit)
        self._layout.addWidget(self._top)

        center = QWidget()
        lay = QVBoxLayout(center)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(scale(40, w))
        lay.setContentsMargins(self._m.pad, scale(24, w), self._m.pad, self._m.pad)

        self._instr = QLabel(S.PAY_CARD_HOLD)
        self._instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._instr.setWordWrap(True)
        self._instr.setFont(kolomna_font(self._m.fs_h3, QFont.Weight.ExtraBold))
        self._instr.setStyleSheet(f"color: {GREEN}; background: transparent;")

        lay.addWidget(self._instr)
        lay.addWidget(KolomnaCardVis(self._m), alignment=Qt.AlignmentFlag.AlignHCenter)

        self._due_row = KolomnaPayDueRow(self._m)
        lay.addWidget(self._due_row, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._layout.addWidget(center, stretch=1)

        self._mock_timer = QTimer(self)
        self._mock_timer.setSingleShot(True)
        self._mock_timer.timeout.connect(lambda: self.completed.emit(True))

    def set_amount(self, total_rub: float) -> None:
        self._due_row.set_amount(f"{fmt_price(total_rub)}\u00a0{S.CUR}")

    def set_instruction(self, title: str, hint: str, status: str = "") -> None:
        self._instr.setText(title if title else S.PAY_CARD_HOLD)

    def start_waiting(self, *, mock_auto_success: bool = True) -> None:
        if mock_auto_success:
            self._mock_timer.start(10_000)
        else:
            self._mock_timer.stop()

    def stop(self) -> None:
        self._mock_timer.stop()

    def retranslate(self) -> None:
        self._top.set_title(S.PAY_TITLE, accent=GREEN)
        self._top.retranslate()
        self._instr.setText(S.PAY_CARD_HOLD)
        self._due_row.set_label(f"{S.PAY_DUE}:")
        amount = self._due_row.amount_text()
        if amount:
            parts = amount.split("\u00a0")
            if parts:
                self._due_row.set_amount(f"{parts[0]}\u00a0{S.CUR}")
