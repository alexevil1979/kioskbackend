from __future__ import annotations

import re

from src.models.product import Product
from src.ui import kolomna_strings as S


def _grade_key(name: str) -> str | None:
    n = name.lower()
    if "премиум" in n or "premium" in n:
        return "premium"
    if "стандарт" in n or "standard" in n:
        return "standard"
    if "варень" in n or "jam" in n:
        return "jam"
    return None


def _strip_pack_from_title(name: str) -> str:
    """Убираем фасовку из заголовка — она показывается отдельным chip (unit)."""
    stripped = re.sub(
        r"\s+ящик\s+\d+[,.]?\d*\s*кг\s*$",
        "",
        name.strip(),
        flags=re.I,
    ).strip()
    return stripped or name.strip()


def product_title(product: Product) -> str:
    key = _grade_key(product.name)
    if key == "premium":
        return S.GRADE_PREMIUM
    if key == "standard":
        return S.GRADE_STANDARD
    if key == "jam":
        return S.GRADE_JAM
    return _strip_pack_from_title(product.name)


def product_description(product: Product) -> str:
    if product.description.strip():
        return product.description.strip()
    key = _grade_key(product.name)
    if key == "premium":
        return S.GRADE_DESC_PREMIUM
    if key == "standard":
        return S.GRADE_DESC_STANDARD
    if key == "jam":
        return S.GRADE_DESC_JAM
    return ""


def product_pack_label(product: Product) -> str:
    unit = product.unit.strip()
    if unit and unit.lower() not in ("шт", "pcs"):
        return unit
    m = re.search(r"ящик\s+(\d+[,.]?\d*\s*кг)", product.name, re.I)
    if m:
        return f"ящик {m.group(1).replace('.', ',')}"
    m = re.search(r"(\d+[,.]?\d*\s*кг)", product.name, re.I)
    if m:
        return f"ящик {m.group(1).replace('.', ',')}"
    return "ящик 2,5 кг"


def product_unit_word(product: Product) -> str:
    if product.unit.lower() in ("person", "чел", "человек"):
        return S.PEOPLE_WORD
    return S.PACKS_WORD


def product_per_word(product: Product) -> str:
    if product.unit.lower() in ("person", "чел", "человек"):
        return S.PER_PERSON
    return S.PER_PACK


def tour_cart_guests_label(adults: int, kids: int) -> str:
    from src.ui import kolomna_strings as S

    adults = max(1, adults)
    kids = max(0, kids)
    if kids > 0:
        return S.CART_TOUR_GUESTS.format(adults=adults, kids=kids, free=S.TOUR_GUEST_FREE.lower())
    return S.CART_TOUR_GUESTS_ADULTS.format(adults=adults)


def full_product_name(product: Product) -> str:
    cat = product.category_name.strip()
    title = product_title(product)
    if cat:
        return f"{cat} · {title}"
    return title


def n_items_label(count: int) -> str:
    from src.ui.kolomna_i18n import n_items_label as _n_items

    return _n_items(count)


def fmt_price(value: float) -> str:
    if value == int(value):
        s = f"{int(value)}"
    else:
        s = f"{value:.2f}".replace(".", ",")
    parts: list[str] = []
    while len(s) > 3:
        parts.insert(0, s[-3:])
        s = s[:-3]
    if s:
        parts.insert(0, s)
    return "\u202f".join(parts)
