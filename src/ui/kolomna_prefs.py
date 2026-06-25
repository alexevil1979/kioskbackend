"""Локальные настройки киоска Kolomna (аналог localStorage в референсе)."""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from src.core.config import ROOT, Settings

logger = logging.getLogger(__name__)

PREFS_PATH = ROOT / "config" / "kolomna_local.json"


@dataclass
class KolomnaPrefs:
    show_attract: bool = True
    menu_layout: str = "list"
    cta_color: str = "#1F4D2A"
    skip_product: bool = False
    load_api_images: bool = True
    breathe_button_text: bool = True
    payment_sbp_enabled: bool = True
    payment_card_enabled: bool = True
    hours: str = "Ежедневно 10:00–19:00"
    lang: str = "ru"
    # False — тестовый каталог/оплата; True — API Катюша (переключается в настройках).
    api_mode: bool = False
    show_product_description: bool = True


def normalize_payment_methods(prefs: KolomnaPrefs) -> None:
    """Хотя бы один способ оплаты должен быть включён."""
    if not prefs.payment_sbp_enabled and not prefs.payment_card_enabled:
        prefs.payment_sbp_enabled = True


def enabled_payment_methods(prefs: KolomnaPrefs) -> list[str]:
    normalize_payment_methods(prefs)
    out: list[str] = []
    if prefs.payment_sbp_enabled:
        out.append("sbp")
    if prefs.payment_card_enabled:
        out.append("card")
    return out


def load_kolomna_prefs(settings: Settings | None = None) -> KolomnaPrefs:
    from src.ui.kolomna_cta import normalize_cta_color

    if not PREFS_PATH.is_file():
        return KolomnaPrefs()
    try:
        raw = json.loads(PREFS_PATH.read_text(encoding="utf-8"))
        lang = str(raw.get("lang", "ru"))
        if lang not in ("ru", "en"):
            lang = "ru"
        layout = str(raw.get("menu_layout", "list"))
        if layout not in ("list", "grid"):
            layout = "list"
        if "api_mode" in raw:
            api_mode = bool(raw["api_mode"])
        elif settings is not None:
            api_mode = not settings.crm.use_mock
        else:
            api_mode = False
        prefs = KolomnaPrefs(
            show_attract=bool(raw.get("show_attract", True)),
            menu_layout=layout,
            cta_color=normalize_cta_color(str(raw.get("cta_color", "#1F4D2A"))),
            skip_product=bool(raw.get("skip_product", False)),
            load_api_images=bool(raw.get("load_api_images", True)),
            breathe_button_text=bool(raw.get("breathe_button_text", True)),
            payment_sbp_enabled=bool(raw.get("payment_sbp_enabled", True)),
            payment_card_enabled=bool(raw.get("payment_card_enabled", True)),
            hours=str(raw.get("hours", "Ежедневно 10:00–19:00")),
            lang=lang,
            api_mode=api_mode,
            show_product_description=bool(raw.get("show_product_description", True)),
        )
        normalize_payment_methods(prefs)
        return prefs
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        logger.warning("kolomna_local.json: %s", exc)
        return KolomnaPrefs()


def save_kolomna_prefs(prefs: KolomnaPrefs) -> None:
    from src.ui.kolomna_cta import normalize_cta_color

    prefs.cta_color = normalize_cta_color(prefs.cta_color)
    if prefs.menu_layout not in ("list", "grid"):
        prefs.menu_layout = "list"
    normalize_payment_methods(prefs)
    PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREFS_PATH.write_text(
        json.dumps(asdict(prefs), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
