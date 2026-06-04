#!/usr/bin/env python3
"""Сравнение скрина киоска с левой половиной референса 699.ru."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
CUR = ROOT / "logs" / "verify_categories.png"
THRESHOLD = 14.0  # % mean diff vs assets/reference/screen_katusha.png


def main() -> int:
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        print("pip install Pillow")
        return 1

    if not REF.is_file():
        print(f"reference missing: {REF}")
        return 1
    if not CUR.is_file():
        print(f"current missing: {CUR} — run verify_categories_ui.py")
        return 1

    ref = Image.open(REF).convert("RGB")
    cur = Image.open(CUR).convert("RGB")
    w, h = cur.width, cur.height
    if ref.size != (w, h):
        ref = ref.resize((w, h), Image.Resampling.LANCZOS)
    cur = cur.resize((w, h), Image.Resampling.LANCZOS)
    diff = ImageChops.difference(ref, cur)
    stat = ImageStat.Stat(diff)
    mean = sum(stat.mean) / 3.0
    pct = mean / 255.0 * 100.0
    out = ROOT / "logs" / "hub_diff.png"
    diff.save(out)
    print(f"size={w}x{h} mean_diff={pct:.2f}% threshold={THRESHOLD}%")
    print(f"diff_image={out}")
    return 0 if pct < THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())
