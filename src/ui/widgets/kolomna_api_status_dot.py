from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from src.ui.kolomna_tokens import GREEN, scale

_OFFLINE = "#D64545"


class KolomnaApiStatusDot(QWidget):
    """Кружок в шапке: зелёный — /health API доступен, красный — нет."""

    def __init__(self, viewport_width: int, parent=None) -> None:
        super().__init__(parent)
        self._online = False
        sz = max(10, scale(14, viewport_width))
        self.setFixedSize(sz, sz)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._update_tooltip()

    def set_online(self, online: bool) -> None:
        if online == self._online:
            return
        self._online = online
        self._update_tooltip()
        self.update()

    def _update_tooltip(self) -> None:
        self.setToolTip("API доступен" if self._online else "API недоступен")

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(GREEN if self._online else _OFFLINE)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        r = min(self.width(), self.height())
        p.drawEllipse(QRectF(0, 0, r, r))
        p.end()
