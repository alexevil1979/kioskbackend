from __future__ import annotations

import logging
import sys
import traceback
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


def _load_styles(app: QApplication, settings) -> None:
    styles_dir = ROOT / "src" / "ui" / "styles"
    parts: list[str] = []
    base = styles_dir / "theme.qss"
    if base.exists():
        parts.append(base.read_text(encoding="utf-8"))
    if settings.app.orientation == "portrait" or settings.app.screen_height > settings.app.screen_width:
        portrait = styles_dir / "theme_portrait.qss"
        if portrait.exists():
            parts.append(portrait.read_text(encoding="utf-8"))
    if parts:
        app.setStyleSheet("\n".join(parts))


def _install_excepthook() -> None:
    log = logging.getLogger("kiosk")

    def hook(exc_type, exc, tb):
        log.critical("Необработанное исключение:\n%s", "".join(traceback.format_exception(exc_type, exc, tb)))
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = hook


def run() -> int:
    settings = load_settings()
    setup_logging(settings)
    _install_excepthook()

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(settings.app.title)

    font_size = 14 if settings.app.orientation == "portrait" else 12
    app.setFont(QFont("Segoe UI", font_size))
    _load_styles(app, settings)

    keyboard = KeyboardBlocker()
    if settings.kiosk.block_keys:
        keyboard.install()

    cart = Cart()
    nav = NavigationController()
    idle = IdleTimer(settings.idle)
    catalog = CatalogStore(settings)

    try:
        window = MainWindow(settings, catalog, cart, nav, idle, keyboard)
        window.show()
        code = app.exec()
    except Exception:
        logging.getLogger("kiosk").exception("Критическая ошибка приложения")
        raise
    finally:
        keyboard.uninstall()
    return code
