#!/usr/bin/env python3
"""Скриншот шапки каталога Kolomna."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEV_MODE", "true")

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

from src.core.config import load_settings
from src.ui.kolomna_fonts import setup_kolomna_fonts
from src.ui.kolomna_tokens import CREAM, KolomnaMetrics, scale
from src.ui.widgets.kolomna_catalog_bar import KolomnaCatalogBar


def main() -> None:
    app = QApplication(sys.argv)
    setup_kolomna_fonts(app)
    settings = load_settings()
    w = settings.app.viewport_width
    m = KolomnaMetrics.from_viewport(w, settings.app.viewport_height)

    host = QWidget()
    host.setFixedSize(w, scale_bar_h := m.tap_min + scale(36 + 28, w))
    host.setStyleSheet(f"background: {CREAM};")
    lay = QVBoxLayout(host)
    lay.setContentsMargins(0, 0, 0, 0)
    bar = KolomnaCatalogBar(m)
    lay.addWidget(bar)

    host.show()
    out = ROOT / "logs" / "catalog_bar_kolomna.png"

    def grab() -> None:
        ok = host.grab().save(str(out))
        print(f"screenshot={out} ok={ok}")
        app.quit()

    QTimer.singleShot(400, grab)
    app.exec()


if __name__ == "__main__":
    main()
