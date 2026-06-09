from __future__ import annotations

import logging
import os
from pathlib import Path

from src.core.config import Settings
from src.services.crm_client import _is_katusha_kiosk_api

logger = logging.getLogger(__name__)


def _truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


def load_dotenv_file(root: Path) -> None:
    """Загружает `.env` из корня проекта (если установлен python-dotenv)."""
    env_path = root / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=True)
        logger.debug("Загружен .env: %s", env_path)
    except ImportError:
        logger.warning(
            "Файл .env найден, но python-dotenv не установлен — pip install python-dotenv"
        )


def apply_env_overrides(settings: Settings) -> None:
    app = settings.app
    title = os.getenv("APP_TITLE")
    if title:
        app.title = title.strip()

    dev_env = os.getenv("DEV_MODE")
    if dev_env is not None:
        app.dev_mode = _truthy(dev_env)
        if app.dev_mode:
            app.fullscreen = False

    kiosk = settings.kiosk
    if app.dev_mode:
        kiosk.block_keys = False
    """
    Переменные окружения перекрывают config/settings.yaml.
    Секреты задавайте в .env (файл в git не попадает).
    """
    crm = settings.crm

    base_url = (
        os.getenv("KIOSK_API_BASE_URL")
        or os.getenv("CRM_API_BASE_URL")
        or os.getenv("CRM_BASE_URL")
    )
    if base_url:
        crm.base_url = base_url.rstrip("/")

    api_key = os.getenv("KIOSK_API_KEY") or os.getenv("CRM_API_KEY")
    if api_key:
        crm.api_key = api_key

    kiosk_id = os.getenv("CRM_KIOSK_ID")
    if kiosk_id:
        crm.kiosk_id = kiosk_id

    mock_env = os.getenv("CRM_USE_MOCK")
    if mock_env is not None:
        crm.use_mock = _truthy(mock_env)
    elif api_key and crm.base_url:
        # Ключ и URL заданы — по умолчанию боевой API, не mock
        crm.use_mock = False
    if (
        settings.app.dev_mode
        and settings.app.ui_theme == "kolomna"
        and os.getenv("CRM_USE_LIVE") is None
        and mock_env is None
    ):
        # DEV_MODE + Kolomna: каталог как в offline-референсе (window.KIOSK)
        crm.use_mock = True

    catalog_mode = os.getenv("CRM_CATALOG_MODE")
    if catalog_mode:
        crm.catalog_mode = catalog_mode.strip().lower()

    purchase_test_mode = os.getenv("PURCHASE_TEST_MODE")
    if purchase_test_mode is not None:
        settings.catalog.purchase_test_mode = _truthy(purchase_test_mode)

    purchase_test_qty = os.getenv("PURCHASE_TEST_QTY")
    if purchase_test_qty:
        try:
            settings.catalog.test_stock_qty = max(1, int(purchase_test_qty))
        except ValueError:
            logger.warning("PURCHASE_TEST_QTY не число: %s", purchase_test_qty)

    kiosk_cfg = settings.kiosk
    support_phone = os.getenv("KIOSK_SUPPORT_PHONE")
    if support_phone is not None:
        kiosk_cfg.support_phone = support_phone.strip()
    show_phone = os.getenv("KIOSK_SHOW_SUPPORT_PHONE_ON_PAYMENT_ERROR")
    if show_phone is not None:
        kiosk_cfg.show_support_phone_on_payment_error = _truthy(show_phone)

    integration_mode = os.getenv("INTEGRATION_MODE") or os.getenv("HARDWARE_INTEGRATION_MODE")
    if integration_mode:
        settings.hardware.integration_mode = integration_mode.strip()
    elif (
        not settings.crm.use_mock
        and _is_katusha_kiosk_api(settings.crm.base_url)
        and settings.crm.api_key
        and settings.hardware.integration_mode == "tbank_aqsi"
    ):
        settings.hardware.integration_mode = "tbank_pos_sbp"
        logger.info(
            "Katusha API: integration_mode tbank_aqsi → tbank_pos_sbp (СБП QR на экране киоска)"
        )

    # aQsi
    aqsi_key = os.getenv("AQSI_API_KEY")
    if aqsi_key:
        settings.hardware.aqsi.api_key = aqsi_key
    aqsi_base = os.getenv("AQSI_API_BASE")
    if aqsi_base:
        settings.hardware.aqsi.api_base = aqsi_base.rstrip("/")

    pay = settings.payment
    qr_trace = os.getenv("PAYMENT_QR_API_TRACE_ENABLED")
    if qr_trace is not None:
        pay.qr_api_trace_enabled = _truthy(qr_trace)
    qr_trace_file = os.getenv("PAYMENT_QR_API_TRACE_FILE")
    if qr_trace_file:
        pay.qr_api_trace_file = qr_trace_file.strip()

    # Т-Банк СБП
    sbp_mock = os.getenv("PAYMENT_SBP_USE_MOCK")
    if sbp_mock is not None:
        settings.payment.sbp.use_mock = _truthy(sbp_mock)
    if tk := os.getenv("TBANK_TERMINAL_KEY"):
        settings.payment.sbp.terminal_key = tk
    if tp := os.getenv("TBANK_TERMINAL_PASSWORD"):
        settings.payment.sbp.password = tp

    # Облачная касса
    if cp := os.getenv("FISCAL_CLOUD_PUBLIC_ID"):
        settings.fiscal.cloud_public_id = cp
    if cs := os.getenv("FISCAL_CLOUD_API_SECRET"):
        settings.fiscal.cloud_api_secret = cs
