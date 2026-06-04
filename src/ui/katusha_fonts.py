from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from src.core.config import ROOT

logger = logging.getLogger(__name__)

FONTS_DIR = ROOT / "assets" / "fonts"


def setup_katusha_fonts(app: QApplication) -> None:
    """Inter (body) + Unbounded (заголовки, CTA) — как в reference/katusha-miniapp."""
    families: list[str] = []
    for path in (
        FONTS_DIR / "Inter-Regular.ttf",
        FONTS_DIR / "Inter-SemiBold.ttf",
        FONTS_DIR / "Unbounded-Bold.ttf",
    ):
        if path.is_file():
            fid = QFontDatabase.addApplicationFont(str(path))
            if fid >= 0:
                families.extend(QFontDatabase.applicationFontFamilies(fid))

    if families:
        logger.info("Шрифты Катюша: %s", ", ".join(sorted(set(families))))
    else:
        logger.warning("Шрифты не найдены в %s — используем системные", FONTS_DIR)

    body = QFont("Inter", 15)
    body.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(body)
