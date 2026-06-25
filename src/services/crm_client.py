from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from src.core.config import ROOT, CrmConfig, PaymentConfig, Settings
from src.services.payment_api_trace import PaymentQrApiTrace
from src.models.order import OrderCreateResult, OrderReceiptResult, OrderStatusResult
from src.models.product import Category, Product

DEMO_PRODUCTS_DIR = ROOT / "assets" / "demo_products"
KOLOMNA_PIC = ROOT / "pic"


def _kolomna_pic(name: str) -> str:
    path = KOLOMNA_PIC / name
    return str(path) if path.is_file() else ""


def _kolomna_mock_catalog() -> tuple[list[Category], list[Product]]:
    """Данные window.KIOSK из offline-референса."""
    cats = [
        Category("strawberry", "Клубника", 1),
        Category("blueberry", "Голубика", 2),
        Category("raspberry", "Малина", 3),
        Category("tours", "Экскурсии", 4),
    ]
    img_str = _kolomna_pic("berry-strawberry.webp")
    img_blu = _kolomna_pic("berry-blueberry.webp")
    img_ras = _kolomna_pic("berry-raspberry.webp")
    rows: list[tuple[str, str, str, float, str, str, bool]] = [
        ("str-prem", "strawberry", "Премиум", 2375, "2,5 кг", img_str, False),
        ("str-std", "strawberry", "Стандарт", 1900, "2,5 кг", img_str, False),
        ("str-jam", "strawberry", "На варенье", 2250, "5 кг", img_str, False),
        ("blu-prem", "blueberry", "Премиум", 3200, "2,5 кг", img_blu, True),
        ("blu-std", "blueberry", "Стандарт", 2600, "2,5 кг", img_blu, True),
        ("blu-jam", "blueberry", "На варенье", 3400, "5 кг", img_blu, True),
        ("ras-prem", "raspberry", "Премиум", 2900, "2,5 кг", img_ras, True),
        ("ras-std", "raspberry", "Стандарт", 2300, "2,5 кг", img_ras, True),
        ("ras-jam", "raspberry", "На варенье", 2700, "5 кг", img_ras, True),
        ("tour-walk", "tours", "Экскурсия по ферме", 2500, "person", img_str, True),
    ]
    products = [
        Product(
            pid,
            cat_id,
            name,
            price,
            image_local=img,
            stock=99,
            unit=unit,
            category_name=next(c.name for c in cats if c.id == cat_id),
            description="",
        )
        for pid, cat_id, name, price, unit, img, _ph in rows
    ]
    return cats, products


logger = logging.getLogger(__name__)


def _demo_image(product_id: str) -> str:
    path = DEMO_PRODUCTS_DIR / f"{product_id}.jpg"
    return str(path) if path.exists() else ""


def _is_katusha_kiosk_api(base_url: str) -> bool:
    return "/api/external/kiosk" in (base_url or "")


def _extract_qr_fields(data: dict[str, Any]) -> tuple[str, str]:
    """qr_code_payload / payment_url для генерации QR; qr_code_image — SVG/PNG от API."""
    payload = str(
        data.get("qr_code_payload")
        or data.get("qrCodePayload")
        or ""
    ).strip()
    if not payload:
        payload = str(
            data.get("payment_url")
            or data.get("paymentUrl")
            or ""
        ).strip()
    image = str(data.get("qr_code_image") or data.get("qrCodeImage") or "").strip()
    return payload, image


def _http_error_detail(exc: requests.HTTPError) -> str:
    resp = exc.response
    if resp is None:
        return str(exc)
    body = (resp.text or "")[:500].replace("\n", " ")
    return f"HTTP {resp.status_code} {resp.request.method} {resp.url} — {body}"


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

    @property
    def supports_kiosk_orders(self) -> bool:
        return False

    def create_order(
        self,
        items: list[dict[str, Any]],
        payment_method: str,
        kiosk_order_id: str | None = None,
    ) -> OrderCreateResult:
        raise NotImplementedError("Заказы через API не поддерживаются этим CRM-клиентом")

    def get_order_status(self, order_id: int) -> OrderStatusResult:
        raise NotImplementedError

    def get_order_receipt(self, order_id: int) -> OrderReceiptResult:
        raise NotImplementedError


class MockCRMClient(CRMClient):
    def __init__(self, *, kolomna: bool = False) -> None:
        self._kolomna = kolomna

    def is_online(self) -> bool:
        return True

    def fetch_categories(self) -> list[Category]:
        if self._kolomna:
            return _kolomna_mock_catalog()[0]
        return [
            Category("berry", "Ягода", 1),
            Category("dairy", "Молочка", 2),
            Category("honey", "Мёд", 3),
            Category("veg", "Овощи", 4),
            Category("other", "Прочее", 5),
        ]

    def fetch_products(self) -> list[Product]:
        if self._kolomna:
            return _kolomna_mock_catalog()[1]
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
    return Category(cid, name, int(row.get("sort_order") or 0))


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
        is_available=bool(row.get("is_available", True)),
        producer_name=str(row.get("producer_name") or ""),
    )


def _parse_katusha_product(row: dict[str, Any]) -> Product | None:
    pid = str(row.get("id", "")).strip()
    base_name = str(row.get("name") or "").strip()
    variant_name = str(row.get("variant_name") or "").strip()
    if not base_name:
        base_name = variant_name
        variant_name = ""
    if not pid or not base_name:
        return None

    api_product_id = int(row.get("product_id") or 0)
    variant_id = int(row.get("variant_id") or 0)
    if not api_product_id or not variant_id:
        parts = pid.split("_", 1)
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            api_product_id = api_product_id or int(parts[0])
            variant_id = variant_id or int(parts[1])

    from src.ui.kolomna_catalog import kolomna_section_for_api_product_id

    section = kolomna_section_for_api_product_id(api_product_id)
    if section is not None:
        category_id = section.category_id
        cat_name = section.display_name
    else:
        cat_id = row.get("main_category_id")
        cat_name = str(row.get("main_category_name") or "").strip()
        if cat_id is not None:
            category_id = str(cat_id)
        elif cat_name:
            category_id = f"n:{cat_name}"
        else:
            category_id = "misc"

    if row.get("is_weight_variable"):
        try:
            price = float(row.get("price_per_weight_unit") or row.get("price") or 0)
        except (TypeError, ValueError):
            price = 0.0
        unit = str(row.get("weight_unit") or row.get("unit") or "100 г").strip()
    else:
        try:
            price = float(row.get("price") or 0)
        except (TypeError, ValueError):
            price = 0.0
        unit = str(row.get("unit") or "шт").strip()

    try:
        stock = int(row.get("available_quantity") or 0)
    except (TypeError, ValueError):
        stock = 0

    image_url = str(row.get("image") or "").strip()
    if not image_url:
        for img in row.get("images") or []:
            if isinstance(img, dict) and img.get("url"):
                image_url = str(img["url"])
                if img.get("is_primary"):
                    break

    producer = row.get("producer")
    producer_name = ""
    if isinstance(producer, dict):
        producer_name = str(producer.get("name") or "").strip()

    return Product(
        pid,
        category_id,
        base_name,
        price,
        image_url=image_url,
        stock=stock,
        unit=unit,
        description=str(row.get("description") or ""),
        category_name=cat_name,
        is_available=bool(row.get("is_available", True)),
        producer_name=producer_name,
        api_product_id=api_product_id,
        variant_id=variant_id,
        variant_name=variant_name,
        is_weight_variable=bool(row.get("is_weight_variable")),
    )


def _katusha_categories_from_rows(rows: list[dict[str, Any]]) -> list[Category]:
    from src.ui.kolomna_catalog import kolomna_section_for_api_product_id

    seen: dict[str, Category] = {}
    order = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        api_product_id = int(row.get("product_id") or 0)
        section = kolomna_section_for_api_product_id(api_product_id)
        if section is not None:
            if section.category_id in seen:
                continue
            sort_order = section.hub_slot if section.hub_slot is not None else order
            seen[section.category_id] = Category(
                section.category_id,
                section.display_name,
                sort_order,
            )
            order += 1
            continue
        cid = row.get("main_category_id")
        cname = row.get("main_category_name")
        if cid is None and not cname:
            continue
        key = str(cid) if cid is not None else f"n:{cname}"
        if key in seen:
            continue
        order += 1
        seen[key] = Category(
            str(cid) if cid is not None else "misc",
            str(cname or "Прочее"),
            order,
        )
    if not seen:
        return [Category("misc", "Каталог", 0)]
    return list(seen.values())


class HttpCRMClient(CRMClient):
    """HTTP: Katusha Kiosk API (X-Kiosk-Key + /catalog) или legacy CRM."""

    def __init__(self, config: CrmConfig, payment: PaymentConfig | None = None) -> None:
        if not config.base_url:
            raise ValueError("crm.base_url не задан (config или KIOSK_API_BASE_URL в .env)")
        if not config.api_key:
            raise ValueError("crm.api_key не задан (KIOSK_API_KEY в .env)")

        self._config = config
        pay = payment or PaymentConfig()
        self._qr_trace = PaymentQrApiTrace(
            enabled=pay.qr_api_trace_enabled,
            file_path=ROOT / pay.qr_api_trace_file,
        )
        self._katusha = _is_katusha_kiosk_api(config.base_url)
        self._catalog_cache: tuple[list[Category], list[Product]] | None = None

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "KioskKatusha/1.0",
            }
        )
        if self._katusha:
            self._session.headers["X-Kiosk-Key"] = config.api_key
            logger.info("CRM: Katusha Kiosk API, заголовок X-Kiosk-Key")
        else:
            self._session.headers["Authorization"] = f"Bearer {config.api_key}"
            if config.kiosk_id:
                self._session.headers["X-Kiosk-Id"] = config.kiosk_id
            logger.info("CRM: legacy Bearer (kiosk_id=%s)", config.kiosk_id)

    def clear_catalog_cache(self) -> None:
        """Сброс кэша /catalog перед очередным poll."""
        self._catalog_cache = None

    def _url(self, path: str) -> str:
        base = self._config.base_url.rstrip("/")
        if not path.startswith("/"):
            path = "/" + path
        return base + path

    def _params(self) -> dict[str, str]:
        if self._katusha:
            return {}
        if self._config.kiosk_id:
            return {"kiosk_id": self._config.kiosk_id}
        return {}

    @property
    def supports_kiosk_orders(self) -> bool:
        return self._katusha

    def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = self._url(path)
        params = self._params()
        trace = self._qr_trace.should_trace_post(path, body)
        if trace:
            self._qr_trace.log_request("POST", url, params=params or None, body=body)
        try:
            resp = self._session.post(
                url,
                json=body,
                params=params,
                timeout=self._config.timeout_sec,
            )
            raw = resp.text or ""
            if trace:
                self._qr_trace.log_response("POST", url, resp.status_code, raw)
            resp.raise_for_status()
        except requests.HTTPError as exc:
            if trace:
                r = exc.response
                self._qr_trace.log_error(
                    "POST",
                    url,
                    _http_error_detail(exc),
                    status_code=r.status_code if r is not None else None,
                    raw_body=(r.text if r is not None else None),
                )
            logger.error("CRM POST неуспешен: %s", _http_error_detail(exc))
            raise
        except requests.RequestException as exc:
            if trace:
                self._qr_trace.log_error("POST", url, str(exc))
            logger.error("CRM POST сеть/таймаут %s: %s", url, exc)
            raise

        try:
            data = resp.json()
        except ValueError as exc:
            logger.error("CRM POST невалидный JSON %s: %s", url, exc)
            raise

        if not isinstance(data, dict):
            raise ValueError(f"Ожидался JSON object, получено: {type(data)}")
        return data

    def create_order(
        self,
        items: list[dict[str, Any]],
        payment_method: str,
        kiosk_order_id: str | None = None,
    ) -> OrderCreateResult:
        if not self._katusha:
            return super().create_order(items, payment_method, kiosk_order_id)

        body: dict[str, Any] = {
            "items": items,
            "payment_method": payment_method,
        }
        if kiosk_order_id:
            body["kiosk_order_id"] = kiosk_order_id

        data = self._post_json("/order/create", body)
        order_id = int(data.get("order_id") or 0)
        if not order_id:
            raise ValueError(f"CRM /order/create: нет order_id в ответе: {data}")

        payload, qr_image = _extract_qr_fields(data)
        if payment_method == "qr_sbp" and not payload and not qr_image:
            payload, qr_image = self._wait_for_sbp_qr(order_id, data)

        if payment_method == "qr_sbp" and not payload and not qr_image:
            logger.error(
                "CRM: сервер не вернул QR для заказа %s, ответ create=%s",
                order_id,
                {k: data.get(k) for k in ("order_id", "payment_id", "payment_method", "total_amount")},
            )
            raise ValueError(
                f"Сервер не выдал QR СБП для заказа {order_id}. "
                "Проверьте настройки СБП на точке в админке Катюша."
            )

        result = OrderCreateResult(
            order_id=order_id,
            total_amount=float(data.get("total_amount") or 0),
            payment_method=str(data.get("payment_method") or payment_method),
            payment_id=str(data.get("payment_id") or ""),
            qr_code_payload=payload,
            qr_code_image=qr_image,
            expires_in_seconds=int(data.get("expires_in_seconds") or 300),
        )
        logger.info(
            "CRM /order/create: order_id=%s total=%.2f method=%s qr=%s",
            result.order_id,
            result.total_amount,
            result.payment_method,
            "да" if (payload or qr_image) else "нет",
        )
        return result

    def _wait_for_sbp_qr(
        self, order_id: int, create_data: dict[str, Any]
    ) -> tuple[str, str]:
        """Повторный запрос GET /order/{id}/payment — QR иногда приходит с задержкой."""
        delays = (0.5, 1.0, 2.0)
        for attempt, delay in enumerate(delays, start=1):
            time.sleep(delay)
            try:
                pay_data = self._get_json(f"/order/{order_id}/payment")
            except Exception as exc:
                logger.warning(
                    "CRM GET /order/%s/payment (попытка %s): %s",
                    order_id,
                    attempt,
                    exc,
                )
                continue
            payload, qr_image = _extract_qr_fields(pay_data)
            if payload or qr_image:
                logger.info(
                    "CRM: QR для заказа %s получен через GET /payment (попытка %s)",
                    order_id,
                    attempt,
                )
                return payload, qr_image
        return _extract_qr_fields(create_data)

    def get_order_status(self, order_id: int) -> OrderStatusResult:
        if not self._katusha:
            return super().get_order_status(order_id)

        data = self._get_json(f"/order/{order_id}/status")
        return OrderStatusResult(
            order_id=int(data.get("order_id") or order_id),
            status=str(data.get("status") or ""),
            payment_status=str(data.get("payment_status") or ""),
            paid=bool(data.get("paid")),
            cancelled=bool(data.get("cancelled")),
            total_amount=float(data.get("total_amount") or 0),
        )

    def get_order_receipt(self, order_id: int) -> OrderReceiptResult:
        if not self._katusha:
            return super().get_order_receipt(order_id)

        data = self._get_json(f"/order/{order_id}/receipt")
        return OrderReceiptResult(
            order_id=int(data.get("order_id") or order_id),
            receipt_text=str(data.get("receipt_text") or ""),
            total_amount=float(data.get("total_amount") or 0),
            station_name=str(data.get("station_name") or ""),
            paid_at=str(data.get("paid_at") or ""),
        )

    def _get_json(self, path: str) -> dict[str, Any]:
        url = self._url(path)
        try:
            resp = self._session.get(
                url,
                params=self._params(),
                timeout=self._config.timeout_sec,
            )
            resp.raise_for_status()
        except requests.HTTPError as exc:
            logger.error("CRM запрос неуспешен: %s", _http_error_detail(exc))
            raise
        except requests.RequestException as exc:
            logger.error("CRM сеть/таймаут %s: %s", url, exc)
            raise

        try:
            data = resp.json()
        except ValueError as exc:
            logger.error("CRM невалидный JSON %s: %s", url, exc)
            raise

        if not isinstance(data, dict):
            raise ValueError(f"Ожидался JSON object, получено: {type(data)}")
        return data

    def is_online(self) -> bool:
        try:
            data = self._get_json("/health")
            if self._katusha:
                ok = bool(data.get("ok"))
                session = data.get("session_active")
                logger.debug(
                    "CRM /health ok=%s session_active=%s kiosk=%s",
                    ok,
                    session,
                    data.get("kiosk_name"),
                )
                if session is False:
                    logger.warning("CRM: смена не активна (session_active=false)")
                return ok
            return True
        except requests.RequestException:
            logger.warning("CRM /health недоступен")
            return False

    def _load_katusha_catalog(self) -> tuple[list[Category], list[Product]]:
        if self._catalog_cache is not None:
            return self._catalog_cache

        data = self._get_json("/catalog")
        self._write_raw_catalog_log(data, source="GET /catalog")
        rows = data.get("products") or []
        if not isinstance(rows, list):
            logger.error("CRM /catalog: поле products не массив")
            rows = []

        products: list[Product] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            p = _parse_katusha_product(row)
            if p:
                products.append(p)

        categories = _katusha_categories_from_rows(
            [r for r in rows if isinstance(r, dict)]
        )
        in_stock = sum(1 for p in products if p.in_stock)

        logger.info(
            "CRM /catalog: total=%s session_active=%s → %d категорий, %d товаров (%d с остатком)",
            data.get("total", len(rows)),
            data.get("session_active"),
            len(categories),
            len(products),
            in_stock,
        )
        if products and in_stock == 0:
            logger.warning(
                "CRM: все товары с нулевым available_quantity — проверьте остатки на точке"
            )

        self._catalog_cache = (categories, products)
        return self._catalog_cache

    def _write_raw_catalog_log(self, payload: dict[str, Any], *, source: str) -> None:
        """Сырой JSON каталога: последний снимок + история в catalog_api.log."""
        stamp = datetime.now().isoformat(timespec="seconds")
        out = ROOT / "logs" / "catalog_api_raw.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        envelope = {
            "timestamp": stamp,
            "source": source,
            "base_url": self._config.base_url,
            "payload": payload,
        }
        out.write_text(
            json.dumps(envelope, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        hist = ROOT / "logs" / "catalog_api.log"
        block = (
            f"\n{'=' * 80}\n"
            f"{stamp} {source} {self._config.base_url}\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
        )
        with open(hist, "a", encoding="utf-8") as fh:
            fh.write(block)
        logger.info("CRM: каталог API записан в %s и %s", out, hist)

    def fetch_categories(self) -> list[Category]:
        if self._katusha:
            return self._load_katusha_catalog()[0]

        if self._config.catalog_mode == "combined":
            data = self._get_json("/kiosk/catalog")
            rows = data.get("categories") or []
        else:
            try:
                data = self._get_json("/categories")
                source = "GET /categories"
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    data = self._get_json("/kiosk/catalog")
                    source = "GET /kiosk/catalog"
                    rows = data.get("categories") or []
                else:
                    raise
            else:
                rows = data.get("categories") or []
            self._write_raw_catalog_log(data, source=source)

        cats = [_parse_category(r) for r in rows if isinstance(r, dict)]
        return [c for c in cats if c]

    def fetch_products(self) -> list[Product]:
        if self._katusha:
            return self._load_katusha_catalog()[1]

        if self._config.catalog_mode == "combined":
            data = self._get_json("/kiosk/catalog")
            source = "GET /kiosk/catalog"
        else:
            try:
                data = self._get_json("/products")
                source = "GET /products"
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    data = self._get_json("/kiosk/catalog")
                    source = "GET /kiosk/catalog"
                else:
                    raise

        self._write_raw_catalog_log(data, source=source)
        rows = data.get("products") or []
        prods = [_parse_product(r) for r in rows if isinstance(r, dict)]
        return [p for p in prods if p]


def create_crm_client(settings: Settings) -> CRMClient:
    if settings.crm.use_mock:
        kolomna = settings.app.ui_theme == "kolomna"
        logger.info("CRM: режим mock-каталога (демо%s)", ", Kolomna" if kolomna else "")
        return MockCRMClient(kolomna=kolomna)
    if not settings.crm.api_key:
        logger.error(
            "CRM: use_mock=false, но KIOSK_API_KEY пуст — задайте ключ в .env или CRM_USE_MOCK=true"
        )
    logger.info("CRM: HTTP %s", settings.crm.base_url)
    client = HttpCRMClient(settings.crm, payment=settings.payment)
    if settings.payment.qr_api_trace_enabled:
        logger.info(
            "СБП QR API trace: %s",
            ROOT / settings.payment.qr_api_trace_file,
        )
    return client
