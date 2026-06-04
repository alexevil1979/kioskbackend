#!/usr/bin/env python3
"""Вырезка блока категорий (hero + сетка) из screen_katusha.png."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
OUT = ROOT / "assets" / "reference" / "hub_block.png"
# верх hero ~200, низ сетки с тенями до nav y=834
Y0, Y1 = 200, 834


def main() -> None:
    from PIL import Image

    im = Image.open(REF).convert("RGB")
    block = im.crop((0, Y0, im.width, Y1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    block.save(OUT)
    print(f"saved {OUT} size={block.size}")


if __name__ == "__main__":
    main()
