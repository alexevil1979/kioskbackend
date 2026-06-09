#!/usr/bin/env python3
"""Admin panel: ref vs app — всегда side-by-side PNG (REF | RESULT)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.kolomna_compare_common import mean_diff_pct  # noqa: E402

THRESHOLD = 1.0
CREAM = (246, 239, 216)
ASSETS = Path(r"C:\Users\1\.cursor\projects\c-Users-1-Documents\assets")


def _grab(scroll: str) -> None:
    env = {**os.environ, "ADMIN_PANEL_SCROLL": scroll}
    subprocess.run([sys.executable, str(ROOT / "scripts" / "grab_admin_panel_ref.py")], check=True, env=env)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "grab_admin_panel.py")], check=True, env=env)


def _align(ref: Image.Image, app: Image.Image) -> tuple[Image.Image, Image.Image]:
    w = min(ref.width, app.width)
    h = min(ref.height, app.height)
    return ref.crop((0, 0, w, h)).convert("RGB"), app.crop((0, 0, w, h)).convert("RGB")


def _side_by_side(
    ref: Image.Image,
    app: Image.Image,
    out: Path,
    *,
    label: str = "",
    diff_pct: float | None = None,
) -> None:
    w, h = ref.size
    title_h = 40
    combo = Image.new("RGB", (w * 2 + 8, h + title_h), (30, 30, 30))
    combo.paste(ref, (0, title_h))
    combo.paste(app, (w + 8, title_h))
    draw = ImageDraw.Draw(combo)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
        font_sm = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        font = font_sm = ImageFont.load_default()
    draw.text((w // 2 - 18, 10), "REF", fill=(220, 220, 220), font=font)
    draw.text((w + 8 + w // 2 - 32, 10), "RESULT", fill=(220, 220, 220), font=font)
    if label or diff_pct is not None:
        extra = label
        if diff_pct is not None:
            extra = f"{label}  diff {diff_pct:.2f}%".strip()
        draw.text((8, 10), extra, fill=(180, 180, 180), font=font_sm)
    out.parent.mkdir(parents=True, exist_ok=True)
    combo.save(out)
    print(f"saved {out}")


def _stack_vertical(top: Image.Image, bottom: Image.Image, out: Path) -> None:
    w = max(top.width, bottom.width)
    h = top.height + bottom.height + 4
    combo = Image.new("RGB", (w, h), (30, 30, 30))
    combo.paste(top, (0, 0))
    combo.paste(bottom, (0, top.height + 4))
    combo.save(out)
    print(f"saved {out}")


def _compare(scroll: str) -> tuple[float, Image.Image, Image.Image]:
    _grab(scroll)
    ref, app = _align(
        Image.open(ROOT / "logs" / "admin_panel_ref.png"),
        Image.open(ROOT / "logs" / "admin_panel_app.png"),
    )
    pct = mean_diff_pct(ref, app)
    print(f"scroll={scroll:6s} size={ref.size} mean_diff={pct:.3f}%")
    return pct, ref, app


def main() -> int:
    logs = ROOT / "logs"
    pct_top, ref_t, app_t = _compare("top")
    pct_bot, ref_b, app_b = _compare("bottom")
    pct = max(pct_top, pct_bot)

    top_png = logs / "admin_panel_compare_top.png"
    bot_png = logs / "admin_panel_compare_bottom.png"
    full_png = logs / "admin_panel_compare_full.png"

    _side_by_side(ref_t, app_t, top_png, label="scroll top", diff_pct=pct_top)
    _side_by_side(ref_b, app_b, bot_png, label="scroll bottom", diff_pct=pct_bot)

    top_img = Image.open(top_png)
    bot_img = Image.open(bot_png)
    _stack_vertical(top_img, bot_img, full_png)

    ASSETS.mkdir(parents=True, exist_ok=True)
    for src, name in (
        (top_png, "admin_panel_compare_top.png"),
        (bot_png, "admin_panel_compare_bottom.png"),
        (full_png, "admin_panel_compare_full.png"),
    ):
        Image.open(src).save(ASSETS / name)

    ImageChops.difference(ref_t, app_t).save(logs / "admin_panel_diff_top.png")

    status = "PASS" if pct <= THRESHOLD else "FAIL"
    print(f"{status} max mean diff {pct:.3f}% (threshold {THRESHOLD}%)")
    return 0 if pct <= THRESHOLD else 1


if __name__ == "__main__":
    raise SystemExit(main())
