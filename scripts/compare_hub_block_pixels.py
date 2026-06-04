#!/usr/bin/env python3
"""Сравнение блока категорий (y=211..797) с референсом."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
CUR = ROOT / "logs" / "verify_categories.png"
Y0, Y1 = 182, 834
THRESHOLD = 1.0


def main() -> int:
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        print("pip install Pillow")
        return 1

    if not REF.is_file() or not CUR.is_file():
        print("missing ref or verify screenshot")
        return 1

    ref = Image.open(REF).convert("RGB").crop((0, Y0, 499, Y1))
    cur = Image.open(CUR).convert("RGB").crop((0, Y0, 499, Y1))
    if ref.size != cur.size:
        cur = cur.resize(ref.size, Image.Resampling.LANCZOS)

    diff = ImageChops.difference(ref, cur)
    pct = sum(ImageStat.Stat(diff).mean) / 3.0 / 255.0 * 100.0
    out = ROOT / "logs" / "hub_block_diff.png"
    diff.save(out)
    side = ROOT / "logs" / "hub_block_side_by_side.png"
    combined = Image.new("RGB", (ref.width * 2, ref.height))
    combined.paste(ref, (0, 0))
    combined.paste(cur, (ref.width, 0))
    combined.save(side)
    print(f"hub_block {ref.size[0]}x{ref.size[1]} mean_diff={pct:.2f}% threshold={THRESHOLD}%")
    print(f"diff={out}")
    print(f"side={side}")
    return 0 if pct < THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())
