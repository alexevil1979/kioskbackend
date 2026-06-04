#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUR = ROOT / "logs" / "verify_categories.png"
REF = ROOT / "assets" / "reference" / "screen_katusha.png"


def find_title(im, name: str) -> None:
    for y in range(145, 200):
        for x in range(10, 120):
            r, g, b = im.getpixel((x, y))
            if r < 30 and g < 35 and b < 50:
                print(f"{name} title y={y} x={x}")
                return


def main() -> None:
    from PIL import Image

    ref = Image.open(REF).convert("RGB")
    cur = Image.open(CUR).convert("RGB")
    find_title(ref, "REF")
    find_title(cur, "CUR")


if __name__ == "__main__":
    main()
