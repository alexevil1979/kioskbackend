from __future__ import annotations

import logging

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from src.core.config import ROOT

logger = logging.getLogger(__name__)

FONTS_DIR = ROOT / "assets" / "kolomna" / "fonts"
_FAMILY: str | None = None


def _pick_family() -> str:
    global _FAMILY
    if _FAMILY:
        return _FAMILY
    for name in ("Montserrat", "Montserrat Medium"):
        if name in QFontDatabase.families():
            _FAMILY = name
            return name
    for fam in QFontDatabase.families():
        if "Montserrat" in fam and "Thin" not in fam:
            _FAMILY = fam
            return fam
    _FAMILY = "Montserrat"
    return _FAMILY


def setup_kolomna_fonts(app: QApplication) -> None:
    """Montserrat из assets/kolomna/fonts/."""
    loaded: list[str] = []
    for path in sorted(FONTS_DIR.glob("Montserrat-*.ttf")):
        fid = QFontDatabase.addApplicationFont(str(path))
        if fid >= 0:
            loaded.extend(QFontDatabase.applicationFontFamilies(fid))

    if loaded:
        logger.info("Шрифты Kolomna: %s → family %s", ", ".join(sorted(set(loaded))), _pick_family())
    else:
        logger.warning("Montserrat не найден в %s", FONTS_DIR)

    body = kolomna_font(15, QFont.Weight.Medium)
    app.setFont(body)


def kolomna_font(px: int, weight: QFont.Weight = QFont.Weight.Medium) -> QFont:
    """px — как font-size в CSS (pixel size, не point)."""
    font = QFont(_pick_family())
    font.setPixelSize(px)
    font.setWeight(weight)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    return font
