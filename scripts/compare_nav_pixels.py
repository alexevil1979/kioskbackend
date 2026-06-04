#!/usr/bin/env python3
"""Сравнение нижнего меню (y=834..913) с референсом."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
CUR = ROOT / "logs" / "verify_categories.png"
Y0, Y1 = 834, 913
THRESHOLD = 1.0


def main() -> int:
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        return 1

    ref = Image.open(REF).convert("RGB").crop((0, Y0, 499, Y1))
    cur = Image.open(CUR).convert("RGB").crop((0, Y0, 499, Y1))
    diff = ImageChops.difference(ref, cur)
    pct = sum(ImageStat.Stat(diff).mean) / 3.0 / 255.0 * 100.0
    out = ROOT / "logs" / "nav_diff.png"
    diff.save(out)
    side = ROOT / "logs" / "nav_side_by_side.png"
    comb = Image.new("RGB", (ref.width * 2, ref.height))
    comb.paste(ref, (0, 0))
    comb.paste(cur, (ref.width, 0))
    comb.save(side)
    print(f"nav {ref.size} mean_diff={pct:.2f}% threshold={THRESHOLD}%")
    return 0 if pct < THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())
