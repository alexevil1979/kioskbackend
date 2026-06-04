#!/usr/bin/env python3
"""Сравнение скрина категорий с референсом 699 (по зонам)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
CUR = ROOT / "logs" / "verify_categories.png"
Y0, Y1 = 182, 716

_SLOTS = {
    "header": (0, 0, 499, 182),
    "hero": (16, 211, 482, 399),
    "card1": (16, 528, 243, 652),
    "nav": (0, 834, 499, 913),
}


def _diff_pct(ref, cur, box: tuple[int, int, int, int]) -> float:
    from PIL import Image, ImageChops, ImageStat

    r = ref.crop(box)
    c = cur.crop(box)
    if c.size != r.size:
        c = c.resize(r.size, Image.Resampling.LANCZOS)
    d = ImageChops.difference(r, c)
    return sum(ImageStat.Stat(d).mean) / 3.0 / 255.0 * 100.0


def main() -> int:
    from PIL import Image, ImageChops, ImageStat

    if not CUR.is_file():
        print(f"missing {CUR} — run verify_categories_layout.py")
        return 1
    ref = Image.open(REF).convert("RGB")
    cur = Image.open(CUR).convert("RGB")
    ref_crop = ref.crop((0, Y0, ref.width, Y1))
    if cur.size != ref_crop.size:
        cur = cur.resize(ref_crop.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(ref_crop, cur)
    pct = sum(ImageStat.Stat(diff).mean) / 3.0 / 255.0 * 100.0
    out = ROOT / "logs" / "categories_ref_diff.png"
    diff.save(out)
    print(f"hub_region diff={pct:.1f}% saved {out}")
    for name, box in _SLOTS.items():
        print(f"  {name}: {_diff_pct(ref, cur, box):.1f}%")
    # Шапка/нав 1:1; hero/card1 отличаются текстом и данными API
    ok = _diff_pct(ref, cur, _SLOTS["header"]) < 1.0 and _diff_pct(ref, cur, _SLOTS["nav"]) < 1.0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
