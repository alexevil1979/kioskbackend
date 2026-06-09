#!/usr/bin/env python3
"""Извлечь design-system из offline HTML «Сады Коломны»."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "Сады Коломны - Киоск (offline).html"
OUT = ROOT / "logs"


def main() -> None:
    text = HTML.read_text(encoding="utf-8")
    m = re.search(
        r'<script type="__bundler/template">(.*?)</script>',
        text,
        re.DOTALL,
    )
    if not m:
        raise SystemExit("template not found")
    tpl: str = json.loads(m.group(1).strip())

    css_start = tpl.find("/* ============================================================")
    css_end = tpl.find("</style>", css_start)
    css = tpl[css_start:css_end] if css_start >= 0 else ""

    body_start = tpl.find("<body")
    body_end = tpl.find("</body>")
    body = tpl[body_start:body_end + 7] if body_start >= 0 else ""

    OUT.mkdir(exist_ok=True)
    (OUT / "kolomna_design_system.css").write_text(css, encoding="utf-8")
    (OUT / "kolomna_body_snippet.html").write_text(body[:50000], encoding="utf-8")

    styles = re.findall(r"<style>(.*?)</style>", tpl, re.DOTALL)
    combined = "\n\n/* ===== BLOCK ===== */\n\n".join(styles)
    (OUT / "kolomna_all_styles.css").write_text(combined, encoding="utf-8")
    print(f"style blocks: {len(styles)}, total {len(combined)} chars")

    vars_ = re.findall(r"--[a-zA-Z0-9_-]+:\s*[^;]+;", css)
    classes = sorted(set(re.findall(r"\.([a-z][a-z0-9_-]{2,30})\b", css)))
    print(f"CSS: {len(css)} chars, vars: {len(vars_)}, classes: {len(classes)}")
    print("\n--- CSS variables ---")
    for v in vars_:
        print(v)
    print("\n--- Sample classes ---")
    for c in classes[:60]:
        print(c)


def extract_js_strings() -> None:
    text = HTML.read_text(encoding="utf-8")
    m = re.search(
        r'<script type="__bundler/template">(.*?)</script>',
        text,
        re.DOTALL,
    )
    if not m:
        return
    tpl: str = json.loads(m.group(1).strip())
    # UI strings from babel bundles
    strings = sorted(
        {
            s.strip()
            for s in re.findall(r'["\']([^"\']{6,120})["\']', tpl)
            if re.search(r"[А-Яа-яЁё]", s)
        },
        key=len,
    )
    out = OUT / "kolomna_ui_strings.txt"
    out.write_text("\n".join(strings), encoding="utf-8")
    print(f"UI strings: {len(strings)} -> {out}")


if __name__ == "__main__":
    main()
    extract_js_strings()
