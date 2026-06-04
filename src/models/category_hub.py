from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CategorySummary:
    """Карточка категории на главной mini app (хаб «КАТЕГОРИИ»)."""

    id: str
    name: str
    product_count: int
    cover_image_local: str = ""
    cover_image_url: str = ""
    hero: bool = False
    # True только для готовых hub/*.jpg с текстом на картинке (референс 699)
    baked: bool = False

    @property
    def count_label(self) -> str:
        n = self.product_count
        if n % 10 == 1 and n % 100 != 11:
            word = "товар"
        elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
            word = "товара"
        else:
            word = "товаров"
        return f"{n} {word}"
