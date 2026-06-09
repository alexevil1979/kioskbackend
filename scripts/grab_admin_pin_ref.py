#!/usr/bin/env python3
"""Скриншот admin PIN из offline-референса."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "Сады Коломны - Киоск (offline).html"
OUT = ROOT / "logs" / "admin_pin_ref.png"


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
        page.click(".attract", force=True)
        page.wait_for_timeout(500)
        info = page.locator(".catalog__info")
        info.dispatch_event("pointerdown")
        page.wait_for_timeout(1300)
        info.dispatch_event("pointerup")
        page.wait_for_timeout(400)
        page.evaluate(
            """() => {
              document.querySelectorAll('*').forEach(el => {
                el.getAnimations?.().forEach(a => a.pause());
              });
            }"""
        )
        OUT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUT))
        print(f"saved {OUT}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
