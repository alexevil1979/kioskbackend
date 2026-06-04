#!/usr/bin/env python3
"""Вырезка прокручиваемой зоны категорий (под шапкой + запас прокрутки)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
OUT = ROOT / "assets" / "reference" / "categories_scroll.png"
Y0, Y1 = 182, 834
VIEWPORT_H = 534


def main() -> None:
    from PIL import Image

    im = Image.open(REF).convert("RGB")
    main_strip = im.crop((0, Y0, im.width, Y1))
    slack = im.crop((0, Y0 + VIEWPORT_H, im.width, Y1))
    w, h1 = main_strip.size
    h2 = slack.size[1]
    out = Image.new("RGB", (w, h1 + h2))
    out.paste(main_strip, (0, 0))
    out.paste(slack, (0, h1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT)
    print(f"saved {OUT} size={out.size} main={h1} slack={h2}")


if __name__ == "__main__":
    main()
