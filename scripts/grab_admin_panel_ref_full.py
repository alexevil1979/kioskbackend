#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "Сады Коломны - Киоск (offline).html"
OUT = ROOT / "logs" / "admin_panel_ref_full.png"
SCROLL = os.environ.get("ADMIN_PANEL_SCROLL", "top")


def main() -> int:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 499, "height": 913})
        page.goto(HTML.resolve().as_uri(), wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(800)
        page.click(".attract", force=True)
        page.wait_for_timeout(400)
        info = page.locator(".catalog__info")
        info.dispatch_event("pointerdown")
        page.wait_for_timeout(1300)
        info.dispatch_event("pointerup")
        page.wait_for_timeout(400)
        for d in "1111":
            page.locator(".pin-key").filter(has_text=d).first.click(force=True)
            page.wait_for_timeout(120)
        page.wait_for_timeout(500)
        js = "panel.scrollTop = 0;" if SCROLL == "top" else "panel.scrollTop = panel.scrollHeight;"
        page.evaluate(f"() => {{ const panel = document.querySelector('.admin-panel'); if (panel) {{ {js} }} }}")
        page.wait_for_timeout(400)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUT))
        browser.close()
    print(f"saved {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
