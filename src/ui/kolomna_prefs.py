"""Локальные настройки киоска Kolomna (аналог localStorage в референсе)."""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from src.core.config import ROOT

logger = logging.getLogger(__name__)

PREFS_PATH = ROOT / "config" / "kolomna_local.json"


@dataclass
class KolomnaPrefs:
    show_attract: bool = True
    menu_layout: str = "list"
    cta_color: str = "#1F4D2A"
    skip_product: bool = False
    hours: str = "Ежедневно 10:00–19:00"
    lang: str = "ru"


def load_kolomna_prefs() -> KolomnaPrefs:
    if not PREFS_PATH.is_file():
        return KolomnaPrefs()
    try:
        raw = json.loads(PREFS_PATH.read_text(encoding="utf-8"))
        lang = str(raw.get("lang", "ru"))
        if lang not in ("ru", "en"):
            lang = "ru"
        return KolomnaPrefs(
            show_attract=bool(raw.get("show_attract", True)),
            menu_layout=str(raw.get("menu_layout", "list")),
            cta_color=str(raw.get("cta_color", "#1F4D2A")),
            skip_product=bool(raw.get("skip_product", False)),
            hours=str(raw.get("hours", "Ежедневно 10:00–19:00")),
            lang=lang,
        )
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        logger.warning("kolomna_local.json: %s", exc)
        return KolomnaPrefs()


def save_kolomna_prefs(prefs: KolomnaPrefs) -> None:
    PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREFS_PATH.write_text(
        json.dumps(asdict(prefs), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
