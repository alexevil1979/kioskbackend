from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from src.core.config import ROOT
from src.models.category_hub import CategorySummary
from src.ui.image_utils import load_pixmap, scale_pixmap_cover
from src.ui.kolomna_tokens import CREAM, FONT, KolomnaMetrics


class _CategoryTile(QPushButton):
    def __init__(
        self,
        summary: CategorySummary,
        accent: str,
        edge: str,
        metrics: KolomnaMetrics,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._summary = summary
        self._m = metrics
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumHeight(scale(260, metrics.width))
        self.setStyleSheet(
            f"QPushButton {{ background: {accent}; border: none; border-bottom: "
            f"{scale(6, metrics.width)}px solid {edge}; border-radius: {metrics.radius_lg}px; "
            f"text-align: left; padding: {scale(20, metrics.width)}px; }}"
            f"QPushButton:pressed {{ filter: brightness(0.94); }}"
        )

        lay = QGridLayout(self)
        lay.setContentsMargins(scale(16, metrics.width), scale(16, metrics.width), scale(16, metrics.width), scale(16, metrics.width))

        art = QLabel()
        art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art.setStyleSheet("background: transparent;")
        pix = self._load_cover()
        if pix and not pix.isNull():
            side = scale(140, metrics.width)
            art.setPixmap(
                scale_pixmap_cover(pix, side, side).scaled(
                    side, side, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
            )
        lay.addWidget(art, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        name = QLabel(summary.name)
        name.setWordWrap(True)
        name.setStyleSheet(
            f"QLabel {{ color: #FFFFFF; font-family: {FONT}; font-size: {metrics.fs_h3}px; "
            f"font-weight: 900; background: transparent; }}"
        )
        lay.addWidget(name, 1, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        sub = QLabel(summary.count_label)
        sub.setStyleSheet(
            f"QLabel {{ color: rgba(246,239,216,0.9); font-family: {FONT}; "
            f"font-size: {metrics.fs_label}px; font-weight: 700; background: transparent; }}"
        )
        lay.addWidget(sub, 2, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

    def _load_cover(self) -> QPixmap | None:
        if self._summary.cover_image_local:
            p = Path(self._summary.cover_image_local)
            if p.is_file():
                return load_pixmap(p)
        if self._summary.cover_image_url:
            return None
        # fallback hub art
        hub = ROOT / "assets" / "hub"
        for name in ("berry.jpg", "dairy.jpg", "honey.jpg", "plants.jpg", "cheese.jpg"):
            path = hub / name
            if path.is_file():
                return load_pixmap(path)
        return None

    @property
    def category_id(self) -> str:
        return self._summary.id


class KolomnaCategoryGrid(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._tiles: list[_CategoryTile] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setStyleSheet(f"QScrollArea {{ background: {CREAM}; border: none; }}")

        self._host = QWidget()
        self._host.setStyleSheet(f"background: {CREAM};")
        self._grid = QGridLayout(self._host)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(metrics.gap)
        self._scroll.setWidget(self._host)
        root.addWidget(self._scroll)

    def scroll_area(self) -> QScrollArea:
        return self._scroll

    def set_summaries(self, summaries: list[CategorySummary]) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._tiles.clear()

        cols = 2
        for i, summary in enumerate(summaries):
            accent, edge = self._m.accent_for_index(i)
            tile = _CategoryTile(summary, accent, edge, self._m, self._host)
            tile.clicked.connect(lambda checked=False, t=tile: self.category_selected.emit(t.category_id))
            r, c = divmod(i, cols)
            self._grid.addWidget(tile, r, c)
            self._tiles.append(tile)


def scale(px: int, width: int) -> int:
    from src.ui.kolomna_tokens import scale as s

    return s(px, width)
