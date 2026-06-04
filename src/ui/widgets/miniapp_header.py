from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.config import ROOT
from src.ui.image_utils import load_pixmap, scale_pixmap
from src.ui.katusha_hub_tokens import VIEWPORT_W, Y_HEADER


_HEADER_REF = ROOT / "assets" / "reference" / "header_strip.png"


class MiniAppHeader(QWidget):
    """Шапка 1:1 — растровая вырезка из screen_katusha.png."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("MiniAppHeader")
        self.setFixedHeight(Y_HEADER)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        art = QLabel()
        art.setObjectName("MiniAppHeaderArt")
        art.setScaledContents(True)
        if _HEADER_REF.is_file():
            pix = load_pixmap(_HEADER_REF)
            if not pix.isNull() and pix.width() != VIEWPORT_W:
                pix = scale_pixmap(pix, VIEWPORT_W, Y_HEADER)
            art.setPixmap(pix)
            art.setFixedSize(VIEWPORT_W, Y_HEADER)
        lay.addWidget(art)
