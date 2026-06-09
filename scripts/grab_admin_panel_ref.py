#!/usr/bin/env python3
"""Grab admin panel ref — crop только .admin-panel."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "Сады Коломны - Киоск (offline).html"
OUT = ROOT / "logs" / "admin_panel_ref.png"
SCROLL = os.environ.get("ADMIN_PANEL_SCROLL", "top")


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("pip install playwright", file=sys.stderr)
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 499, "height": 913})
        page.goto(HTML.resolve().as_uri(), wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(800)
        page.evaluate(
            """() => {
              localStorage.removeItem('sk_showAttract');
              localStorage.removeItem('sk_menuLayout');
              localStorage.removeItem('sk_ctaColor');
              localStorage.removeItem('sk_skipProduct');
              localStorage.removeItem('sk_hours');
            }"""
        )
        page.reload(wait_until="networkidle")
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
        scroll_js = (
            "panel.scrollTop = 0;"
            if SCROLL == "top"
            else "panel.scrollTop = panel.scrollHeight;"
        )
        page.evaluate(
            f"""() => {{
              const panel = document.querySelector('.admin-panel');
              if (panel) {{ {scroll_js} }}
            }}"""
        )
        page.wait_for_timeout(400)
        panel = page.locator(".admin-panel").first
        OUT.parent.mkdir(parents=True, exist_ok=True)
        panel.screenshot(path=str(OUT))
        box = panel.bounding_box()
        print(f"saved {OUT} {box}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
