from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget

from src.ui.kolomna_tokens import CREAM, GREEN, STRAWBERRY, YELLOW, KolomnaMetrics, scale


class KolomnaCardVis(QWidget):
    """pay-cardvis: терминал + карта (референс CardScreen)."""

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        w = scale(300, metrics.width)
        h = scale(224, metrics.width)
        self.setFixedSize(int(w * 1.5), int(h * 1.5))

        term = QFrame(self)
        term.setGeometry(scale(20, metrics.width), scale(24, metrics.width), scale(152, metrics.width), scale(204, metrics.width))
        term.setStyleSheet(
            f"QFrame {{ background: {GREEN}; border-radius: {scale(28, metrics.width)}px; }}"
        )
        screen = QFrame(term)
        screen.setGeometry(scale(24, metrics.width), scale(24, metrics.width), scale(104, metrics.width), scale(74, metrics.width))
        screen.setStyleSheet(
            f"QFrame {{ background: {CREAM}; border-radius: {scale(12, metrics.width)}px; }}"
        )

        card = QFrame(self)
        card.setGeometry(scale(120, metrics.width), scale(36, metrics.width), scale(206, metrics.width), scale(128, metrics.width))
        card.setStyleSheet(
            f"QFrame {{ background: {STRAWBERRY}; border-radius: {scale(20, metrics.width)}px; }}"
        )
        chip = QFrame(card)
        chip.setGeometry(scale(24, metrics.width), scale(28, metrics.width), scale(44, metrics.width), scale(34, metrics.width))
        chip.setStyleSheet(
            f"QFrame {{ background: {YELLOW}; border-radius: {scale(8, metrics.width)}px; }}"
        )
