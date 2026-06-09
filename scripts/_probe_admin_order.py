#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parents[1] / "Сады Коломны - Киоск (offline).html"


def _open_panel(page) -> None:
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
    page.wait_for_timeout(500)


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 499, "height": 913})
    _open_panel(page)
    panel = page.locator(".admin-overlay .admin-panel, .admin-panel").first
    print("panel count", panel.count())
    texts = panel.evaluate(
        """el => {
          const out = [];
          for (const c of el.children) {
            if (c.classList.contains('admin-panel__head')) out.push('HEAD: ' + c.innerText.trim().slice(0,60));
            else if (c.classList.contains('admin-sec')) {
              const top = c.querySelector('.admin-sec__top');
              out.push('SEC: ' + (top ? top.innerText.trim().slice(0,60) : c.className));
            } else out.push('OTHER: ' + c.tagName + '.' + c.className + ' | ' + c.innerText.trim().slice(0,40));
          }
          return out;
        }"""
    )
    for line in texts:
        print(line)
    browser.close()
