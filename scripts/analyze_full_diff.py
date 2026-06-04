#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "screen_katusha.png"
CUR = ROOT / "logs" / "verify_categories.png"


def main() -> None:
    from PIL import Image, ImageChops

    ref = Image.open(REF).convert("RGB")
    cur = Image.open(CUR).convert("RGB")
    diff = ImageChops.difference(ref, cur)
    px = diff.load()
    w, h = diff.size
    bands = [(0, 182), (182, 211), (211, 797), (797, 834), (834, 913)]
    for y0, y1 in bands:
        total = n = 0
        for y in range(y0, min(y1, h)):
            for x in range(w):
                total += sum(px[x, y]) / 3.0
                n += 1
        print(f"y={y0}-{y1} diff={total/n/255*100:.2f}%")


if __name__ == "__main__":
    main()
