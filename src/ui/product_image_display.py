"""Какое фото показывать у товара: с API или локальная заглушка."""
from __future__ import annotations

from pathlib import Path

from src.models.product import Product


def use_api_product_images() -> bool:
    from src.ui.kolomna_prefs import load_kolomna_prefs

    return load_kolomna_prefs().load_api_images


def product_display_image_path(product: Product) -> Path | None:
    """Путь к файлу для отрисовки: кэш API или заглушка Kolomna."""
    from src.ui.kolomna_catalog import is_tour_product, kolomna_ticket_image_path

    if is_tour_product(product):
        if product.image_local:
            p = Path(product.image_local)
            if p.is_file():
                return p
        ticket = kolomna_ticket_image_path()
        if ticket is not None:
            return ticket
        return None

    if use_api_product_images() and product.image_local:
        p = Path(product.image_local)
        if p.is_file():
            return p
    from src.ui.kolomna_catalog import kolomna_product_placeholder_path

    return kolomna_product_placeholder_path(product)
