#!/usr/bin/env python3
"""Сборка categories_scroll.png из полного референса (скрин с 4 рядами карточек)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (
    ROOT.parent.parent
    / ".cursor"
    / "projects"
    / "c-Users-1-Documents"
    / "assets"
    / "c__Users_1_AppData_Roaming_Cursor_User_workspaceStorage_a777e55647e0af6bd8513d5ba924768d_images_image-f8a5f916-f146-4067-ace3-4a5123126294.png"
)
# fallback в репо, если путь Cursor недоступен
FALLBACK = ROOT / "assets" / "reference" / "categories_full_ref.png"
SCREEN_REF = ROOT / "assets" / "reference" / "screen_katusha.png"
OUT = ROOT / "assets" / "reference" / "categories_scroll.png"
TARGET_W = 499
Y_HEADER, Y_HUB_END = 182, 834


def _find_hero_top(im) -> int:
    w, h = im.size
    for y in range(40, min(220, h)):
        r, g, b = im.getpixel((w // 3, y))
        if r > 120 and g < 120 and b < 120:
            return max(0, y - 4)
    return 70


def _find_content_bottom(im) -> int:
    w, h = im.size
    last_content = h - 1
    for y in range(h - 1, int(h * 0.35), -1):
        row = [im.getpixel((x, y)) for x in range(20, w - 20, 25)]
        non_white = sum(1 for c in row if c != (255, 255, 255))
        if non_white > len(row) * 0.2:
            last_content = y
            break
    return min(h, last_content + 8)


def main() -> None:
    from PIL import Image

    if SCREEN_REF.is_file():
        im = Image.open(SCREEN_REF).convert("RGB")
        strip = im.crop((0, Y_HEADER, im.width, Y_HUB_END))
        OUT.parent.mkdir(parents=True, exist_ok=True)
        strip.save(OUT)
        print(f"saved {OUT} size={strip.size} from screen_katusha y={Y_HEADER}-{Y_HUB_END}")
        return

    src_path = SRC if SRC.is_file() else FALLBACK
    if not src_path.is_file():
        print("missing source", src_path)
        return
    im = Image.open(src_path).convert("RGB")
    nw = TARGET_W
    nh = int(im.height * nw / im.width)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)

    y0 = _find_hero_top(im)
    y1 = _find_content_bottom(im)
    strip = im.crop((0, y0, nw, y1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    strip.save(OUT)
    print(f"saved {OUT} size={strip.size} crop y={y0}-{y1}")


if __name__ == "__main__":
    main()
