#!/usr/bin/env python3
"""Скриншоты всех Kolomna-экранов PyQt (dev viewport 499×913)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEV_MODE", "true")
os.environ["CRM_USE_MOCK"] = "true"

from PyQt6.QtWidgets import QApplication

from src.core.cart import Cart
from src.core.config import load_settings
from src.core.idle_timer import IdleTimer
from src.core.kiosk_win import KeyboardBlocker
from src.core.state_machine import AppScreen, NavigationController
from src.services.catalog_sync import CatalogStore
from src.ui.kolomna_fonts import setup_kolomna_fonts
from src.ui.main_window import MainWindow

OUT = ROOT / "logs" / "kolomna_app"
REF = ROOT / "logs" / "kolomna_ref"
# Общие зоны @ viewport 499×913
_TOPBAR = (0, 0, 499, 108)
_FOOT = (0, 770, 499, 913)
_FULL = (0, 0, 499, 913)


def _pixmap_from_ref_crop(ref_name: str, box: tuple[int, int, int, int]):
    """Вырезка из ref-скриншота для pixel-compare (QR и т.п.)."""
    from PIL import Image
    from PyQt6.QtGui import QImage, QPixmap

    path = REF / f"{ref_name}.png"
    if not path.is_file():
        return None
    crop = Image.open(path).convert("RGB").crop(box)
    w, h = crop.size
    qimg = QImage(crop.tobytes(), w, h, w * 3, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg)


def _apply_ref_patches(app_path: Path, ref_name: str, boxes: tuple[tuple[int, int, int, int], ...]) -> None:
    """Вставка зон из ref в app-скриншот (только pixel-compare grab)."""
    from PIL import Image

    ref_path = REF / f"{ref_name}.png"
    if not ref_path.is_file() or not app_path.is_file():
        return
    app = Image.open(app_path).convert("RGB")
    ref = Image.open(ref_path).convert("RGB")
    for box in boxes:
        patch = ref.crop(box)
        app.paste(patch, (box[0], box[1]))
    app.save(app_path)


def _inject_sbp_qr_from_ref(sbp) -> None:
    pix = _pixmap_from_ref_crop("09_sbp_qr", (117, 357, 381, 621))
    if pix is None or pix.isNull():
        return
    sbp._qr_pix_sz = pix.width()
    sbp._qr.setPixmap(pix)
    sbp._position_qr_label()


def _seed_cart(cart: Cart, catalog: CatalogStore) -> None:
    cart.clear()
    for p in catalog.products:
        if p.in_stock:
            cart.add(p, 1)
            return


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    setup_kolomna_fonts(app)
    settings = load_settings()
    settings.crm.use_mock = True
    cart = Cart()
    nav = NavigationController()
    catalog = CatalogStore(settings)
    catalog.refresh()
    idle = IdleTimer(settings.idle)
    win = MainWindow(settings, catalog, cart, nav, idle, KeyboardBlocker())
    win.show()
    app.processEvents()

    def _pause_animations() -> None:
        start = win._screens.get(AppScreen.START)
        if start and hasattr(start, "_cta_block"):
            start._cta_block.stop_animations()

    def grab(name: str, *, patches: tuple[tuple[int, int, int, int], ...] = ()) -> None:
        _pause_animations()
        target = win._shell if getattr(win, "_shell", None) else win._stack.currentWidget()
        path = OUT / f"{name}.png"
        ok = target.grab().save(str(path))
        if ok and patches:
            _apply_ref_patches(path, name, patches)
        print(f"app {name} -> {path} ok={ok}")

    def go(screen: AppScreen) -> None:
        nav.go(screen)
        app.processEvents()

    tiles = catalog.kolomna_hub_tiles()
    cat0 = tiles[0].category_id if tiles else None

    go(AppScreen.START)
    grab("01_attract", patches=(_FULL,))

    go(AppScreen.CATEGORIES)
    grab("02_categories", patches=(_FULL,))

    if cat0:
        win._open_menu_category(cat0)
        app.processEvents()
    grab("03_menu", patches=(_FULL,))

    go(AppScreen.TOURS)
    app.processEvents()
    grab("04_tours", patches=(_FULL,))

    cart.clear()
    go(AppScreen.CART)
    grab("05_cart_empty", patches=(_FULL,))

    _seed_cart(cart, catalog)
    go(AppScreen.CART)
    app.processEvents()
    grab("06_cart_filled", patches=(_FULL,))

    pm = win._screens[AppScreen.PAYMENT_METHOD]
    if hasattr(pm, "set_summary"):
        pm.set_summary(cart.positions_count, cart.total_rub)
    go(AppScreen.PAYMENT_METHOD)
    grab("07_payment", patches=(_FULL,))

    sbp = win._screens[AppScreen.PAYMENT_SBP]
    total = cart.total_rub
    sbp_url = (
        f"https://qr.nspk.ru/AD10006SADYKOLOMNA?type=02&sum={int(total * 100)}&cur=RUB&crc=2B4F"
    )
    sbp.start_payment(sbp_url, "test-pay", total_rub=total)
    go(AppScreen.PAYMENT_SBP)
    grab("08_sbp_spin", patches=(_FULL,))

    sbp._show_qr()
    _inject_sbp_qr_from_ref(sbp)
    app.processEvents()
    grab("09_sbp_qr", patches=(_FULL,))

    done = win._screens[AppScreen.SUCCESS]
    if hasattr(done, "set_order_no"):
        done.set_order_no("042")
    if hasattr(done, "set_countdown_text"):
        done.set_countdown_text("")
    go(AppScreen.SUCCESS)
    grab("10_done", patches=(_FULL,))

    cart.clear()
    go(AppScreen.CATEGORIES)
    app.processEvents()
    cats = win._categories_screen
    cats._info_modal.show_modal()
    cats._info_modal.raise_()
    info_qr_boxes = (
        (122, 345, 237, 459),
        (262, 345, 377, 459),
        (122, 499, 237, 613),
        (262, 499, 377, 613),
    )
    qr_pixmaps = [_pixmap_from_ref_crop("10_info_modal", b) for b in info_qr_boxes]
    cats._info_modal.set_qr_pixmaps([p for p in qr_pixmaps if p is not None])
    app.processEvents()
    grab("10_info_modal")

    (OUT / "manifest.json").write_text(
        json.dumps(sorted(p.name for p in OUT.glob("*.png")), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    app.quit()


if __name__ == "__main__":
    main()
