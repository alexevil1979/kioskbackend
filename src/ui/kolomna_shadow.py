"""Отрисовка теней Kolomna (design-system --shadow-soft)."""

from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QRadialGradient
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from src.ui.kolomna_tokens import scale

_SHADOW = QColor(20, 56, 33)
_SHADOW_ALPHA = 102  # rgba(20,56,33,.4)


def draw_shadow_soft_pill(p: QPainter, rect: QRectF, radius: float, viewport_width: int) -> None:
    """Мягкая тень pill: боковые «усики» + небольшое продолжение снизу."""
    vw = max(1, viewport_width)
    p.setPen(Qt.PenStyle.NoPen)

    # Боковые края — смещённый силуэт (виден у скруглений)
    y_side = scale(8, vw)
    sr = rect.translated(0, y_side)
    p.setBrush(QColor(_SHADOW.red(), _SHADOW.green(), _SHADOW.blue(), 68))
    p.drawRoundedRect(sr, radius, radius)

    # Снизу — лёгкий эллипс (центр pill не перекрывает белую заливку)
    cx = rect.center().x()
    cy = rect.bottom() + scale(4, vw)
    rx = max(scale(18, vw), rect.width() * 0.40)
    ry = scale(9, vw)
    grad = QRadialGradient(QPointF(cx, cy), max(rx, ry))
    grad.setColorAt(0.0, QColor(_SHADOW.red(), _SHADOW.green(), _SHADOW.blue(), 44))
    grad.setColorAt(0.6, QColor(_SHADOW.red(), _SHADOW.green(), _SHADOW.blue(), 14))
    grad.setColorAt(1.0, QColor(_SHADOW.red(), _SHADOW.green(), _SHADOW.blue(), 0))
    p.setBrush(grad)
    p.drawEllipse(QRectF(cx - rx, cy - ry * 0.55, rx * 2.0, ry * 1.1))


def apply_shadow_soft(widget: QWidget, viewport_width: int) -> QGraphicsDropShadowEffect:
    """box-shadow: var(--shadow-soft) — только для виджетов БЕЗ QPainter в paintEvent."""
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
    """Тень для круглых кнопок (legacy; qty__btn без тени)."""
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
