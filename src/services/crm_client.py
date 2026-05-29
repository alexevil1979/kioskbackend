from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import requests

from src.core.config import CrmConfig, Settings
from src.models.product import Category, Product

logger = logging.getLogger(__name__)


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
        return [
            Product("1", "berry", "Клубника", 450, stock=12, unit="кг"),
            Product("2", "berry", "Малина", 520, stock=8, unit="кг"),
            Product("3", "berry", "Черника", 680, stock=0, unit="кг"),
            Product("4", "dairy", "Молоко 3,2%", 95, stock=30, unit="л"),
            Product("5", "dairy", "Творог домашний", 180, stock=15, unit="шт"),
            Product("6", "dairy", "Сметана 20%", 120, stock=20, unit="шт"),
            Product("7", "honey", "Мёд липовый", 850, stock=10, unit="банка"),
            Product("8", "honey", "Мёд гречишный", 780, stock=6, unit="банка"),
            Product("9", "veg", "Картофель", 45, stock=50, unit="кг"),
            Product("10", "veg", "Морковь", 55, stock=40, unit="кг"),
            Product("11", "other", "Яйца С0", 110, stock=24, unit="десяток"),
            Product("12", "other", "Зелень укроп", 60, stock=5, unit="пучок"),
        ]


class HttpCRMClient(CRMClient):
    """Реальный клиент — эндпоинты уточняются по API заказчика."""

    def __init__(self, config: CrmConfig) -> None:
        self._config = config
        self._session = requests.Session()
        if config.api_key:
            self._session.headers["Authorization"] = f"Bearer {config.api_key}"
        if config.kiosk_id:
            self._session.headers["X-Kiosk-Id"] = config.kiosk_id

    def is_online(self) -> bool:
        try:
            r = self._session.get(
                f"{self._config.base_url.rstrip('/')}/health",
                timeout=self._config.timeout_sec,
            )
            return r.status_code < 500
        except requests.RequestException:
            return False

    def fetch_categories(self) -> list[Category]:
        # TODO: заменить на реальный контракт
        raise NotImplementedError("Подключите эндпоинт категорий CRM")

    def fetch_products(self) -> list[Product]:
        raise NotImplementedError("Подключите эндпоинт товаров CRM")


def create_crm_client(settings: Settings) -> CRMClient:
    if settings.crm.use_mock:
        logger.info("CRM: режим mock-каталога")
        return MockCRMClient()
    logger.info("CRM: HTTP клиент %s", settings.crm.base_url)
    return HttpCRMClient(settings.crm)
