from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from src.core.cart import CartLine
from src.core.config import FiscalConfig, HardwareUmkaConfig, Settings

logger = logging.getLogger(__name__)

# Документация: docs/hardware/03-umka-01-fa.md, UMKA_API_QUICKREF.md


@dataclass
class FiscalResult:
    success: bool
    receipt_number: str = ""
    error: str = ""
    raw: dict[str, Any] | None = None


class FiscalUmkaService:
    """Онлайн-касса УМКА-01-ФА по HTTP API (платформа arMax / УМКА)."""

    def __init__(self, settings: Settings) -> None:
        self._cfg = settings.fiscal
        self._hw = settings.hardware.umka

    def _base_url(self) -> str:
        if self._cfg.use_test_server:
            scheme = "https" if self._cfg.use_https else "http"
            return f"{scheme}://{self._cfg.test_host}:{self._cfg.test_port}/"
        scheme = "https" if self._cfg.use_https else "http"
        host = self._cfg.host or self._hw.host
        port = self._cfg.port or self._hw.port
        return f"{scheme}://{host}:{port}/"

    def _auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self._cfg.cashier_login, self._cfg.cashier_password)

    def check_status(self) -> tuple[bool, str]:
        """GET /cashboxstatus.json — готовность кассы."""
        url = urljoin(self._base_url(), "cashboxstatus.json")
        try:
            r = requests.get(url, auth=self._auth(), timeout=10)
            r.raise_for_status()
            data = r.json()
            status = data.get("cashboxStatus") or data
            result = status.get("result", 0) if isinstance(status, dict) else 0
            if result != 0:
                return False, f"Касса вернула result={result}"
            return True, "OK"
        except requests.RequestException as exc:
            logger.error("УМКА: нет связи %s: %s", url, exc)
            return False, str(exc)

    def print_receipt(
        self,
        lines: list[CartLine],
        total: float,
        payment_type: str,
    ) -> FiscalResult:
        if not self._cfg.enabled:
            logger.info("УМКА: отключена в конфиге (mock OK)")
            return FiscalResult(success=True, receipt_number="MOCK-001")

        ok, msg = self.check_status()
        if not ok:
            return FiscalResult(success=False, error=f"Касса недоступна: {msg}")

        body = self._build_receipt_json(lines, total, payment_type)
        url = urljoin(self._base_url(), "fiscalcheck.json")
        try:
            r = requests.post(url, json=body, auth=self._auth(), timeout=30)
            r.raise_for_status()
            data = r.json()
            doc = data.get("document") or data
            result = doc.get("result", -1) if isinstance(doc, dict) else -1
            if result != 0:
                return FiscalResult(
                    success=False,
                    error=f"fiscalcheck result={result}",
                    raw=data if isinstance(data, dict) else None,
                )
            doc_num = ""
            inner = doc.get("data") if isinstance(doc, dict) else None
            if isinstance(inner, dict):
                doc_num = str(inner.get("docNumber", ""))
            logger.info("УМКА: чек пробит, doc=%s", doc_num)
            return FiscalResult(success=True, receipt_number=doc_num, raw=data if isinstance(data, dict) else None)
        except requests.RequestException as exc:
            logger.exception("УМКА: ошибка fiscalcheck")
            return FiscalResult(success=False, error=str(exc))

    def _build_receipt_json(
        self,
        lines: list[CartLine],
        total: float,
        payment_type: str,
    ) -> dict[str, Any]:
        """
        Упрощённое тело чека. Перед продом — согласовать теги ФФД с бухгалтерией / umki.org.
        Суммы в копейках.
        """
        money_type = 1 if payment_type in ("cash", "наличные") else 2
        items = []
        for line in lines:
            price_kop = int(round(line.product.price_rub * 100))
            qty = line.quantity
            items.append(
                {
                    "tag": 1059,
                    "fiscprops": [
                        {"tag": 1030, "value": line.product.name},
                        {"tag": 1079, "value": str(price_kop)},
                        {"tag": 1023, "value": str(qty)},
                        {"tag": 1043, "value": str(price_kop * qty)},
                        {"tag": 1199, "value": 6},
                    ],
                }
            )
        total_kop = int(round(total * 100))
        return {
            "document": {
                "print": 1,
                "data": {
                    "type": 1,
                    "moneyType": money_type,
                    "sum": total_kop,
                    "fiscprops": items,
                },
            }
        }
