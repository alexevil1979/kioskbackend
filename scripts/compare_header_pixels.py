#!/usr/bin/env python3
"""Сравнение шапки (y=0..Y_END) киоска с референсом."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
CUR = ROOT / "logs" / "verify_categories.png"
Y_END = 182
THRESHOLD = 1.0  # % mean diff — цель ~100% совпадение


def main() -> int:
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        print("pip install Pillow")
        return 1

    if not REF.is_file():
        print(f"missing ref: {REF}")
        return 1
    if not CUR.is_file():
        print(f"missing cur: {CUR} — run verify_categories_ui.py")
        return 1

    ref = Image.open(REF).convert("RGB")
    cur = Image.open(CUR).convert("RGB")
    w = min(ref.width, cur.width)
    ref = ref.crop((0, 0, w, min(Y_END, ref.height)))
    cur = cur.crop((0, 0, w, min(Y_END, cur.height)))
    if ref.size != cur.size:
        cur = cur.resize(ref.size, Image.Resampling.LANCZOS)

    diff = ImageChops.difference(ref, cur)
    stat = ImageStat.Stat(diff)
    mean = sum(stat.mean) / 3.0
    pct = mean / 255.0 * 100.0
    out = ROOT / "logs" / "header_diff.png"
    diff.save(out)
    side = ROOT / "logs" / "header_side_by_side.png"
    combined = Image.new("RGB", (w * 2, ref.height))
    combined.paste(ref, (0, 0))
    combined.paste(cur, (w, 0))
    combined.save(side)
    print(f"header {ref.size[0]}x{ref.size[1]} mean_diff={pct:.2f}% threshold={THRESHOLD}%")
    print(f"diff={out}")
    print(f"side_by_side={side}")
    return 0 if pct < THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())
