from __future__ import annotations

from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, pyqtSignal

from src.models.product import Product


@dataclass
class CartLine:
    product: Product
    quantity: int = 1
    tour_kids: int = 0
    tour_pickup_schedule_id: int = 0
    tour_date_id: str = ""
    tour_date_label: str = ""

    @property
    def line_total(self) -> float:
        return self.product.price_rub * self.quantity

    @property
    def is_tour(self) -> bool:
        from src.ui.kolomna_catalog import is_tour_product

        return is_tour_product(self.product)


class Cart(QObject):
    changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._lines: dict[str, CartLine] = {}

    def add(
        self,
        product: Product,
        qty: int = 1,
        *,
        tour_kids: int | None = None,
        tour_pickup_schedule_id: int = 0,
        tour_date_id: str = "",
        tour_date_label: str = "",
    ) -> None:
        if not product.is_purchasable:
            return
        if tour_kids is not None:
            adults = max(1, qty)
            self._lines[product.id] = CartLine(
                product=product,
                quantity=adults,
                tour_kids=max(0, tour_kids),
                tour_pickup_schedule_id=max(0, tour_pickup_schedule_id),
                tour_date_id=tour_date_id,
                tour_date_label=tour_date_label,
            )
            self.changed.emit()
            return
        if product.id in self._lines:
            self._lines[product.id].quantity += qty
        else:
            self._lines[product.id] = CartLine(product=product, quantity=qty)
        self._clamp_stock(product.id)
        self.changed.emit()

    def set_quantity(self, product_id: str, qty: int) -> None:
        if product_id not in self._lines:
            return
        if qty <= 0:
            del self._lines[product_id]
        else:
            self._lines[product_id].quantity = qty
            self._clamp_stock(product_id)
        self.changed.emit()

    def _clamp_stock(self, product_id: str) -> None:
        line = self._lines.get(product_id)
        if line and line.quantity > line.product.stock:
            line.quantity = max(0, line.product.stock)
            if line.quantity == 0:
                del self._lines[product_id]

    def quantity_of(self, product_id: str) -> int:
        line = self._lines.get(product_id)
        return line.quantity if line else 0

    def remove(self, product_id: str) -> None:
        self._lines.pop(product_id, None)
        self.changed.emit()

    def clear(self) -> None:
        self._lines.clear()
        self.changed.emit()

    def sync_products_from_catalog(self, catalog) -> None:
        """Подтянуть актуальные name/variant_name с каталога перед показом корзины."""
        for line in self._lines.values():
            fresh = catalog.product_by_id(line.product.id)
            if fresh is not None:
                line.product = fresh

    @property
    def lines(self) -> list[CartLine]:
        return list(self._lines.values())

    @property
    def item_count(self) -> int:
        return sum(line.quantity for line in self._lines.values())

    @property
    def positions_count(self) -> int:
        return len(self._lines)

    @property
    def total_rub(self) -> float:
        return sum(line.line_total for line in self._lines.values())

    def total_display(self) -> str:
        total = self.total_rub
        if total == int(total):
            return f"{int(total)} ₽"
        return f"{total:.2f} ₽"
