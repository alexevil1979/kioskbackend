from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.core.config import Settings
from src.models.product import Category, Product
from src.services.crm_client import CRMClient, create_crm_client

logger = logging.getLogger(__name__)


class CatalogStore(QObject):
    """Хранилище каталога с периодическим обновлением."""

    updated = pyqtSignal()
    offline_changed = pyqtSignal(bool)

    def __init__(self, settings: Settings, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self._crm: CRMClient = create_crm_client(settings)
        self._categories: list[Category] = []
        self._products: list[Product] = []
        self._offline = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        interval = max(15, settings.catalog.poll_interval_sec) * 1000
        self._timer.start(interval)

    @property
    def categories(self) -> list[Category]:
        return sorted(self._categories, key=lambda c: c.sort_order)

    @property
    def products(self) -> list[Product]:
        return self._products

    @property
    def is_offline(self) -> bool:
        return self._offline

    def product_by_id(self, product_id: str) -> Product | None:
        for p in self._products:
            if p.id == product_id:
                return p
        return None

    def products_for_category(self, category_id: str | None) -> list[Product]:
        if not category_id:
            return [p for p in self._products if p.in_stock]
        return [p for p in self._products if p.category_id == category_id]

    def refresh(self) -> None:
        online = self._crm.is_online()
        if online != (not self._offline):
            self._offline = not online
            self.offline_changed.emit(self._offline)
            logger.warning("Каталог offline=%s", self._offline)

        if not online and self._products:
            return

        try:
            cats = self._crm.fetch_categories()
            prods = self._crm.fetch_products()
            media_dir = self._settings.media_path
            for p in prods:
                local = self._crm.download_image(p, media_dir)
                if local:
                    p.image_local = local
            self._categories = cats
            self._products = prods
            self._offline = False
            self.updated.emit()
            logger.debug("Каталог обновлён: %d товаров", len(prods))
        except Exception as exc:
            logger.exception("Ошибка обновления каталога: %s", exc)
            if not self._products:
                self._offline = True
                self.offline_changed.emit(True)
