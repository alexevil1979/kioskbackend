from __future__ import annotations

from src.core.config import KioskConfig

CONTACT_LINE = "Свяжитесь, пожалуйста, с нами и сообщите об ошибке."


def build_payment_error_message(detail: str | None, kiosk: KioskConfig) -> str:
    """Текст ошибки оплаты: описание + обращение в поддержку (+ телефон по настройке)."""
    lines: list[str] = []
    if detail and detail.strip():
        lines.append(detail.strip())
    lines.append(CONTACT_LINE)
    if kiosk.show_support_phone_on_payment_error:
        phone = kiosk.support_phone.strip()
        if phone:
            lines.append(phone)
    return "\n\n".join(lines)
