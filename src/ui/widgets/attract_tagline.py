from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QWidget

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import GREEN, scale


class AttractTagline(QWidget):
    """
    attract__tagline: uppercase, font-weight 800, letter-spacing .14em.
    Рисуем вручную — QFont letterSpacing ломает кириллицу на Windows.
    """

    def __init__(self, text: str, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        self._viewport_width = viewport_width
        self._text = text.upper()
        px = scale(34, viewport_width)
        self._font = kolomna_font(px, QFont.Weight.ExtraBold)
        self._spacing = px * 0.14
        self._color = QColor(GREEN)

        fm = QFontMetrics(self._font)
        total_w = sum(fm.horizontalAdvance(ch) for ch in self._text)
        if len(self._text) > 1:
            total_w += self._spacing * (len(self._text) - 1)
        self.setFixedSize(max(1, int(total_w) + 2), fm.height() + 4)

    def set_text(self, text: str) -> None:
        self._text = text.upper()
        fm = QFontMetrics(self._font)
        total_w = sum(fm.horizontalAdvance(ch) for ch in self._text)
        if len(self._text) > 1:
            total_w += self._spacing * (len(self._text) - 1)
        self.setFixedSize(max(1, int(total_w) + 2), fm.height() + 4)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font)
        painter.setPen(self._color)
        fm = QFontMetrics(self._font)
        x = 0.0
        y = fm.ascent() + 1
        for i, ch in enumerate(self._text):
            painter.drawText(int(x), y, ch)
            x += fm.horizontalAdvance(ch)
            if i < len(self._text) - 1:
                x += self._spacing
