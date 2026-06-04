#!/usr/bin/env python3
"""Вырезать фото категорий из assets/reference/screen_katusha.png (499×913)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
FALLBACK = ROOT / "assets" / "reference" / "categories_699.png"
OUT = ROOT / "assets" / "hub"
TARGET = (499, 913)

# Координаты на viewport 499×913
CROPS: dict[str, tuple[int, int, int, int]] = {
    "berry": (16, 211, 482, 399),
    "honey": (16, 528, 243, 652),
    "cheese": (255, 528, 482, 652),
    "dairy": (16, 673, 243, 797),
    "plants": (255, 673, 482, 797),
}


def main() -> None:
    src = REF if REF.is_file() else FALLBACK
    im = Image.open(src).convert("RGB")
    if src == FALLBACK:
        left = im.crop((0, 0, im.width // 2, im.height))
        left = left.resize(TARGET, Image.Resampling.LANCZOS)
    else:
        left = im.resize(TARGET, Image.Resampling.LANCZOS)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, box in CROPS.items():
        card = left.crop(box)
        card.save(OUT / f"{name}.jpg", "JPEG", quality=92)
        print("OK", OUT / f"{name}.jpg", card.size)


if __name__ == "__main__":
    main()
