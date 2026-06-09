#!/usr/bin/env python3
"""Скриншот заставки Kolomna (dev viewport 499×913)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEV_MODE", "true")

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.core.config import load_settings
from src.ui.kolomna_fonts import setup_kolomna_fonts
from src.ui.screens.start_screen import StartScreen


def main() -> None:
    app = QApplication(sys.argv)
    setup_kolomna_fonts(app)
    settings = load_settings()
    screen = StartScreen(settings)
    screen.resize(settings.app.viewport_width, settings.app.viewport_height)
    screen.show()

    out = ROOT / "logs" / "start_screen_kolomna.png"

    def grab() -> None:
        ok = screen.grab().save(str(out))
        print(f"screenshot={out} ok={ok} size={screen.width()}x{screen.height()}")
        app.quit()

    QTimer.singleShot(400, grab)
    app.exec()


if __name__ == "__main__":
    main()
