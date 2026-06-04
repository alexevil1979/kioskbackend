from __future__ import annotations

from pathlib import Path

from src.core.config import ROOT
from src.models.category_hub import CategorySummary
from src.models.product import Category, Product

DEMO = ROOT / "assets" / "demo_products"
HERO_BG = ROOT / "assets" / "reference" / "hero_card_bg.jpg"

MISC_HUB_ID = "misc"
MISC_TITLE = "БЕЗ КАТЕГОРИИ"

_DEMO_FALLBACKS: tuple[tuple[str, str], ...] = (
    ("сажен", "12.jpg"),
    ("растен", "12.jpg"),
    ("мёд", "7.jpg"),
    ("мед", "7.jpg"),
    ("сыр", "5.jpg"),
    ("молоч", "4.jpg"),
    ("молок", "4.jpg"),
    ("ягод", "1.jpg"),
)


def _demo_fallback(category: Category) -> Path:
    name = category.name.lower()
    for needle, fname in _DEMO_FALLBACKS:
        if needle in name:
            p = DEMO / fname
            if p.is_file():
                return p
    return DEMO / "1.jpg"


def _cover_for_products(products: list[Product], fallback: Path) -> str:
    for product in products:
        if product.image_local:
            return product.image_local
    if fallback.is_file():
        return str(fallback)
    return ""


def _category_sort_key(category: Category) -> tuple[int, int | str, str]:
    try:
        return (0, int(category.id), category.name)
    except ValueError:
        return (1, category.sort_order, category.name)


def build_hub_summaries(
    categories: list[Category],
    products: list[Product],
) -> list[CategorySummary]:
    """Категории и количества с API; hero — «без категории» или первая категория каталога."""
    catalog: list[CategorySummary] = []
    seen: set[str] = set()

    for category in sorted(categories, key=_category_sort_key):
        if category.id in seen:
            continue
        seen.add(category.id)
        cat_products = [p for p in products if p.category_id == category.id]
        catalog.append(
            CategorySummary(
                id=category.id,
                name=category.name.upper(),
                product_count=len(cat_products),
                cover_image_local=_cover_for_products(
                    cat_products, _demo_fallback(category)
                ),
                hero=False,
                baked=False,
            )
        )

    misc_products = [p for p in products if p.category_id == MISC_HUB_ID]
    if misc_products:
        return [
            CategorySummary(
                id=MISC_HUB_ID,
                name=MISC_TITLE,
                product_count=len(misc_products),
                cover_image_local=(
                    str(HERO_BG)
                    if HERO_BG.is_file()
                    else _cover_for_products(misc_products, DEMO / "1.jpg")
                ),
                hero=True,
                baked=False,
            ),
            *catalog,
        ]

    if not catalog:
        return []

    first = catalog[0]
    hero = CategorySummary(
        id=first.id,
        name=first.name,
        product_count=first.product_count,
        cover_image_local=first.cover_image_local,
        hero=True,
        baked=False,
    )
    return [hero, *catalog[1:]]
