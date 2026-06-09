"""Цвет primary-кнопок (ctaColor в референсе / админ-панели)."""
from __future__ import annotations

from dataclasses import dataclass

from src.ui.kolomna_prefs import load_kolomna_prefs
from src.ui.kolomna_tokens import CREAM, GREEN, GREEN_DEEP, STRAWBERRY, YELLOW

CTA_GREEN = "#1F4D2A"
CTA_STRAWBERRY = "#D9143A"
CTA_YELLOW = "#F4C90A"


@dataclass(frozen=True)
class CtaPalette:
    bg: str
    bg_active: str
    fg: str


_CTA: dict[str, CtaPalette] = {
    CTA_GREEN: CtaPalette(GREEN, GREEN_DEEP, CREAM),
    CTA_STRAWBERRY: CtaPalette(STRAWBERRY, "#B5102F", "#FFFFFF"),
    CTA_YELLOW: CtaPalette(YELLOW, "#E0B800", GREEN),
}


def normalize_cta_color(code: str) -> str:
    key = str(code or CTA_GREEN).strip().upper()
    for k in _CTA:
        if k.upper() == key:
            return k
    return CTA_GREEN


def cta_palette(code: str | None = None) -> CtaPalette:
    if code is None:
        code = load_kolomna_prefs().cta_color
    return _CTA[normalize_cta_color(code)]


def cta_swatch_check_color(swatch_code: str) -> str:
    return GREEN if normalize_cta_color(swatch_code) == CTA_YELLOW else "#FFFFFF"
