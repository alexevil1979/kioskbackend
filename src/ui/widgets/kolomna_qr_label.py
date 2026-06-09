from __future__ import annotations

from typing import Literal

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_qr_render import LogoId, load_cached_qr_pixmap, render_kolomna_qr_pixmap, scale_qr_for_display
from src.ui.kolomna_tokens import GREEN, KolomnaMetrics, scale


class KolomnaQrTile(QWidget):
    def __init__(
        self,
        url: str,
        label: str,
        metrics: KolomnaMetrics,
        *,
        logo: LogoId = "",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        box = scale(248, metrics.width)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(scale(16, metrics.width))
        lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        box_w = QLabel()
        box_w.setFixedSize(box, box)
        box_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box_w.setStyleSheet(
            f"background: #FFFFFF; border-radius: {scale(18, metrics.width)}px;"
        )
        src = load_cached_qr_pixmap("info", logo=logo, px=box)
        if src.isNull():
            src = load_cached_qr_pixmap("info", logo=logo, px=460)
        if src.isNull():
            src = render_kolomna_qr_pixmap(url, px=460, color=GREEN, logo=logo)
        pix = src if not src.isNull() and src.width() == box else scale_qr_for_display(src, box)
        inner = None
        if not pix.isNull():
            inner = QLabel()
            inner.setPixmap(pix)
            inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inner.setStyleSheet("background: transparent;")
            inner_lay = QVBoxLayout(box_w)
            inner_lay.setContentsMargins(0, 0, 0, 0)
            inner_lay.addWidget(inner, alignment=Qt.AlignmentFlag.AlignCenter)

        self._cap = QLabel(label)
        self._cap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cap.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        self._cap.setStyleSheet(f"color: {GREEN}; background: transparent;")

        self._box_w = box_w
        self._inner = inner if not pix.isNull() else None

        lay.addWidget(box_w, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._cap)

    def set_label(self, text: str) -> None:
        self._cap.setText(text)

    def set_qr_pixmap(self, pix) -> None:
        if pix is None or pix.isNull():
            return
        if self._inner is None:
            self._inner = QLabel(self._box_w)
            self._inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._inner.setStyleSheet("background: transparent;")
            inner_lay = QVBoxLayout(self._box_w)
            inner_lay.setContentsMargins(0, 0, 0, 0)
            inner_lay.addWidget(self._inner, alignment=Qt.AlignmentFlag.AlignCenter)
        self._inner.setPixmap(pix)
