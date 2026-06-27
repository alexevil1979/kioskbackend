from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtGui import QPixmap

from src.core.config import ROOT
from src.models.product import Category, Product
from src.ui.image_utils import load_pixmap
from src.ui.katusha_hub_catalog import _category_sort_key
from src.ui.kolomna_i18n import hub_label_for_slot

KOLOMNA_TOURS_ID = "__kolomna_tours__"


@dataclass(frozen=True)
class KolomnaApiProductSection:
    """Подраздел Katusha API: product_id → слот хаба Kolomna."""

    category_id: str
    display_name: str
    hub_slot: int | None
    is_tickets: bool


# product_id с API — линейка товара (клубника / голубика / малина / экскурсии), не variant_id.
KOLOMNA_API_SECTIONS: dict[int, KolomnaApiProductSection] = {
    6: KolomnaApiProductSection("6", "Клубника", 0, False),
    33: KolomnaApiProductSection("33", "Голубика", 1, False),
    7: KolomnaApiProductSection("7", "Малина", 2, False),
    84: KolomnaApiProductSection("84", "Агротуризм", 3, True),
}


def kolomna_section_for_api_product_id(api_product_id: int) -> KolomnaApiProductSection | None:
    if api_product_id <= 0:
        return None
    return KOLOMNA_API_SECTIONS.get(api_product_id)


def is_kolomna_tickets_api_product_id(api_product_id: int) -> bool:
    section = kolomna_section_for_api_product_id(api_product_id)
    return bool(section and section.is_tickets)


def kolomna_section_for_category_id(category_id: str) -> KolomnaApiProductSection | None:
    for section in KOLOMNA_API_SECTIONS.values():
        if section.category_id == category_id:
            return section
    return None

_TICKETS_CATEGORY_NEEDLES: tuple[str, ...] = (
    "билет",
    "ticket",
    "агротуризм",
    "экскурс",
    "tour",
    "excursion",
)


def is_tickets_category(category: Category) -> bool:
    """Раздел API с билетами / экскурсиями — не ягодный слот хаба."""
    section = kolomna_section_for_category_id(category.id)
    if section is not None:
        return section.is_tickets
    hay = f"{category.id} {category.name}".lower()
    return any(needle in hay for needle in _TICKETS_CATEGORY_NEEDLES)


def kolomna_berry_categories(categories: list[Category]) -> list[Category]:
    """Разделы для слотов 01–03 хаба (без билетов), по hub_slot из product_id."""
    berries = [c for c in categories if not is_tickets_category(c)]

    def _berry_sort_key(category: Category) -> tuple[int, int | str, str]:
        section = kolomna_section_for_category_id(category.id)
        if section is not None and section.hub_slot is not None and section.hub_slot < 3:
            return (0, section.hub_slot, category.name)
        return (1, *_category_sort_key(category)[1:])

    return sorted(berries, key=_berry_sort_key)[:3]


def kolomna_tickets_category(categories: list[Category]) -> Category | None:
    for cat in sorted(categories, key=_category_sort_key):
        if is_tickets_category(cat):
            return cat
    return None


def kolomna_tickets_category_id(categories: list[Category]) -> str | None:
    cat = kolomna_tickets_category(categories)
    return cat.id if cat else None


def is_tour_product(product: Product) -> bool:
    if product.is_excursion:
        return True
    if is_kolomna_tickets_api_product_id(product.api_product_id):
        return True
    section = kolomna_section_for_category_id(product.category_id)
    if section is not None and section.is_tickets:
        return True
    if product.category_id == KOLOMNA_TOURS_ID:
        return True
    if product.id in ("kolomna-tour-walk", "tour-walk"):
        return True
    hay = f"{product.category_id} {product.category_name} {product.name} {product.unit}".lower()
    if any(needle in hay for needle in _TICKETS_CATEGORY_NEEDLES):
        return True
    unit = product.unit.strip().lower()
    if unit in ("билет", "ticket"):
        return True
    if unit in ("person", "чел", "человек") and "экскурс" in product.name.lower():
        return True
    return False


def kolomna_products_for_category(
    categories: list[Category],
    products: list[Product],
    category_id: str,
) -> list[Product]:
    """Товары раздела для Kolomna: билеты не попадают в ягодные меню."""
    if category_id == KOLOMNA_TOURS_ID:
        tickets_cat = kolomna_tickets_category(categories)
        if tickets_cat:
            return [p for p in products if p.category_id == tickets_cat.id]
        return [p for p in products if is_tour_product(p)]
    return [
        p
        for p in products
        if p.category_id == category_id and not is_tour_product(p)
    ]

KOLOMNA_CARD_ACCENTS: tuple[str, ...] = (
    "#D9143A",
    "#3F5E96",
    "#A8123E",
    "#1F4D2A",
)

PIC_DIR = ROOT / "pic"
PIC_FALLBACK_DIRS: tuple[Path, ...] = (
    PIC_DIR,
    ROOT / "assets" / "kolomna" / "img",
)


def _resolve_pic(name: str) -> Path | None:
    for base in PIC_FALLBACK_DIRS:
        path = base / name
        if path.is_file():
            return path
    return None

_SLOT_DEFS: tuple[tuple[str, str, str, str, str | None, bool], ...] = (
    ("01", "Клубника", "#D9143A", "#143821", "berry-strawberry.webp", False),
    ("02", "Голубика", "#3F5E96", "#22324F", "berry-blueberry.webp", False),
    ("03", "Малина", "#A8123E", "#143821", "berry-raspberry.webp", False),
    ("04", "Экскурсии", "#1F4D2A", "#143821", None, True),
)


@dataclass(frozen=True)
class KolomnaHubTile:
    """Фиксированная карточка хаба Kolomna (01–04)."""

    num: str
    label: str
    accent: str
    edge: str
    image_path: Path | None
    is_service: bool
    category_id: str | None
    slot_index: int

    @property
    def navigation_id(self) -> str:
        if self.is_service:
            return KOLOMNA_TOURS_ID
        return self.category_id or ""


def kolomna_card_accent(index: int) -> str:
    return KOLOMNA_CARD_ACCENTS[index % len(KOLOMNA_CARD_ACCENTS)]


_BERRY_PLACEHOLDER_NEEDLES: tuple[tuple[str, str], ...] = (
    ("клубник", "berry-strawberry.webp"),
    ("strawber", "berry-strawberry.webp"),
    ("голубик", "berry-blueberry.webp"),
    ("blueber", "berry-blueberry.webp"),
    ("малин", "berry-raspberry.webp"),
    ("raspber", "berry-raspberry.webp"),
)


def kolomna_ticket_image_path() -> Path | None:
    """Сохранённое фото билета с API (media/products/kolomna_ticket_placeholder.jpg)."""
    from src.services.product_image_cache import ProductImageCache

    return ProductImageCache.find_ticket_placeholder()


def kolomna_product_placeholder_path(product: Product) -> Path | None:
    """Заглушка товара: ягода раздела из pic/, билет — кэш с API, иначе demo_products."""
    if is_tour_product(product):
        ticket = kolomna_ticket_image_path()
        if ticket is not None:
            return ticket
    haystack = f"{product.category_name} {product.name} {product.category_id}".lower()
    for needle, pic_name in _BERRY_PLACEHOLDER_NEEDLES:
        if needle in haystack:
            path = _resolve_pic(pic_name)
            if path is not None:
                return path
    demo = ROOT / "assets" / "demo_products"
    for i in range(1, 13):
        path = demo / f"{i}.jpg"
        if path.is_file():
            return path
    return None


def hub_slot_index_for_category(categories: list[Category], category_id: str) -> int:
    """Индекс 0–2 (клубника / голубика / малина) как в хабе."""
    section = kolomna_section_for_category_id(category_id)
    if section is not None and section.hub_slot is not None and section.hub_slot < 3:
        return section.hub_slot
    for i, cat in enumerate(kolomna_berry_categories(categories)):
        if cat.id == category_id:
            return i
    return 0


def hub_berry_pixmap(slot_index: int) -> QPixmap:
    """Ягода раздела из pic/ (berry-strawberry.webp и т.д.) — для flyBerryToCart."""
    if not (0 <= slot_index < len(_SLOT_DEFS)):
        return QPixmap()
    img_name = _SLOT_DEFS[slot_index][4]
    if not img_name:
        return QPixmap()
    path = _resolve_pic(img_name)
    if path is None:
        return QPixmap()
    pix = load_pixmap(path)
    return pix if not pix.isNull() else QPixmap()


def _berry_category_for_hub_slot(
    categories: list[Category], hub_slot: int
) -> Category | None:
    berries = kolomna_berry_categories(categories)
    mapped = [c for c in berries if kolomna_section_for_category_id(c.id) is not None]
    if mapped:
        for cat in mapped:
            section = kolomna_section_for_category_id(cat.id)
            if section is not None and section.hub_slot == hub_slot:
                return cat
        return None
    if hub_slot < len(berries):
        return berries[hub_slot]
    return None


def build_kolomna_hub_tiles(categories: list[Category]) -> list[KolomnaHubTile]:
    """4 карточки референса; 01–03 → ягодные разделы API (без билетов), 04 → билеты."""
    tickets_cat = kolomna_tickets_category(categories)
    tiles: list[KolomnaHubTile] = []
    for i, (num, _label, accent, edge, img_name, is_service) in enumerate(_SLOT_DEFS):
        label = hub_label_for_slot(i)
        cat_id: str | None = None
        if is_service:
            cat_id = tickets_cat.id if tickets_cat else None
        else:
            berry_cat = _berry_category_for_hub_slot(categories, i)
            cat_id = berry_cat.id if berry_cat else None
        img_path = _resolve_pic(img_name) if img_name else None
        tiles.append(
            KolomnaHubTile(
                num=num,
                label=label,
                accent=accent,
                edge=edge,
                image_path=img_path,
                is_service=is_service,
                category_id=cat_id,
                slot_index=i,
            )
        )
    return tiles


def resolve_tour_product(categories: list[Category], products: list[Product]) -> Product:
    """Товар билета/экскурсии из раздела API с билетами."""
    excursion = [
        p for p in products if p.is_excursion and p.is_purchasable
    ]
    if excursion:
        return excursion[0]
    tickets_cat = kolomna_tickets_category(categories)
    if tickets_cat:
        cat_products = [
            p for p in products if p.category_id == tickets_cat.id and p.in_stock
        ]
        if cat_products:
            return cat_products[0]
    tour_products = [p for p in products if is_tour_product(p) and p.in_stock]
    if tour_products:
        return tour_products[0]
    return Product(
        id="kolomna-tour-walk",
        category_id=KOLOMNA_TOURS_ID,
        name="Экскурсия по ферме",
        price_rub=2500,
        unit="person",
        category_name="Экскурсии",
    )
