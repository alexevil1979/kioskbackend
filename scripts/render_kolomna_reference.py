#!/usr/bin/env python3
"""Скриншоты экранов из offline HTML-референса (Playwright, viewport 499×913)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "Сады Коломны - Киоск (offline).html"
OUT = ROOT / "logs" / "kolomna_ref"
VIEW_W, VIEW_H = 499, 913


def _url() -> str:
    return HTML.resolve().as_uri()


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
    steps: list[tuple[str, str]] = [
        ("01_attract", ""),
        ("02_categories", "document.querySelector('.attract')?.click()"),
        ("03_menu", "document.querySelectorAll('.cat-card')[0]?.click()"),
        ("04_tours", """
            (() => {
              const cards = document.querySelectorAll('.cat-card');
              if (cards[3]) cards[3].click();
            })()
        """),
        ("05_cart_empty", """
            (() => {
              const back = document.querySelector('.topbar__back');
              if (back) back.click();
              setTimeout(() => {
                const cards = document.querySelectorAll('.cat-card');
                if (cards[0]) cards[0].click();
              }, 200);
            })()
        """),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": VIEW_W, "height": VIEW_H})
        page.goto(_url(), wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(800)

        # Сброс localStorage к дефолтам референса
        page.evaluate(
            """() => {
              localStorage.removeItem('sk_showAttract');
              localStorage.removeItem('sk_menuLayout');
              location.reload();
            }"""
        )
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        def dismiss_errors() -> None:
            page.evaluate(
                """() => {
                  const el = document.getElementById('__bundler_err');
                  if (el) el.remove();
                }"""
            )

        def pause_animations() -> None:
            page.evaluate(
                """() => {
                  document.querySelectorAll('*').forEach(el => {
                    el.getAnimations?.().forEach(a => a.pause());
                  });
                  const st = document.createElement('style');
                  st.id = '__pause_anim';
                  st.textContent = '*, *::before, *::after { animation-play-state: paused !important; }';
                  if (!document.getElementById('__pause_anim')) document.head.appendChild(st);
                }"""
            )

        def shot(name: str) -> None:
            dismiss_errors()
            pause_animations()
            path = OUT / f"{name}.png"
            page.screenshot(path=str(path), full_page=False)
            print(f"ref {name} -> {path}")

        shot("01_attract")
        dismiss_errors()
        page.click(".attract", force=True)
        page.wait_for_timeout(600)
        shot("02_categories")

        dismiss_errors()
        page.locator(".cat-card").nth(0).click(force=True)
        page.wait_for_timeout(600)
        shot("03_menu")

        dismiss_errors()
        page.locator(".topbar__back").click(force=True)
        page.wait_for_timeout(400)
        dismiss_errors()
        page.locator(".cat-card").nth(3).click(force=True)
        page.wait_for_timeout(600)
        shot("04_tours")

        # Корзина: сначала с товаром, затем пустая (remove)
        dismiss_errors()
        page.locator(".topbar__back").click(force=True)
        page.wait_for_timeout(400)
        page.locator(".cat-card").nth(0).click(force=True)
        page.wait_for_timeout(400)
        add_btn = page.locator(".prod-row .btn--yellow, .prod-row button").first
        if add_btn.count():
            add_btn.click(force=True)
            page.wait_for_timeout(500)
        cart_open = page.locator(".screen__footbar button, .cart-pill").first
        if cart_open.count():
            cart_open.click(force=True)
            page.wait_for_timeout(600)
            shot("06_cart_filled")
            remove = page.locator(".cart-row__remove").first
            if remove.count():
                remove.click(force=True)
                page.wait_for_timeout(600)
                shot("05_cart_empty")
            # снова в меню и в корзину для оплаты
            page.locator(".topbar__back").click(force=True)
            page.wait_for_timeout(400)
            page.locator(".cat-card").nth(0).click(force=True)
            page.wait_for_timeout(400)
            if add_btn.count():
                add_btn.click(force=True)
                page.wait_for_timeout(400)
            if cart_open.count():
                cart_open.click(force=True)
                page.wait_for_timeout(500)

        dismiss_errors()
        page.locator(".btn--primary").filter(has_text="оплат").first.click(force=True)
        page.wait_for_timeout(500)
        shot("07_payment")

        dismiss_errors()
        page.locator(".pay-method").first.click(force=True)
        page.wait_for_timeout(300)
        page.locator("button").filter(has_text="Оплатить").first.click(force=True)
        page.wait_for_timeout(500)
        shot("08_sbp_spin")

        page.wait_for_timeout(1500)
        shot("09_sbp_qr")

        try:
            page.wait_for_selector(".done__title", timeout=9000)
            shot("10_done")
        except Exception:
            pass

        # Info modal — с экрана категорий
        page.goto(_url(), wait_until="networkidle")
        page.wait_for_timeout(800)
        dismiss_errors()
        page.click(".attract", force=True)
        page.wait_for_timeout(400)
        dismiss_errors()
        page.locator(".catalog__info").click(force=True)
        page.wait_for_timeout(500)
        shot("10_info_modal")

        browser.close()

    manifest = sorted(p.name for p in OUT.glob("*.png"))
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"done: {len(manifest)} shots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
