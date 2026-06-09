#!/usr/bin/env python3
"""Копирует ассеты pic/ → design-core/assets/img/ для offline HTML-референса."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "pic"
DST = ROOT / "design-core" / "assets" / "img"
REF_CATEGORIES = ROOT / "logs" / "kolomna_ref" / "02_categories.png"
LOGO_DROP_OUT = ROOT / "assets" / "kolomna" / "logo_drop_catalog.png"
KIOSK_W = 1080


MASK_OUT = ROOT / "assets" / "kolomna" / "logo_drop_mask.png"
COMPOSITE_OUT = ROOT / "assets" / "kolomna" / "logo_drop_composite.png"


def _extract_logo_drop_from_ref() -> None:
    """Маска капли catalog__bar из скриншота референса."""
    if not REF_CATEGORIES.is_file():
        return
    try:
        from PIL import Image
    except ImportError:
        return
    img = Image.open(REF_CATEGORIES).convert("RGBA")
    w = img.width
    logo_w = round(340 * w / KIOSK_W)
    logo_h = round(158 * w / KIOSK_W)
    pad_top = round(36 * w / KIOSK_W)
    x0 = max(0, (w - logo_w) // 2)
    y0 = pad_top
    crop = img.crop((x0, y0, x0 + logo_w, y0 + logo_h))
    MASK_OUT.parent.mkdir(parents=True, exist_ok=True)
    mask = Image.new("L", crop.size, 0)
    px, mp = crop.load(), mask.load()
    for yy in range(crop.height):
        for xx in range(crop.width):
            r, g, b, _a = px[xx, yy]
            if r > 150 and g < 80 and b < 80:
                mp[xx, yy] = 255
    mask.save(MASK_OUT)
    crop.save(COMPOSITE_OUT)
    print(f"extracted logo drop mask -> {MASK_OUT.name}")
    print(f"extracted logo drop composite -> {COMPOSITE_OUT.name}")


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for pattern in ("berry-*.webp", "logo.webp"):
        for src in SRC.glob(pattern):
            shutil.copy2(src, DST / src.name)
            print(f"copied {src.name}")
    logo = ROOT / "assets" / "kolomna" / "logo.webp"
    if logo.is_file():
        shutil.copy2(logo, DST / "logo.webp")
        print("copied logo.webp from assets/kolomna")
    _extract_logo_drop_from_ref()


if __name__ == "__main__":
    main()
