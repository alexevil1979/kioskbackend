"""btnBreathe — плавное дыхание pill-кнопок (как корзина в footbar)."""

from __future__ import annotations

import math
import time

from PyQt6.QtCore import QPointF, Qt, QRectF, QTimer
from PyQt6.QtGui import QFont, QPainter, QStaticText, QTransform

BREATHE_CYCLE_MS = 2600
BREATHE_SCALE = 0.028
ANIM_INTERVAL_MS = 8


def start_breathe_timer(timer: QTimer) -> None:
    timer.setTimerType(Qt.TimerType.PreciseTimer)
    timer.start(ANIM_INTERVAL_MS)


def breathe_scale(elapsed_ms: float) -> float:
    phase = (elapsed_ms % BREATHE_CYCLE_MS) / BREATHE_CYCLE_MS
    ease = 0.5 * (1.0 - math.cos(2.0 * math.pi * phase))
    return 1.0 + BREATHE_SCALE * ease


def breathe_scale_at(t0: float) -> float:
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return breathe_scale(elapsed_ms)


def breathe_pad(content_size: float) -> int:
    """Запас по краям под масштаб дыхания (pill не обрезается)."""
    return max(1, math.ceil(content_size * BREATHE_SCALE))


def font_for_breathe(font: QFont, breathing: bool) -> QFont:
    if not breathing:
        return font
    out = QFont(font)
    out.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return out


def apply_pill_scale(p: QPainter, cx: float, cy: float, s: float) -> bool:
    if abs(s - 1.0) < 1e-6:
        return False
    p.save()
    p.translate(cx, cy)
    p.scale(s, s)
    p.translate(-cx, -cy)
    return True


def static_text(font: QFont, text: str, cache: dict[str, QStaticText]) -> QStaticText:
    key = f"{text}|{font.pointSize()}|{int(font.weight())}"
    st = cache.get(key)
    if st is None:
        st = QStaticText(text)
        st.setTextFormat(Qt.TextFormat.PlainText)
        st.prepare(QTransform(), font)
        cache[key] = st
    return st


def draw_static_text(
    p: QPainter,
    font: QFont,
    text: str,
    rect: QRectF,
    align: Qt.AlignmentFlag,
    cache: dict[str, QStaticText],
) -> None:
    if not text:
        return
    p.setFont(font)
    if "\n" in text:
        p.drawText(rect, int(align | Qt.AlignmentFlag.AlignVCenter), text)
        return
    st = static_text(font, text, cache)
    sz = st.size()
    x = rect.left()
    if align & Qt.AlignmentFlag.AlignRight:
        x = rect.right() - sz.width()
    elif align & Qt.AlignmentFlag.AlignHCenter:
        x = rect.left() + (rect.width() - sz.width()) / 2.0
    y = rect.top() + (rect.height() - sz.height()) / 2.0
    p.drawStaticText(QPointF(x, y), st)
