#!/usr/bin/env python3
"""Вырезка нижнего меню из screen_katusha.png."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
OUT = ROOT / "assets" / "reference" / "nav_strip.png"
Y0 = 913 - 79


def main() -> None:
    from PIL import Image

    im = Image.open(REF).convert("RGB")
    strip = im.crop((0, Y0, im.width, im.height))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    strip.save(OUT)
    print(f"saved {OUT} size={strip.size}")


if __name__ == "__main__":
    main()
