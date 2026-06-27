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
    category_name: str = ""
    is_available: bool = True
    sale_available: bool = True
    unavailable_reason: str = ""
    sale_unavailable_label: str = ""
    hide_price_when_unavailable: bool = False
    producer_name: str = ""
    api_product_id: int = 0
    variant_id: int = 0
    variant_name: str = ""
    is_weight_variable: bool = False
    is_excursion: bool = False
    schedule_location_id: int = 0
    schedule_location_name: str = ""

    @property
    def display_name(self) -> str:
        """name + variant_name для чеков и API-логов."""
        base = self.name.strip()
        variant = self.variant_name.strip()
        if base and variant:
            return f"{base} {variant}"
        return base or variant

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def unavailable_label(self) -> str:
        reason = self.unavailable_reason.strip()
        if reason:
            return reason
        if not self.sale_available:
            return self.sale_unavailable_label.strip() or "Созревает"
        return ""

    @property
    def is_purchasable(self) -> bool:
        if not self.sale_available:
            return False
        if self.unavailable_reason.strip():
            return False
        return self.is_available and self.stock > 0

    @property
    def show_in_catalog(self) -> bool:
        if not self.sale_available:
            return True
        if self.unavailable_reason.strip():
            return True
        return self.is_available and self.stock > 0

    @property
    def show_price(self) -> bool:
        if not self.sale_available and self.hide_price_when_unavailable:
            return False
        if self.unavailable_reason.strip() and self.hide_price_when_unavailable:
            return False
        return True

    @property
    def price_display(self) -> str:
        if self.price_rub == int(self.price_rub):
            return f"{int(self.price_rub)} ₽"
        return f"{self.price_rub:.2f} ₽"
