#!/usr/bin/env python3
"""Конвертация woff2 → ttf для PyQt6."""
from __future__ import annotations

from pathlib import Path

from fontTools.ttLib.woff2 import decompress as woff2_decompress

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "kolomna" / "fonts"
DST = ROOT / "assets" / "kolomna" / "fonts"

# cyrillic subset — основной для киоска
CYRILLIC = SRC / "9a6b637a-21e6-4ca7-9587-c0ea694a5695.woff2"


def convert(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(src)
    woff2_decompress(str(src), str(dst))
    print(f"OK {dst.name} ({dst.stat().st_size} bytes)")


def main() -> None:
    convert(CYRILLIC, DST / "Montserrat-Medium.ttf")


if __name__ == "__main__":
    main()
