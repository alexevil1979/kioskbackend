#!/usr/bin/env python3
"""Вырезать иконки нижнего меню из assets/reference/bottom_nav_ref.png."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "bottom_nav_ref.png"
OUT = ROOT / "assets" / "nav"

NAMES = ("orders", "feed", "catalog", "cart", "profile")
ICON_BOTTOM = 42  # над подписями


def _gray_icon(active: Image.Image) -> Image.Image:
    """Серый контур для неактивного КАТАЛОГ из активной иконки."""
    rgba = active.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)
            if lum > 200:  # фон круга
                px[x, y] = (255, 255, 255, 0)
            else:
                px[x, y] = (194, 199, 207, a)
    return rgba


def main() -> None:
    im = Image.open(REF).convert("RGBA")
    w, h = im.size
    col_w = w // 5
    OUT.mkdir(parents=True, exist_ok=True)

    for i, name in enumerate(NAMES):
        x0 = i * col_w + 8
        x1 = (i + 1) * col_w - 8
        icon = im.crop((x0, 4, x1, ICON_BOTTOM))
        if name == "catalog":
            icon.save(OUT / "catalog_active.png")
            _gray_icon(icon).save(OUT / "catalog.png")
        else:
            icon.save(OUT / f"{name}.png")
        print("OK", OUT / f"{name}.png", icon.size)

    print("OK", OUT / "catalog_active.png")


if __name__ == "__main__":
    main()
