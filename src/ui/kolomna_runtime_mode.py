from __future__ import annotations

from src.core.config import Settings
from src.ui import kolomna_strings as S

_INTEGRATION_KEYS: dict[str, str] = {
    "tbank_aqsi": "ADMIN_INTEGRATION_AQSI",
    "tbank_pos_sbp": "ADMIN_INTEGRATION_POS_SBP",
    "tbank_pos_printer": "ADMIN_INTEGRATION_POS_PRINTER",
    "legacy_umka": "ADMIN_INTEGRATION_LEGACY",
}


def _integration_label(mode: str) -> str:
    key = _INTEGRATION_KEYS.get(mode.strip())
    if key:
        return str(getattr(S, key))
    return mode or "—"


def runtime_mode_rows(settings: Settings) -> list[tuple[str, str]]:
    """Подписи для экрана настроек: (заголовок строки, значение)."""
    catalog = S.ADMIN_MODE_TEST if settings.crm.use_mock else S.ADMIN_MODE_API
    sbp_mock = settings.crm.use_mock or settings.payment.sbp.use_mock
    payment = S.ADMIN_MODE_TEST if sbp_mock else S.ADMIN_MODE_API
    return [
        (S.ADMIN_RUNTIME_CATALOG, catalog),
        (S.ADMIN_RUNTIME_PAYMENT, payment),
        (S.ADMIN_RUNTIME_INTEGRATION, _integration_label(settings.hardware.integration_mode)),
    ]
