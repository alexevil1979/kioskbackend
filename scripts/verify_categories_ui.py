"""Снимок экрана «КАТЕГОРИИ» для сверки с reference (запуск без GUI блокирует)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QTimer  # noqa: E402
from PyQt6.QtWidgets import QApplication, QStyleFactory  # noqa: E402

from src.core.cart import Cart  # noqa: E402
from src.core.config import load_settings  # noqa: E402
from src.core.state_machine import AppScreen, NavigationController  # noqa: E402
from src.services.catalog_sync import CatalogStore  # noqa: E402
from src.ui.katusha_fonts import setup_katusha_fonts  # noqa: E402
from src.ui.screens.categories_screen import CategoriesScreen  # noqa: E402


def main() -> int:
    settings = load_settings()
    app = QApplication(sys.argv)
    fusion = QStyleFactory.create("Fusion")
    if fusion:
        app.setStyle(fusion)
    setup_katusha_fonts(app)
    styles = ROOT / "src" / "ui" / "styles" / "theme.qss"
    if styles.exists():
        app.setStyleSheet(styles.read_text(encoding="utf-8"))

    catalog = CatalogStore(settings)
    catalog.refresh()

    screen = CategoriesScreen(catalog, settings)
    screen.setFixedSize(settings.app.viewport_width, settings.app.viewport_height)
    screen.show()

    out = ROOT / "logs" / "verify_categories.png"

    def grab() -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        ok = screen.grab().save(str(out))
        summaries = catalog.category_summaries()
        print(f"screenshot={out} ok={ok} cards={len(summaries)}")
        for s in summaries:
            print(f"  - {s.name}: {s.product_count} hero={s.hero}")
        app.quit()

    QTimer.singleShot(1500, grab)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
