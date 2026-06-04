#!/usr/bin/env python3
"""Вырезка шапки из screen_katusha.png → assets/reference/header_strip.png."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
OUT = ROOT / "assets" / "reference" / "header_strip.png"
H = 182


def main() -> None:
    from PIL import Image

    im = Image.open(REF).convert("RGB")
    strip = im.crop((0, 0, im.width, H))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    strip.save(OUT)
    print(f"saved {OUT} {strip.size}")


if __name__ == "__main__":
    main()
