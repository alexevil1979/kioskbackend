from __future__ import annotations

from PyQt6.QtWidgets import QScrollArea


def enable_kinetic_scroll(scroll: QScrollArea) -> None:
    """Свайп/колесо на тач-киоске без видимого скроллбара."""
    vp = scroll.viewport()
    vp.setAutoFillBackground(True)
    try:
        from PyQt6.QtWidgets import QScroller, QScrollerProperties

        QScroller.grabGesture(vp, QScroller.ScrollerGestureType.TouchGesture)
        QScroller.grabGesture(vp, QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        props = scroll.scrollerProperties()
        props.setScrollMetric(
            QScrollerProperties.ScrollMetric.OvershootDragResistanceFactor,
            1.0,
        )
        props.setScrollMetric(
            QScrollerProperties.ScrollMetric.OvershootScrollDistanceFactor,
            0.0,
        )
        scroll.setScrollerProperties(props)
    except Exception:
        pass
