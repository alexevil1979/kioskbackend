#!/usr/bin/env python3
import os, sys
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
from src.ui.kolomna_prefs import KolomnaPrefs
from src.ui.main_window import MainWindow

app = QApplication(sys.argv)
setup_kolomna_fonts(app)
settings = load_settings()
settings.crm.use_mock = True
win = MainWindow(settings, CatalogStore(settings), Cart(), NavigationController(), IdleTimer(settings.idle), KeyboardBlocker())
win.show()
win._screens[AppScreen.CATEGORIES]._admin_panel.show_modal(scroll="top")
app.processEvents()

def probe():
    p = win._screens[AppScreen.CATEGORIES]._admin_panel
    bar = p._scroll.verticalScrollBar()
    print("app scroll", {"max": bar.maximum(), "page": bar.pageStep(), "box_h": p._box.height()})
    app.quit()

QTimer.singleShot(200, probe)
app.exec()
