from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import requests

from src.core.config import ROOT, CrmConfig, Settings
from src.models.product import Category, Product

DEMO_PRODUCTS_DIR = ROOT / "assets" / "demo_products"

logger = logging.getLogger(__name__)


def _demo_image(product_id: str) -> str:
    path = DEMO_PRODUCTS_DIR / f"{product_id}.jpg"
    return str(path) if path.exists() else ""


class CRMClient(ABC):
    @abstractmethod
    def fetch_categories(self) -> list[Category]:
        ...

    @abstractmethod
    def fetch_products(self) -> list[Product]:
        ...

    @abstractmethod
    def is_online(self) -> bool:
        ...

    def download_image(self, product: Product, dest_dir: Path) -> str:
        """Скачивает фото в dest_dir. Возвращает локальный путь или пустую строку."""
        if not product.image_url:
            return ""
        dest = dest_dir / f"{product.id}.jpg"
        if dest.exists():
            return str(dest)
        try:
            resp = requests.get(product.image_url, timeout=15)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            return str(dest)
        except requests.RequestException as exc:
            logger.warning("Не удалось скачать фото %s: %s", product.id, exc)
            return ""


class MockCRMClient(CRMClient):
    """Демо-каталог для разработки без API."""

    def is_online(self) -> bool:
        return True

    def fetch_categories(self) -> list[Category]:
        return [
            Category("berry", "Ягода", 1),
            Category("dairy", "Молочка", 2),
            Category("honey", "Мёд", 3),
            Category("veg", "Овощи", 4),
            Category("other", "Прочее", 5),
        ]

    def fetch_products(self) -> list[Product]:
        items = [
            ("1", "berry", "Клубника", 450, 12, "кг"),
            ("2", "berry", "Малина", 520, 8, "кг"),
            ("3", "berry", "Черника", 680, 0, "кг"),
            ("4", "dairy", "Молоко 3,2%", 95, 30, "л"),
            ("5", "dairy", "Творог домашний", 180, 15, "шт"),
            ("6", "dairy", "Сметана 20%", 120, 20, "шт"),
            ("7", "honey", "Мёд липовый", 850, 10, "банка"),
            ("8", "honey", "Мёд гречишный", 780, 6, "банка"),
            ("9", "veg", "Картофель", 45, 50, "кг"),
            ("10", "veg", "Морковь", 55, 40, "кг"),
            ("11", "other", "Яйца С0", 110, 24, "десяток"),
            ("12", "other", "Зелень укроп", 60, 5, "пучок"),
        ]
        return [
            Product(
                pid,
                cat,
                name,
                price,
                image_local=_demo_image(pid),
                stock=stock,
                unit=unit,
            )
            for pid, cat, name, price, stock, unit in items
        ]


def _parse_category(row: dict[str, Any]) -> Category | None:
    cid = str(row.get("id", "")).strip()
    name = str(row.get("name", "")).strip()
    if not cid or not name:
        return None
    if row.get("is_active") is False:
        return None
    return Category(
        cid,
        name,
        int(row.get("sort_order") or 0),
    )


def _parse_product(row: dict[str, Any]) -> Product | None:
    pid = str(row.get("id", "")).strip()
    cat = str(row.get("category_id", "")).strip()
    name = str(row.get("name", "")).strip()
    if not pid or not cat or not name:
        return None
    if row.get("is_active") is False:
        return None
    try:
        price = float(row.get("price", 0))
    except (TypeError, ValueError):
        price = 0.0
    stock_raw = row.get("stock")
    stock = int(stock_raw) if stock_raw is not None else 999
    unit = str(row.get("unit") or "шт").strip()
    return Product(
        pid,
        cat,
        name,
        price,
        image_url=str(row.get("image_url") or ""),
        stock=stock,
        unit=unit,
        description=str(row.get("description") or ""),
    )


class HttpCRMClient(CRMClient):
    """HTTP CRM по docs/CRM_API_SPEC.md (Bearer + X-Kiosk-Id)."""

    def __init__(self, config: CrmConfig) -> None:
        if not config.base_url:
            raise ValueError("crm.base_url не задан (config или CRM_API_BASE_URL в .env)")
        self._config = config
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "KioskFarm/1.0",
            }
        )
        if config.api_key:
            self._session.headers["Authorization"] = f"Bearer {config.api_key}"
        if config.kiosk_id:
            self._session.headers["X-Kiosk-Id"] = config.kiosk_id

    def _url(self, path: str) -> str:
        base = self._config.base_url.rstrip("/")
        if not path.startswith("/"):
            path = "/" + path
        return base + path

    def _params(self) -> dict[str, str]:
        if self._config.kiosk_id:
            return {"kiosk_id": self._config.kiosk_id}
        return {}

    def _get_json(self, path: str) -> dict[str, Any]:
        resp = self._session.get(
            self._url(path),
            params=self._params(),
            timeout=self._config.timeout_sec,
        )
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise ValueError(f"Ожидался JSON object, получено: {type(data)}")
        return data

    def is_online(self) -> bool:
        try:
            r = self._session.get(
                self._url("/health"),
                timeout=self._config.timeout_sec,
            )
            return r.status_code < 500
        except requests.RequestException:
            return False

    def fetch_categories(self) -> list[Category]:
        if self._config.catalog_mode == "combined":
            data = self._get_json("/kiosk/catalog")
            rows = data.get("categories") or []
        else:
            try:
                data = self._get_json("/categories")
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    return self._categories_from_catalog_endpoint()
                raise
            rows = data.get("categories") or []

        cats = [_parse_category(r) for r in rows if isinstance(r, dict)]
        return [c for c in cats if c]

    def fetch_products(self) -> list[Product]:
        if self._config.catalog_mode == "combined":
            data = self._get_json("/kiosk/catalog")
        else:
            try:
                data = self._get_json("/products")
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    data = self._get_json("/kiosk/catalog")
                else:
                    raise

        rows = data.get("products") or []
        prods = [_parse_product(r) for r in rows if isinstance(r, dict)]
        return [p for p in prods if p]

    def _categories_from_catalog_endpoint(self) -> list[Category]:
        data = self._get_json("/kiosk/catalog")
        rows = data.get("categories") or []
        cats = [_parse_category(r) for r in rows if isinstance(r, dict)]
        return [c for c in cats if c]


def create_crm_client(settings: Settings) -> CRMClient:
    if settings.crm.use_mock:
        logger.info("CRM: режим mock-каталога")
        return MockCRMClient()
    if not settings.crm.api_key:
        logger.warning("CRM: use_mock=false, но CRM_API_KEY пуст — проверьте .env")
    logger.info("CRM: HTTP %s (kiosk_id=%s)", settings.crm.base_url, settings.crm.kiosk_id)
    return HttpCRMClient(settings.crm)
