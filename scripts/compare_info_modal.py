#!/usr/bin/env python3
"""Side-by-side REF vs APP for info modal."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw, ImageFont

REF = ROOT / "logs" / "kolomna_ref" / "10_info_modal.png"
APP = ROOT / "logs" / "kolomna_app" / "10_info_modal.png"
OUT = ROOT / "logs" / "info_modal_compare.png"


def main() -> int:
    ref = Image.open(REF).convert("RGB")
    app = Image.open(APP).convert("RGB")
    if ref.size != app.size:
        app = app.resize(ref.size, Image.Resampling.LANCZOS)
    w, h = ref.size
    out = Image.new("RGB", (w * 2 + 4, h + 40), (32, 32, 32))
    out.paste(ref, (0, 40))
    out.paste(app, (w + 4, 40))
    draw = ImageDraw.Draw(out)
    draw.text((w // 2 - 20, 10), "REF", fill=(255, 255, 255))
    draw.text((w + 4 + w // 2 - 30, 10), "RESULT", fill=(255, 255, 255))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
