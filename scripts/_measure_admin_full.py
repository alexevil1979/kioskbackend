#!/usr/bin/env python3
"""Full-viewport grab + modal crop compare (legacy pipeline)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.kolomna_compare_common import mean_diff_pct  # noqa: E402

CREAM = (246, 239, 216)


def _modal_crop(im: Image.Image) -> Image.Image:
    px = im.convert("RGB").load()
    w, h = im.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - CREAM[0]) < 8 and abs(g - CREAM[1]) < 8 and abs(b - CREAM[2]) < 8:
                xs.append(x)
                ys.append(y)
    if not xs:
        return im
    return im.crop((min(xs), min(ys), max(xs), max(ys)))


def main() -> None:
    scroll = os.environ.get("ADMIN_PANEL_SCROLL", "top")
    env = {**os.environ, "ADMIN_PANEL_SCROLL": scroll}

    # ref full page
    subprocess.run([sys.executable, str(ROOT / "scripts" / "grab_admin_panel_ref_full.py")], env=env, check=True)

    # app full shell
    subprocess.run([sys.executable, str(ROOT / "scripts" / "grab_admin_panel_full.py")], env=env, check=True)

    ref = _modal_crop(Image.open(ROOT / "logs" / "admin_panel_ref_full.png"))
    app = _modal_crop(Image.open(ROOT / "logs" / "admin_panel_app_full.png"))
    w, h = min(ref.width, app.width), min(ref.height, app.height)
    pct = mean_diff_pct(ref.crop((0, 0, w, h)), app.crop((0, 0, w, h)))
    print(f"full-viewport modal crop scroll={scroll} mean_diff={pct:.3f}%")


if __name__ == "__main__":
    main()
