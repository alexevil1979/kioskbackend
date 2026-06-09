#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEV_MODE", "true")
os.environ["CRM_USE_MOCK"] = "true"
SCROLL = os.environ.get("ADMIN_PANEL_SCROLL", "top")
OUT = ROOT / "logs" / "admin_panel_app_full.png"


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
    win = MainWindow(settings, CatalogStore(settings), Cart(), NavigationController(), IdleTimer(settings.idle), KeyboardBlocker())
    win.show()
    win._screens[AppScreen.CATEGORIES]._admin_panel.show_modal(scroll=SCROLL)
    app.processEvents()

    def _shot() -> None:
        p = win._screens[AppScreen.CATEGORIES]._admin_panel
        p.scroll_to(SCROLL)
        app.processEvents()
        target = win._shell if getattr(win, "_shell", None) else win
        target.grab().save(str(OUT))
        print(f"saved {OUT}")
        app.quit()

    QTimer.singleShot(400, _shot)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
