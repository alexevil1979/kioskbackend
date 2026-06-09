#!/usr/bin/env python3
"""Grab admin panel — crop только .admin-panel / KolomnaAdminPanelBox."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEV_MODE", "true")
os.environ["CRM_USE_MOCK"] = "true"
SCROLL = os.environ.get("ADMIN_PANEL_SCROLL", "top")
OUT = ROOT / "logs" / "admin_panel_app.png"


def main() -> None:
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication

    from src.core.cart import Cart
    from src.core.config import load_settings
    from src.core.idle_timer import IdleTimer
    from src.core.kiosk_win import KeyboardBlocker
    from src.core.state_machine import AppScreen, NavigationController
    from src.services.catalog_sync import CatalogStore
    from src.ui.kolomna_fonts import setup_kolomna_fonts
    from src.ui.kolomna_prefs import KolomnaPrefs
    from src.ui.main_window import MainWindow

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
    panel = cats._admin_panel
    panel._prefs = KolomnaPrefs()
    panel.show_modal(scroll=SCROLL)
    app.processEvents()

    def _shot() -> None:
        panel.scroll_to(SCROLL)
        app.processEvents()
        pix = panel._box.grab()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(OUT))
        print(f"saved {OUT} {pix.width()}x{pix.height()}")
        app.quit()

    QTimer.singleShot(400, _shot)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
