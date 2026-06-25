from __future__ import annotations

from src.core.config import KioskConfig

CONTACT_LINE = "Свяжитесь, пожалуйста, с нами и сообщите об ошибке."

_PLACEHOLDER_PHONE = "+7 (900) 000-00-00"


def resolve_support_phone(kiosk: KioskConfig, *, kolomna: bool = False) -> str:
    """Телефон поддержки: из информации (Kolomna) или настроек киоска."""
    if kolomna:
        from src.ui import kolomna_strings as S

        return S.INFO_PHONE.strip()
    phone = kiosk.support_phone.strip()
    if phone and phone != _PLACEHOLDER_PHONE:
        return phone
    return ""


def build_payment_error_message(
    detail: str | None,
    kiosk: KioskConfig,
    *,
    kolomna: bool = False,
) -> str:
    """Текст ошибки оплаты: описание + обращение в поддержку (+ телефон по настройке)."""
    lines: list[str] = []
    if detail and detail.strip():
        lines.append(detail.strip())
    lines.append(CONTACT_LINE)
    if kiosk.show_support_phone_on_payment_error:
        phone = resolve_support_phone(kiosk, kolomna=kolomna)
        if phone:
            lines.append(phone)
    return "\n\n".join(lines)
