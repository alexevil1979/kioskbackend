#!/usr/bin/env python3
"""Фото хаба: приоритет — вырезка из reference/categories_699.png."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "reference" / "categories_699.png"
EXTRACT = ROOT / "scripts" / "extract_hub_from_reference.py"


def main() -> None:
    if REF.is_file() and EXTRACT.is_file():
        subprocess.check_call([sys.executable, str(EXTRACT)])
        return
    # fallback: цветные плейсхолдеры без тёмной полосы
    from PIL import Image, ImageDraw

    OUT = ROOT / "assets" / "hub"
    OUT.mkdir(parents=True, exist_ok=True)
    specs = [
        ("berry", "#E53935", "#FFCDD2"),
        ("honey", "#F9A825", "#FFF9C4"),
        ("cheese", "#FBC02D", "#FFF9C4"),
        ("dairy", "#FF8F00", "#FFE0B2"),
        ("plants", "#43A047", "#C8E6C9"),
    ]
    for name, c1, c2 in specs:
        img = Image.new("RGB", (640, 480), c2)
        d = ImageDraw.Draw(img)
        d.ellipse((180, 80, 460, 360), fill=c1)
        (OUT / f"{name}.jpg").parent.mkdir(parents=True, exist_ok=True)
        img.save(OUT / f"{name}.jpg", quality=90)
        print("OK", OUT / f"{name}.jpg")


if __name__ == "__main__":
    main()
