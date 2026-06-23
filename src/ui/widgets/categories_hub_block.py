from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QSizePolicy, QWidget

from src.models.category_hub import CategorySummary
from src.ui.katusha_hub_tokens import (
    SLOT_HERO,
    SLOTS_HALF,
    VIEWPORT_W,
    hub_content_height,
)
from src.ui.widgets.category_hub_card import CategoryHubCard


class CategoriesScrollContent(QWidget):
    """Категории 1:1 — абсолютная геометрия как screen_katusha.png."""

    category_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CategoriesScrollContent")
        self._summaries: list[CategorySummary] = []
        self._cards: list[CategoryHubCard] = []
        self._signature: tuple[tuple[str, str, int, str, bool, bool], ...] = ()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(VIEWPORT_W, hub_content_height(0))
        self.set_summaries([])

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#FFFFFF"))
        p.end()
        super().paintEvent(event)

    def _clear_cards(self) -> None:
        for card in self._cards:
            card.hide()
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()

    @staticmethod
    def _build_signature(
        summaries: list[CategorySummary],
    ) -> tuple[tuple[str, str, int, str, bool, bool], ...]:
        return tuple(
            (
                s.id,
                s.name,
                s.product_count,
                s.cover_image_local,
                s.hero,
                s.baked,
            )
            for s in summaries
        )

    def set_summaries(self, summaries: list[CategorySummary]) -> None:
        new_signature = self._build_signature(summaries)
        if new_signature == self._signature:
            return
        self._signature = new_signature
        self._summaries = summaries
        self._clear_cards()

        h = hub_content_height(len(summaries))
        self.setFixedSize(VIEWPORT_W, h)

        if not summaries:
            return

        hero = summaries[0]
        rest = summaries[1:]

        x, y, w, height = SLOT_HERO
        hero_card = CategoryHubCard(hero, hero=True, width=w)
        hero_card.setParent(self)
        hero_card.setGeometry(x, y, w, height)
        hero_card.clicked.connect(self.category_selected.emit)
        hero_card.show()
        self._cards.append(hero_card)

        for index, summary in enumerate(rest):
            if index >= len(SLOTS_HALF):
                break
            x, y, w, height = SLOTS_HALF[index]
            card = CategoryHubCard(summary, hero=False, width=w)
            card.setParent(self)
            card.setGeometry(x, y, w, height)
            card.clicked.connect(self.category_selected.emit)
            card.show()
            self._cards.append(card)

        self.updateGeometry()
