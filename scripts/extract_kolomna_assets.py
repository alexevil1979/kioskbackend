#!/usr/bin/env python3
"""Извлечь шрифты/картинки из offline HTML «Сады Коломны»."""
from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "Сады Коломны - Киоск (offline).html"
OUT = ROOT / "assets" / "kolomna"


def decode_entry(entry: dict) -> bytes:
    raw = base64.b64decode(entry["data"])
    if entry.get("compressed"):
        raw = gzip.decompress(raw)
    return raw


def main() -> None:
    text = HTML.read_text(encoding="utf-8")
    manifest = json.loads(
        re.search(
            r'<script type="__bundler/manifest">(.*?)</script>',
            text,
            re.DOTALL,
        ).group(1)
    )
    ext = json.loads(
        re.search(
            r'<script type="__bundler/ext_resources">(.*?)</script>',
            text,
            re.DOTALL,
        ).group(1)
    )
    OUT.mkdir(parents=True, exist_ok=True)
    id_map: dict[str, str] = {}
    for item in ext:
        id_map[item["id"]] = item["uuid"]

    for uid, entry in manifest.items():
        mime = entry.get("mime", "")
        blob = decode_entry(entry)
        path = OUT / f"_raw_{uid}"
        if len(blob) < 500_000:
            path.write_bytes(blob)
            print("raw", uid, mime, len(blob))
        if mime == "font/woff2":
            path = OUT / "fonts" / f"{uid}.woff2"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
            print("font", path.name, len(blob))
        elif mime.startswith("image/"):
            ext_name = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/svg+xml": ".svg",
                "image/webp": ".webp",
            }.get(mime, ".bin")
            for rid, ruuid in id_map.items():
                if ruuid == uid:
                    safe = re.sub(r"[^\w.-]+", "_", rid)
                    path = OUT / f"{safe}{ext_name}"
                    path.write_bytes(blob)
                    print("image", path.name, len(blob))


if __name__ == "__main__":
    main()
