#!/usr/bin/env python3
"""Поэлементное сравнение экрана категорий: ref vs app по зонам."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.kolomna_compare_common import crop_kiosk_content, mean_diff_pct

REF = ROOT / "logs" / "kolomna_ref" / "02_categories.png"
APP = ROOT / "logs" / "kolomna_app" / "02_categories.png"
OUT = ROOT / "logs" / "kolomna_diff" / "categories_zones"
THRESHOLD = 3.0


def _pct(a: Image.Image, b: Image.Image) -> float:
    return mean_diff_pct(a, b)


def _crop(img: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    return img.crop(box)


def main() -> None:
    if not REF.is_file() or not APP.is_file():
        print("Run render_kolomna_reference.py and grab_all_kolomna_screens.py first")
        return 1
    ref = crop_kiosk_content(Image.open(REF).convert("RGB"))
    app = crop_kiosk_content(Image.open(APP).convert("RGB"))
    w, h = ref.size
    if app.size != ref.size:
        app = app.resize(ref.size, Image.Resampling.LANCZOS)
    # Зоны @ 499×913 (letterbox); bar ~22% высоты контента
    bar_h = int(h * 0.125)
    mid_y = bar_h + (h - bar_h) // 2
    zones = {
        "01_bar": (0, 0, w, bar_h),
        "02_logo": (int(w * 0.28), 0, int(w * 0.72), bar_h),
        "03_info": (0, int(bar_h * 0.1), int(w * 0.32), bar_h),
        "04_lang": (int(w * 0.68), int(bar_h * 0.1), w, bar_h),
        "05_tile_tl": (0, bar_h, w // 2, mid_y),
        "06_tile_tr": (w // 2, bar_h, w, mid_y),
        "07_tile_bl": (0, mid_y, w // 2, h),
        "08_tile_br": (w // 2, mid_y, w, h),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    failed: list[str] = []
    perfect: list[str] = []
    print(f"compare {w}x{h}")
    for name, box in zones.items():
        r = _crop(ref, box)
        a = _crop(app, box)
        pct = _pct(r, a)
        diff = ImageChops.difference(r, a.resize(r.size, Image.Resampling.LANCZOS))
        diff.save(OUT / f"{name}.png")
        mark = "OK" if pct <= THRESHOLD else "FAIL"
        if pct <= THRESHOLD and pct == 0.0:
            perfect.append(name)
        elif pct > THRESHOLD:
            failed.append(name)
        print(f"  {mark} {name}: {pct:.2f}%")
    total = len(zones)
    print(f"zones failed: {len(failed)} / {total}")
    print(f"zones perfect (0.0%): {len(perfect)} / {total}")
    print(f"pass rate: {round(100 * (total - len(failed)) / total, 1)}%")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
