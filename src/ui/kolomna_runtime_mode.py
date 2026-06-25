from __future__ import annotations

from src.core.config import Settings
from src.ui import kolomna_strings as S

_INTEGRATION_KEYS: dict[str, str] = {
    "tbank_aqsi": "ADMIN_INTEGRATION_AQSI",
    "tbank_pos_sbp": "ADMIN_INTEGRATION_POS_SBP",
    "tbank_pos_printer": "ADMIN_INTEGRATION_POS_PRINTER",
    "legacy_umka": "ADMIN_INTEGRATION_LEGACY",
}


def integration_label(mode: str) -> str:
    key = _INTEGRATION_KEYS.get((mode or "").strip())
    if key:
        return str(getattr(S, key))
    return mode or "—"


def apply_prefs_api_mode(settings: Settings, api_mode: bool) -> bool:
    """Применить режим API/тест к settings. Возвращает True, если что-то изменилось."""
    use_mock = not api_mode
    prev_crm = settings.crm.use_mock
    prev_sbp = settings.payment.sbp.use_mock
    settings.crm.use_mock = use_mock
    settings.payment.sbp.use_mock = use_mock
    if (
        api_mode
        and settings.crm.api_key.strip()
        and _is_katusha_kiosk_api(settings.crm.base_url)
        and settings.hardware.integration_mode == "tbank_aqsi"
    ):
        settings.hardware.integration_mode = "tbank_pos_sbp"
    return prev_crm != use_mock or prev_sbp != use_mock


def _is_katusha_kiosk_api(base_url: str) -> bool:
    u = (base_url or "").lower()
    return "katusha" in u or "/kiosk" in u


def runtime_mode_rows(settings: Settings) -> list[tuple[str, str]]:
    """Подписи для экрана настроек: (заголовок строки, значение)."""
    catalog = S.ADMIN_MODE_TEST if settings.crm.use_mock else S.ADMIN_MODE_API
    sbp_mock = settings.crm.use_mock or settings.payment.sbp.use_mock
    payment = S.ADMIN_MODE_TEST if sbp_mock else S.ADMIN_MODE_API
    return [
        (S.ADMIN_RUNTIME_CATALOG, catalog),
        (S.ADMIN_RUNTIME_PAYMENT, payment),
        (S.ADMIN_RUNTIME_INTEGRATION, integration_label(settings.hardware.integration_mode)),
    ]
