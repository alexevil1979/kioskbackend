from __future__ import annotations

import logging
from datetime import datetime

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.core.config import Settings
from src.models.category_hub import CategorySummary
from src.models.product import Category, Product
from src.services.crm_client import CRMClient, create_crm_client
from src.services.product_image_cache import ProductImageCache

logger = logging.getLogger(__name__)


class CatalogStore(QObject):
    """Хранилище каталога с периодическим обновлением."""

    updated = pyqtSignal()
    offline_changed = pyqtSignal(bool)
    api_online_changed = pyqtSignal(bool)

    def __init__(self, settings: Settings, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self._crm: CRMClient = create_crm_client(settings)
        self._image_cache = ProductImageCache(settings.media_path)
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

    @property
    def is_api_online(self) -> bool:
        return self._api_online

    @property
    def crm(self) -> CRMClient:
        return self._crm

    def reconnect_crm(self) -> None:
        self._crm = create_crm_client(self._settings)

    def product_by_id(self, product_id: str) -> Product | None:
        for p in self._products:
            if p.id == product_id:
                return p
        return None

    def products_for_category(self, category_id: str | None) -> list[Product]:
        if not category_id:
            return [p for p in self._products if p.in_stock]
        key = str(category_id)
        return [
            p
            for p in self._products
            if str(p.category_id) == key and p.in_stock
        ]

    def category_summaries(self) -> list[CategorySummary]:
        from src.ui.katusha_hub_catalog import build_hub_summaries

        return build_hub_summaries(self._categories, self._products)

    def kolomna_hub_tiles(self):
        from src.ui.kolomna_catalog import build_kolomna_hub_tiles

        return build_kolomna_hub_tiles(self._categories)

    def products_for_hub(self, hub_id: str) -> list[Product]:
        from src.ui.katusha_hub_catalog import MISC_HUB_ID

        if hub_id == MISC_HUB_ID:
            return [
                p
                for p in self._products
                if p.category_id == MISC_HUB_ID and p.in_stock
            ]
        return self.products_for_category(hub_id)

    def refresh(self) -> None:
        logger.debug("Каталог: обновление…")
        try:
            online = self._crm.is_online()
        except Exception as exc:
            logger.error("Каталог: проверка /health не удалась: %s", exc, exc_info=True)
            online = False

        self._set_api_online(online)

        if not online:
            if not self._products:
                self._set_offline(True, "API недоступен, каталог пуст")
            else:
                logger.warning("Каталог: API offline, показываем кэш (%d товаров)", len(self._products))
            return

        try:
            clear = getattr(self._crm, "clear_catalog_cache", None)
            if callable(clear):
                clear()
            cats = self._crm.fetch_categories()
            prods = self._crm.fetch_products()
        except Exception as exc:
            logger.error("Каталог: ошибка загрузки с API: %s", exc, exc_info=True)
            if not self._products:
                self._set_offline(True, "не удалось загрузить каталог")
            return

        if not prods:
            logger.warning(
                "Каталог: API ответил успешно, но товаров 0 (категорий %d)",
                len(cats),
            )

        self._categories = cats
        self._products = prods
        from src.ui.kolomna_product_meta import set_catalog_from_live_api

        set_catalog_from_live_api(
            not self._settings.crm.use_mock and bool(self._settings.crm.api_key.strip())
        )
        self._apply_purchase_test_mode(self._products)
        img_stats = self._attach_product_images(self._products)
        self._set_offline(False)
        self._write_products_table_log(prods)

        in_stock = sum(1 for p in prods if p.in_stock)
        with_local = sum(1 for p in prods if p.image_local)
        logger.info(
            "Каталог загружен: %d категорий, %d товаров (%d в наличии), фото локально %d",
            len(cats),
            len(prods),
            in_stock,
            with_local,
        )
        if img_stats.downloaded or img_stats.updated:
            logger.info(
                "Фото каталога: скачано %d, обновлено (новое имя) %d, из кэша %d, ошибок %d",
                img_stats.downloaded,
                img_stats.updated,
                img_stats.reused,
                img_stats.failed,
            )
        self.updated.emit()

    def _attach_product_images(self, products: list[Product]):
        from src.ui.kolomna_catalog import is_tour_product
        from src.ui.product_image_display import use_api_product_images
        from src.services.product_image_cache import ImageCacheStats

        if use_api_product_images():
            stats = self._image_cache.attach_all(products)
        else:
            for product in products:
                product.image_local = ""
            stats = ImageCacheStats()

        self._attach_ticket_images(products)
        return stats

    def _attach_ticket_images(self, products: list[Product]) -> None:
        """Фото билета с API кэшируем всегда — и как заглушку на будущее."""
        from src.ui.kolomna_catalog import is_tour_product

        for product in products:
            if not is_tour_product(product) or not product.image_url:
                continue
            path = self._image_cache.resolve(product)
            if path:
                product.image_local = path
                self._image_cache.update_ticket_placeholder(path)
            break

    def _apply_purchase_test_mode(self, products: list[Product]) -> None:
        cfg = self._settings.catalog
        if not cfg.purchase_test_mode:
            return
        qty = max(1, int(cfg.test_stock_qty))
        for p in products:
            p.is_available = True
            p.stock = qty
        logger.info(
            "Каталог: TEST PURCHASE MODE включён — всем товарам stock=%d, is_available=true",
            qty,
        )

    def _write_products_table_log(self, products: list[Product]) -> None:
        """Пишет удобную табличку товаров API в отдельный файл logs/."""
        out = self._settings.log_path.parent / "catalog_products_table.log"
        out.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        columns = (
            ("id", 6),
            ("category_id", 12),
            ("category_name", 24),
            ("name", 38),
            ("description", 32),
            ("price", 8),
            ("stock", 7),
            ("unit", 8),
            ("in_stock", 8),
            ("image_url", 44),
        )

        def cell(value: object, width: int) -> str:
            text = str(value or "")
            if len(text) > width:
                return text[: max(1, width - 1)] + "…"
            return text.ljust(width)

        header = " | ".join(cell(title, width) for title, width in columns)
        sep = "-+-".join("-" * width for _title, width in columns)
        lines = [
            f"[{stamp}] products={len(products)}",
            header,
            sep,
        ]
        for p in products:
            row = (
                p.id,
                p.category_id,
                p.category_name,
                p.name,
                p.description,
                f"{p.price_rub:.2f}",
                p.stock,
                p.unit,
                "yes" if p.in_stock else "no",
                p.image_url,
            )
            lines.append(
                " | ".join(
                    cell(value, width) for value, (_title, width) in zip(row, columns)
                )
            )
        lines.append("")

        out.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Каталог: таблица товаров записана в %s", out)

    def _set_offline(self, offline: bool, reason: str = "") -> None:
        if offline and reason:
            logger.warning("Каталог offline: %s", reason)
        if offline != self._offline:
            self._offline = offline
            self.offline_changed.emit(self._offline)

    def _set_api_online(self, online: bool) -> None:
        if online != self._api_online:
            self._api_online = online
            self.api_online_changed.emit(online)
