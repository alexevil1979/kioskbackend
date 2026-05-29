from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Category:
    id: str
    name: str
    sort_order: int = 0


@dataclass
class Product:
    id: str
    category_id: str
    name: str
    price_rub: float
    image_url: str = ""
    image_local: str = ""
    stock: int = 999
    unit: str = "шт"
    description: str = ""

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def price_display(self) -> str:
        if self.price_rub == int(self.price_rub):
            return f"{int(self.price_rub)} ₽"
        return f"{self.price_rub:.2f} ₽"
