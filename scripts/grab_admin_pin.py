#!/usr/bin/env python3
"""Скриншот модалки admin PIN для сверки с референсом."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEV_MODE", "true")
os.environ["CRM_USE_MOCK"] = "true"

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.core.cart import Cart
from src.core.config import load_settings
from src.core.idle_timer import IdleTimer
from src.core.kiosk_win import KeyboardBlocker
from src.core.state_machine import AppScreen, NavigationController
from src.services.catalog_sync import CatalogStore
from src.ui.kolomna_fonts import setup_kolomna_fonts
from src.ui.main_window import MainWindow


def main() -> None:
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
    nav.go(AppScreen.CATEGORIES)
    app.processEvents()

    cats = win._screens[AppScreen.CATEGORIES]
    cats._admin_pin.show_modal()
    app.processEvents()

    out = ROOT / "logs" / "admin_pin_app.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    target = win._shell if getattr(win, "_shell", None) else win._stack.currentWidget()

    def _shot() -> None:
        pix = target.grab()
        pix.save(str(out))
        print(f"saved {out} ({pix.width()}x{pix.height()})")
        app.quit()

    QTimer.singleShot(400, _shot)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
