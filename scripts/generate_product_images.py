#!/usr/bin/env python3
"""Генерация демо-фото товаров для киоска (Pillow)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "demo_products"
W, H = 520, 390

PRODUCTS: list[tuple[str, str, str, str]] = [
    ("1", "Клубника", "#C62828", "#FFEBEE"),
    ("2", "Малина", "#AD1457", "#FCE4EC"),
    ("3", "Черника", "#4527A0", "#EDE7F6"),
    ("4", "Молоко 3,2%", "#1565C0", "#E3F2FD"),
    ("5", "Творог", "#F5F5F5", "#ECEFF1"),
    ("6", "Сметана", "#FFF8E1", "#FFFDE7"),
    ("7", "Мёд липовый", "#F9A825", "#FFF8E1"),
    ("8", "Мёд гречишный", "#E65100", "#FBE9E7"),
    ("9", "Картофель", "#8D6E63", "#EFEBE9"),
    ("10", "Морковь", "#EF6C00", "#FFF3E0"),
    ("11", "Яйца С0", "#FDD835", "#FFFDE7"),
    ("12", "Укроп", "#2E7D32", "#E8F5E9"),
]


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_product(pid: str, title: str, accent: str, bg: str) -> Image.Image:
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((16, 16, W - 16, H - 16), radius=24, fill="white", outline=accent, width=4)
    cx, cy = W // 2, H // 2 - 20
    r = min(W, H) // 5
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=accent, outline="white", width=3)
    draw.ellipse((cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2), fill=bg)
    font = _font(36)
    bbox = draw.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H - 72), title, fill="#2C2416", font=font)
    small = _font(18)
    draw.text((24, 28), "Ферма", fill=accent, font=small)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for pid, title, accent, bg in PRODUCTS:
        path = OUT / f"{pid}.jpg"
        draw_product(pid, title, accent, bg).save(path, "JPEG", quality=88)
        print("OK", path)
    hero = Image.new("RGB", (1080, 600), "#3D7C2E")
    d = ImageDraw.Draw(hero)
    d.rectangle((0, 0, 1080, 600), fill="#2D5016")
    d.ellipse((340, 80, 740, 480), fill="#4CAF50")
    f = _font(72)
    t = "Ферма"
    bb = d.textbbox((0, 0), t, font=f)
    d.text(((1080 - bb[2] + bb[0]) // 2, 220), t, fill="white", font=f)
    hero.save(ROOT / "assets" / "branding" / "farm_hero.jpg", "JPEG", quality=90)
    print("OK hero")


if __name__ == "__main__":
    main()
