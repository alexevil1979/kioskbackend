from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, GREEN, KolomnaMetrics, scale
from src.ui.widgets.kolomna_cart_footbar import PaySumPillBtn, _FootPillBtn


class KolomnaFootBar(QFrame):
    """Нижняя панель с CTA (screen__footbar): pill-кнопка, слева текст, справа сумма."""

    primary_clicked = pyqtSignal()
    secondary_clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self.setObjectName("KolomnaFootBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(metrics.pad, scale(30, metrics.width), metrics.pad, scale(48, metrics.width))
        lay.setSpacing(scale(16, metrics.width))

        self._label_row = QLabel()
        self._label_row.hide()
        lay.addWidget(self._label_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(scale(16, metrics.width))
        btn_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._secondary = _FootPillBtn(metrics, ghost=True)
        self._secondary.hide()
        self._secondary.clicked.connect(self.secondary_clicked.emit)
        btn_row.addWidget(self._secondary, stretch=10)

        self._primary = PaySumPillBtn(metrics, "")
        self._primary.clicked.connect(self.primary_clicked.emit)
        btn_row.addWidget(self._primary, stretch=14)

        lay.addLayout(btn_row)

    def set_primary(self, text: str, *, sum_text: str = "") -> None:
        self._primary.set_label(text)
        self._primary.set_sum(sum_text)

    def set_secondary(self, text: str) -> None:
        if text:
            self._secondary.setText(text)
            self._secondary.show()
        else:
            self._secondary.hide()

    def set_summary(self, label: str, total: str) -> None:
        if label:
            self._label_row.setText(f"{label}  {total}")
            self._label_row.setFont(kolomna_font(self._m.fs_h2, QFont.Weight.Black))
            self._label_row.setStyleSheet(
                f"QLabel {{ color: {GREEN}; background: transparent; }}"
            )
            self._label_row.show()
        else:
            self._label_row.hide()
