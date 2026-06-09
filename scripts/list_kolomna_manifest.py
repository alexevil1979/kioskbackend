#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "Сады Коломны - Киоск (offline).html").read_text(encoding="utf-8")
manifest = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', text, re.DOTALL).group(1))
ext = json.loads(re.search(r'<script type="__bundler/ext_resources">(.*?)</script>', text, re.DOTALL).group(1))
print("ext_resources:")
for item in ext:
    print(" ", item.get("id"), "->", item.get("uuid"), item.get("mime", ""))
print("\nmanifest images:")
for uid, entry in manifest.items():
    if entry.get("mime", "").startswith("image/"):
        print(" ", uid, entry.get("mime"), entry.get("compressed"))
