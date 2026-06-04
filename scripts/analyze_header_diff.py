#!/usr/bin/env python3
"""Где максимальное расхождение шапки."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
CUR = ROOT / "logs" / "verify_categories.png"
Y_END = 210


def main() -> None:
    from PIL import Image, ImageChops

    ref = Image.open(REF).convert("RGB").crop((0, 0, 499, Y_END))
    cur = Image.open(CUR).convert("RGB").crop((0, 0, 499, Y_END))
    diff = ImageChops.difference(ref, cur)
    px = diff.load()
    w, h = diff.size
    bands = [(0, 55), (55, 90), (90, 145), (145, 210)]
    for y0, y1 in bands:
        total = 0
        n = 0
        for y in range(y0, min(y1, h)):
            for x in range(w):
                r, g, b = px[x, y]
                total += (r + g + b) / 3.0
                n += 1
        print(f"y={y0}-{y1} mean_diff={total/n/255*100:.2f}%")

    hot = []
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            m = (r + g + b) / 3.0
            if m > 40:
                hot.append((m, x, y, ref.getpixel((x, y)), cur.getpixel((x, y))))
    hot.sort(reverse=True)
    for item in hot[:15]:
        print(item)


if __name__ == "__main__":
    main()
