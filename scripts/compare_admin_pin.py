#!/usr/bin/env python3
"""Сравнение admin PIN modal: ref vs app."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "logs" / "admin_pin_ref.png"
APP = ROOT / "logs" / "admin_pin_app.png"
OUT = ROOT / "logs"


def _modal_crop(im: Image.Image) -> Image.Image:
    px = im.convert("RGB").load()
    w, h = im.size
    cream = (246, 239, 216)
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - cream[0]) < 6 and abs(g - cream[1]) < 6 and abs(b - cream[2]) < 6:
                xs.append(x)
                ys.append(y)
    return im.crop((min(xs), min(ys), max(xs), max(ys)))


def main() -> None:
    ref = _modal_crop(Image.open(REF))
    app = _modal_crop(Image.open(APP))
    ref.save(OUT / "modal_only_ref.png")
    app.save(OUT / "modal_only_app.png")
    h = min(ref.height, app.height)
    w = min(ref.width, app.width)
    rh = ref.crop((0, 0, w, h)).convert("RGB")
    ah = app.crop((0, 0, w, h)).convert("RGB")
    diff = ImageChops.difference(rh, ah)
    data = list(diff.getdata())
    changed = sum(1 for p in data if max(p) > 25)
    pct = 100 * changed / len(data)
    combo = Image.new("RGB", (rh.width * 2 + 4, h))
    combo.paste(rh, (0, 0))
    combo.paste(ah, (rh.width + 4, 0))
    combo.save(OUT / "modal_only_side.png")
    print(f"ref {ref.size} app {app.size} modal diff {pct:.2f}%")


if __name__ == "__main__":
    main()
