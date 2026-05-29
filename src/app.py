from __future__ import annotations

import sys
from pathlib import Path

# Корень проекта в PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from src.core.cart import Cart
from src.core.config import load_settings
from src.core.idle_timer import IdleTimer
from src.core.kiosk_win import KeyboardBlocker
from src.core.logging_setup import setup_logging
from src.core.state_machine import NavigationController
from src.services.catalog_sync import CatalogStore
from src.ui.main_window import MainWindow


def _load_styles(app: QApplication) -> None:
    qss_path = ROOT / "src" / "ui" / "styles" / "theme.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


def run() -> int:
    settings = load_settings()
    setup_logging(settings)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(settings.app.title)

    font = QFont("Segoe UI", 12)
    app.setFont(font)
    _load_styles(app)

    keyboard = KeyboardBlocker()
    if settings.kiosk.block_keys:
        keyboard.install()

    cart = Cart()
    nav = NavigationController()
    idle = IdleTimer(settings.idle)
    catalog = CatalogStore(settings)

    window = MainWindow(settings, catalog, cart, nav, idle, keyboard)
    window.show()

    code = app.exec()
    keyboard.uninstall()
    return code
