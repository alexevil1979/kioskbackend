"""Иконки нижнего меню — PNG из референса 699.ru (assets/nav/)."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from src.core.config import ROOT
from src.ui.image_utils import load_pixmap, scale_pixmap

_NAV = ROOT / "assets" / "nav"


def nav_icon_pixmap(
    kind: str,
    *,
    color=None,  # noqa: ARG001 — цвет зашит в PNG референса
    size: int = 22,
    active: bool = False,
) -> QPixmap:
    if active and kind == "catalog":
        path = _NAV / "catalog_active.png"
        pix = load_pixmap(path)
        if pix.isNull():
            return QPixmap()
        h = 36
        w = max(1, int(pix.width() * h / max(1, pix.height())))
        return scale_pixmap(pix, w, h)

    name = "catalog" if kind == "catalog" else kind
    path = _NAV / f"{name}.png"
    pix = load_pixmap(path)
    if pix.isNull():
        return QPixmap()
    h = size
    w = max(1, int(pix.width() * h / max(1, pix.height())))
    return scale_pixmap(pix, w, h)
