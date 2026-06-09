#!/usr/bin/env python3
"""Экспорт QR из offline-референса (qrcode-generator) → assets/kolomna/qr/."""
from __future__ import annotations

import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "Сады Коломны - Киоск (offline).html"
OUT = ROOT / "assets" / "kolomna" / "qr"
VIEW_W = 499


def _save_data_url(data_url: str, path: Path) -> None:
    raw = base64.b64decode(data_url.split(",", 1)[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    print(f"saved {path.name}")


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("pip install playwright && playwright install chromium", file=sys.stderr)
        return 1
    if not HTML.is_file():
        print(f"Нет файла: {HTML}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    info_disp = round(248 * VIEW_W / 1080)
    pay_disp = round(572 * VIEW_W / 1080)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": VIEW_W, "height": 913})
        page.goto(HTML.resolve().as_uri(), wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(800)

        page.click(".attract", force=True)
        page.wait_for_timeout(400)
        page.click(".catalog__info", force=True)
        page.wait_for_timeout(600)

        urls = page.evaluate(
            """() => Array.from(document.querySelectorAll('.info-qr__box canvas')).map(cv => cv.toDataURL('image/png'))"""
        )
        labels = ("site", "tg", "vk", "max")
        canvases = page.locator(".info-qr__box canvas")
        for label, data_url in zip(labels, urls):
            _save_data_url(data_url, OUT / f"info_{label}_460.png")
            idx = labels.index(label)
            canvases.nth(idx).screenshot(path=str(OUT / f"info_{label}_{info_disp}.png"))
            print(f"saved info_{label}_{info_disp}.png (screenshot)")

        page.goto(HTML.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(800)
        page.click(".attract", force=True)
        page.wait_for_timeout(400)
        page.locator(".cat-card").nth(0).click(force=True)
        page.wait_for_timeout(400)
        page.locator(".prod-row button").first.click(force=True)
        page.wait_for_timeout(400)
        page.locator(".screen__footbar button, .cart-pill").first.click(force=True)
        page.wait_for_timeout(500)
        page.locator(".btn--primary").filter(has_text="оплат").first.click(force=True)
        page.wait_for_timeout(400)
        page.locator(".pay-method").first.click(force=True)
        page.wait_for_timeout(300)
        page.locator("button").filter(has_text="Оплатить").first.click(force=True)
        page.wait_for_timeout(2000)

        pay_url = page.evaluate(
            """() => document.querySelector('.pay-qr canvas')?.toDataURL('image/png') || ''"""
        )
        if pay_url:
            _save_data_url(pay_url, OUT / "pay_sbp_560.png")
            page.locator(".pay-qr canvas").screenshot(path=str(OUT / f"pay_sbp_{pay_disp}.png"))
            print(f"saved pay_sbp_{pay_disp}.png (screenshot)")

        browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
