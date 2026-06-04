#!/usr/bin/env python3
"""Проверка вёрстки экрана «КАТЕГОРИИ»: скриншот + геометрия карточек 1:1."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QTimer  # noqa: E402
from PyQt6.QtWidgets import QApplication, QStyleFactory  # noqa: E402

from src.core.config import load_settings  # noqa: E402
from src.services.catalog_sync import CatalogStore  # noqa: E402
from src.ui.katusha_fonts import setup_katusha_fonts  # noqa: E402
from src.ui.katusha_hub_tokens import (  # noqa: E402
    HUB_SCROLL_H,
    SLOT_HERO,
    SLOTS_HALF,
    Y_HEADER,
    hub_content_height,
)
from src.ui.screens.categories_screen import CategoriesScreen  # noqa: E402
from src.ui.widgets.category_hub_card import CategoryHubCard  # noqa: E402

_TOL = 2


def _geom(widget, content) -> tuple[int, int, int, int]:
    tl = widget.mapTo(content, widget.rect().topLeft())
    return tl.x(), tl.y(), widget.width(), widget.height()


def _check_geometry(screen: CategoriesScreen) -> list[str]:
    errors: list[str] = []
    content = screen._scroll_content
    heroes = content.findChildren(CategoryHubCard, "CategoryHubHero")
    cards = content.findChildren(CategoryHubCard, "CategoryHubCard")

    summaries = screen._scroll_content._summaries
    want_h = hub_content_height(len(summaries))
    if content.height() != want_h:
        errors.append(f"content h={content.height()}, ожидали {want_h}")
    if screen._scroll.height() != HUB_SCROLL_H:
        errors.append(
            f"scroll h={screen._scroll.height()}, ожидали {HUB_SCROLL_H}"
        )

    if len(heroes) != 1:
        errors.append(f"ожидали 1 hero, получили {len(heroes)}")
    if not cards:
        errors.append("нет карточек категорий")

    if heroes:
        g = _geom(heroes[0], content)
        exp = SLOT_HERO
        for name, got, want in zip("xywh", g, exp):
            if abs(got - want) > _TOL:
                errors.append(f"hero {name}: {got} != {want}")
                break

    for i, card in enumerate(cards):
        if i >= len(SLOTS_HALF):
            break
        g = _geom(card, content)
        exp = SLOTS_HALF[i]
        for name, got, want in zip("xywh", g, exp):
            if abs(got - want) > _TOL:
                errors.append(f"card[{i}] {name}: {got} != {want}")
                break

    for i, a in enumerate(cards):
        for j, b in enumerate(cards):
            if j <= i:
                continue
            if a.geometry().intersects(b.geometry()):
                errors.append(f"пересечение карточек {i} и {j}")

    header = screen._header
    if header.height() != Y_HEADER:
        errors.append(f"header h={header.height()}, ожидали {Y_HEADER}")

    return errors


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
    errors: list[str] = []

    def finish() -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        ok = screen.grab().save(str(out))
        errors.extend(_check_geometry(screen))
        summaries = catalog.category_summaries()
        print(f"screenshot={out} ok={ok} cards={len(summaries)}")
        for s in summaries:
            print(f"  - {s.name}: {s.product_count} hero={s.hero}")
        if errors:
            print("LAYOUT ERRORS:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("layout ok")
        app.quit()

    QTimer.singleShot(1500, finish)
    code = app.exec()
    return 1 if errors else code


if __name__ == "__main__":
    raise SystemExit(main())
