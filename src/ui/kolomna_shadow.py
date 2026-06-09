"""Отрисовка теней Kolomna (design-system --shadow-soft)."""

from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from src.ui.kolomna_tokens import scale

_SHADOW = QColor(20, 56, 33)
_SHADOW_ALPHA = 102  # rgba(20,56,33,.4)


def apply_shadow_soft(widget: QWidget, viewport_width: int) -> QGraphicsDropShadowEffect:
    """box-shadow: var(--shadow-soft) — для pill-виджетов (topbar__back, lang-toggle)."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(scale(28, viewport_width))
    effect.setOffset(0, scale(12, viewport_width))
    effect.setColor(QColor(_SHADOW.red(), _SHADOW.green(), _SHADOW.blue(), _SHADOW_ALPHA))
    widget.setGraphicsEffect(effect)
    return effect


def shadow_soft_bleed(viewport_width: int) -> tuple[int, int, int, int]:
    """Отступы контейнера, чтобы тень не обрезалась (L, T, R, B)."""
    s = scale(10, viewport_width)
    b = scale(32, viewport_width)
    return (s, 0, s, b)


def draw_shadow_soft_ellipse(p: QPainter, rect: QRectF, vw: int) -> None:
    """Тень для круглых qty__btn."""
    y_off = scale(12, vw)
    spread = scale(8, vw)
    base = rect.adjusted(spread, spread, -spread, -spread).translated(0, y_off)
    cx, cy = base.center().x(), base.center().y()
    for radius, alpha in (
        (scale(14, vw), 38),
        (scale(22, vw), 28),
        (scale(28, vw), 18),
    ):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(_SHADOW.red(), _SHADOW.green(), _SHADOW.blue(), alpha))
        p.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))
