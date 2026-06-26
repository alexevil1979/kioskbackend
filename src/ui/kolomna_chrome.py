"""Единая строка chrome: «Назад» / Инфо + lang-toggle (одинаковый уровень на всех экранах)."""

from __future__ import annotations

from src.ui.kolomna_shadow import shadow_soft_bleed
from src.ui.kolomna_tokens import KolomnaMetrics, scale


def chrome_pill_height(viewport_width: int) -> int:
    """Высота белой pill внутри тени (как у lang-toggle)."""
    btn_h = scale(64, viewport_width)
    pad = scale(6, viewport_width)
    return pad * 2 + btn_h


def chrome_row_height(viewport_width: int) -> int:
    """Полная высота виджета в строке chrome (pill + нижняя тень)."""
    _, _, _, bleed_b = shadow_soft_bleed(viewport_width)
    return chrome_pill_height(viewport_width) + bleed_b


def chrome_top_pad(metrics: KolomnaMetrics) -> int:
    return metrics.pad


def chrome_api_status_gap(metrics: KolomnaMetrics) -> int:
    """Отступ индикатора API от краёв формы и от lang-toggle (одинаковый)."""
    return metrics.pad


def chrome_status_stack_height(metrics: KolomnaMetrics) -> int:
    """Высота колонки: индикатор + отступ + lang-toggle."""
    dot_h = max(10, scale(14, metrics.width))
    return dot_h + chrome_api_status_gap(metrics) + chrome_row_height(metrics.width)
