from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainterPath, QPixmap, QRegion
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from src.core.config import ROOT
from src.models.category_hub import CategorySummary
from src.ui.image_utils import load_pixmap, scale_pixmap_cover
from src.ui.katusha_hub_tokens import CARD_HEIGHT, CARD_RADIUS, HERO_HEIGHT

_RADIUS = CARD_RADIUS
_HUB_DIR = (ROOT / "assets" / "hub").resolve()


class CategoryHubCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(
        self,
        summary: CategorySummary,
        *,
        hero: bool = False,
        width: int = 448,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._summary = summary
        h = HERO_HEIGHT if hero else CARD_HEIGHT
        obj = "CategoryHubHero" if hero else "CategoryHubCard"
        self.setObjectName(obj)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(width, h)

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)

        photo = QLabel()
        photo.setFixedSize(width, h)
        photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = self._load_pixmap()
        baked = summary.baked
        if not pix.isNull():
            if baked:
                photo.setPixmap(
                    pix.scaled(
                        width,
                        h,
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            else:
                photo.setPixmap(scale_pixmap_cover(pix, width, h))
        else:
            photo.setStyleSheet(f"background-color: #2D6A4F; border-radius: {_RADIUS}px;")

        grid.addWidget(photo, 0, 0)

        if not baked:
            grid.addWidget(self._caption_overlay(summary, hero, width, h), 0, 0)

        self.setStyleSheet(f"QFrame#{obj} {{ border-radius: {_RADIUS}px; border: none; }}")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), _RADIUS, _RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    @staticmethod
    def _caption_overlay(
        summary: CategorySummary, hero: bool, width: int, height: int
    ) -> QWidget:
        from src.ui.katusha_hub_tokens import CARD_PAD, GRADIENT_BOTTOM

        overlay = QWidget()
        overlay.setFixedSize(width, height)
        overlay.setStyleSheet(
            f"""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,0,0,0),
                stop:0.55 rgba(0,0,0,0),
                stop:1 rgba(0,0,0,{GRADIENT_BOTTOM})
            );
            border-radius: {_RADIUS}px;
            """
        )
        ov = QVBoxLayout(overlay)
        ov.setContentsMargins(CARD_PAD, 0, CARD_PAD, CARD_PAD)
        ov.setSpacing(2)
        ov.addStretch(1)
        title = QLabel(summary.name.upper())
        px = "12px" if hero else "9px"
        title.setStyleSheet(
            f"color:#FFF;font-family:Unbounded,Segoe UI,sans-serif;"
            f"font-size:{px};font-weight:700;background:transparent;"
            "letter-spacing:0.02em;"
        )
        title.setWordWrap(hero)
        ov.addWidget(title)
        count = QLabel(summary.count_label)
        count_px = "11px" if hero else "10px"
        count.setStyleSheet(
            f"color:rgba(255,255,255,0.92);font-family:Inter,Segoe UI,sans-serif;"
            f"font-size:{count_px};font-weight:500;background:transparent;"
        )
        ov.addWidget(count)
        return overlay

    def _load_pixmap(self) -> QPixmap:
        if self._summary.cover_image_local:
            pix = load_pixmap(self._summary.cover_image_local)
            if not pix.isNull():
                return pix
        return QPixmap()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._summary.id)
        super().mouseReleaseEvent(event)


def _is_baked_hub_image(path: str) -> bool:
    if not path:
        return False
    try:
        return Path(path).resolve().parent == _HUB_DIR
    except OSError:
        return False
