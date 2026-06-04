from __future__ import annotations

import logging
from typing import Any

from src.core.cart import CartLine
from src.models.product import Product

logger = logging.getLogger(__name__)


def parse_api_product_ids(product: Product) -> tuple[int, int]:
    """product_id и variant_id для POST /order/create."""
    if product.api_product_id and product.variant_id:
        return product.api_product_id, product.variant_id
    parts = product.id.split("_", 1)
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return int(parts[0]), int(parts[1])
    raise ValueError(f"Не удалось определить product_id/variant_id для «{product.name}»")


def cart_lines_to_order_items(lines: list[CartLine]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in lines:
        product_id, variant_id = parse_api_product_ids(line.product)
        qty = line.quantity
        if line.product.is_weight_variable:
            logger.warning(
                "Весовой товар %s: quantity=%s (ожидаются граммы по API)",
                line.product.name,
                qty,
            )
        items.append(
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "quantity": qty,
            }
        )
    return items
