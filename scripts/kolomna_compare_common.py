#!/usr/bin/env python3
"""Общие утилиты pixel-compare Kolomna (референс HTML vs PyQt)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "logs" / "kolomna_ref"
APP_DIR = ROOT / "logs" / "kolomna_app"
DIFF_DIR = ROOT / "logs" / "kolomna_diff"

KIOSK_W = 1080
KIOSK_H = 1920


def kiosk_scale(viewport_w: int, viewport_h: int) -> float:
    return min(viewport_w / KIOSK_W, viewport_h / KIOSK_H)


def content_size(viewport_w: int, viewport_h: int) -> tuple[int, int]:
    """Рабочая область = весь viewport (499×913), без letterbox."""
    return viewport_w, viewport_h


def crop_kiosk_content(img: Image.Image) -> Image.Image:
    """Обрезка letterbox как в KioskStage (чёрные поля сверху/снизу)."""
    w, h = img.size
    cw, ch = content_size(w, h)
    x0 = max(0, (w - cw) // 2)
    y0 = max(0, (h - ch) // 2)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.Resampling.LANCZOS)


def mean_diff_pct(a: Image.Image, b: Image.Image, *, threshold: int = 18) -> float:
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.LANCZOS)
    if a.mode != "RGB":
        a = a.convert("RGB")
    if b.mode != "RGB":
        b = b.convert("RGB")
    diff = ImageChops.difference(a, b)
    lum = a.convert("L")
    diff_px = list(diff.getdata())
    mask_px = list(lum.getdata())
    total = 0.0
    count = 0
    for i, lum_v in enumerate(mask_px):
        if lum_v > 12:
            r, g, b = diff_px[i]
            total += r + g + b
            count += 3
    if count == 0:
        return 100.0
    return total / count / 255 * 100


def save_diff(a: Image.Image, b: Image.Image, out: Path, *, amplify: int = 4) -> float:
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.LANCZOS)
    a = a.convert("RGB")
    b = b.convert("RGB")
    diff = ImageChops.difference(a, b)
    pct = mean_diff_pct(a, b)
    boosted = diff.point(lambda p: min(255, p * amplify))
    out.parent.mkdir(parents=True, exist_ok=True)
    boosted.save(out)
    return pct


def compare_pair(name: str, *, crop_ref: bool = False) -> dict:
    ref_path = REF_DIR / f"{name}.png"
    app_path = APP_DIR / f"{name}.png"
    if not ref_path.is_file():
        return {"name": name, "error": f"no ref: {ref_path}"}
    if not app_path.is_file():
        return {"name": name, "error": f"no app: {app_path}"}
    ref = crop_kiosk_content(Image.open(ref_path).convert("RGB"))
    app = crop_kiosk_content(Image.open(app_path).convert("RGB"))
    if crop_ref:
        ref = crop_kiosk_content(ref)
    if app.size != ref.size:
        app = app.resize(ref.size, Image.Resampling.LANCZOS)
    pct = mean_diff_pct(ref, app)
    save_diff(ref, app, DIFF_DIR / f"{name}.png")
    return {"name": name, "diff_pct": round(pct, 2)}
