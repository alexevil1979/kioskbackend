"""Строка «К оплате: сумма» (.pay-due в design-system)."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QSizePolicy, QWidget

from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import GREEN, KolomnaMetrics, scale


class KolomnaPayDueRow(QWidget):
    """label + price--display на одной базовой линии (align-items: baseline)."""

    def __init__(
        self,
        metrics: KolomnaMetrics,
        *,
        sum_font_px: int | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics
        w = metrics.width
        self._gap = scale(20, w)
        self._label_text = f"{S.PAY_DUE}:"
        self._sum_text = ""
        self._label_font = kolomna_font(scale(38, w), QFont.Weight.Bold)
        self._sum_font = kolomna_font(
            sum_font_px if sum_font_px is not None else metrics.fs_display,
            QFont.Weight.Black,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._sync_size()

    def set_amount(self, amount_text: str) -> None:
        self._sum_text = amount_text
        self._sync_size()
        self.update()

    def set_label(self, text: str) -> None:
        self._label_text = text
        self._sync_size()
        self.update()

    def amount_text(self) -> str:
        return self._sum_text

    def _sync_size(self) -> None:
        fm_l = QFontMetrics(self._label_font)
        fm_s = QFontMetrics(self._sum_font)
        w = fm_l.horizontalAdvance(self._label_text)
        if self._sum_text:
            w += self._gap + fm_s.horizontalAdvance(self._sum_text)
        h = fm_s.height() if self._sum_text else fm_l.height()
        self.setFixedSize(max(1, w), max(1, h))

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        fm_l = QFontMetrics(self._label_font)
        fm_s = QFontMetrics(self._sum_font)
        baseline = self.height() - max(fm_l.descent(), fm_s.descent() if self._sum_text else 0)

        p.setPen(QColor(GREEN))
        x = 0
        p.setFont(self._label_font)
        p.drawText(x, baseline, self._label_text)
        x += fm_l.horizontalAdvance(self._label_text)
        if self._sum_text:
            p.setFont(self._sum_font)
            p.drawText(x + self._gap, baseline, self._sum_text)
        p.end()
