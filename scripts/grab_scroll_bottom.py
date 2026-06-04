#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QStyleFactory

from src.core.config import load_settings
from src.services.catalog_sync import CatalogStore
from src.ui.katusha_fonts import setup_katusha_fonts
from src.ui.screens.categories_screen import CategoriesScreen


def main() -> int:
    settings = load_settings()
    app = QApplication(sys.argv)
    if fusion := QStyleFactory.create("Fusion"):
        app.setStyle(fusion)
    setup_katusha_fonts(app)
    qss = ROOT / "src" / "ui" / "styles" / "theme.qss"
    if qss.exists():
        app.setStyleSheet(qss.read_text(encoding="utf-8"))

    screen = CategoriesScreen(CatalogStore(settings), settings)
    screen.show()

    def snap() -> None:
        bar = screen._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())
        app.processEvents()
        out = ROOT / "logs" / "scroll_test" / "scroll_bottom_new.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        screen.grab().save(str(out))
        print(f"max={bar.maximum()} saved {out}")
        app.quit()

    QTimer.singleShot(900, snap)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
