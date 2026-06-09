#!/usr/bin/env python3
"""Scroll metrics ref vs app."""
from pathlib import Path

from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parents[1] / "Сады Коломны - Киоск (offline).html"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 499, "height": 913})
    page.goto(HTML.resolve().as_uri(), wait_until="networkidle", timeout=120_000)
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
    m = page.evaluate(
        """() => {
          const p = document.querySelector('.admin-panel');
          return {sh: p.scrollHeight, ch: p.clientHeight, max: p.scrollHeight - p.clientHeight};
        }"""
    )
    print("ref scroll", m)
    browser.close()
