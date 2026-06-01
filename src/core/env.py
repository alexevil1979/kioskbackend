from __future__ import annotations

import logging
import os
from pathlib import Path

from src.core.config import Settings

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
    """
    Переменные окружения перекрывают config/settings.yaml.
    Секреты задавайте в .env (файл в git не попадает).
    """
    crm = settings.crm

    base_url = os.getenv("CRM_API_BASE_URL") or os.getenv("CRM_BASE_URL")
    if base_url:
        crm.base_url = base_url.rstrip("/")

    api_key = os.getenv("CRM_API_KEY")
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

    catalog_mode = os.getenv("CRM_CATALOG_MODE")
    if catalog_mode:
        crm.catalog_mode = catalog_mode.strip().lower()

    # aQsi
    aqsi_key = os.getenv("AQSI_API_KEY")
    if aqsi_key:
        settings.hardware.aqsi.api_key = aqsi_key
    aqsi_base = os.getenv("AQSI_API_BASE")
    if aqsi_base:
        settings.hardware.aqsi.api_base = aqsi_base.rstrip("/")

    # Т-Банк СБП
    if tk := os.getenv("TBANK_TERMINAL_KEY"):
        settings.payment.sbp.terminal_key = tk
    if tp := os.getenv("TBANK_TERMINAL_PASSWORD"):
        settings.payment.sbp.password = tp

    # Облачная касса
    if cp := os.getenv("FISCAL_CLOUD_PUBLIC_ID"):
        settings.fiscal.cloud_public_id = cp
    if cs := os.getenv("FISCAL_CLOUD_API_SECRET"):
        settings.fiscal.cloud_api_secret = cs
