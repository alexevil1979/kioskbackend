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


def hub_slot_index_for_category(categories: list[Category], category_id: str) -> int:
    """Индекс 0–2 (клубника / голубика / малина) как в хабе."""
    api_cats = sorted(categories, key=_category_sort_key)
    for i, cat in enumerate(api_cats[:3]):
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


def build_kolomna_hub_tiles(categories: list[Category]) -> list[KolomnaHubTile]:
    """4 карточки референса; 01–03 → первые 3 раздела API."""
    api_cats = sorted(categories, key=_category_sort_key)
    tiles: list[KolomnaHubTile] = []
    berry_idx = 0
    for i, (num, _label, accent, edge, img_name, is_service) in enumerate(_SLOT_DEFS):
        label = hub_label_for_slot(i)
        cat_id: str | None = None
        if not is_service:
            if berry_idx < len(api_cats):
                cat_id = api_cats[berry_idx].id
            berry_idx += 1
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
    """Товар экскурсии: 4-й раздел API или заглушка референса."""
    if len(categories) >= 4:
        cat = sorted(categories, key=_category_sort_key)[3]
        cat_products = [p for p in products if p.category_id == cat.id and p.in_stock]
        if cat_products:
            return cat_products[0]
    return Product(
        id="kolomna-tour-walk",
        category_id=KOLOMNA_TOURS_ID,
        name="Экскурсия по ферме",
        price_rub=2500,
        unit="person",
        category_name="Экскурсии",
    )
