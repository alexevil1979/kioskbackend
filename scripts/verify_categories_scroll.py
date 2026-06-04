#!/usr/bin/env python3
"""Проверка скролла блока категорий: снимки на 0 / mid / max и анализ артефактов."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QTimer, Qt  # noqa: E402
from PyQt6.QtWidgets import QApplication, QStyleFactory  # noqa: E402

from src.core.cart import Cart  # noqa: E402
from src.core.config import load_settings  # noqa: E402
from src.core.state_machine import NavigationController  # noqa: E402
from src.services.catalog_sync import CatalogStore  # noqa: E402
from src.ui.katusha_fonts import setup_katusha_fonts  # noqa: E402
from src.ui.katusha_hub_tokens import HUB_SCROLL_H, NAV_HEIGHT, Y_HEADER  # noqa: E402
from src.ui.screens.categories_screen import CategoriesScreen  # noqa: E402

OUT_DIR = ROOT / "logs" / "scroll_test"
REF_SCROLL = ROOT / "assets" / "reference" / "categories_scroll.png"


def _diff_scroll_vs_ref(screen_path: Path, scroll_y: int, label: str) -> None:
    from PIL import Image, ImageChops, ImageStat

    if not REF_SCROLL.is_file():
        return
    ref = Image.open(REF_SCROLL).convert("RGB")
    screen = Image.open(screen_path).convert("RGB")
    w = ref.width
    view_h = min(ref.height - scroll_y, screen.height - Y_HEADER)
    crop_ref = ref.crop((0, scroll_y, w, scroll_y + view_h))
    crop_scr = screen.crop((0, Y_HEADER, w, Y_HEADER + crop_ref.height))
    if crop_scr.size != crop_ref.size:
        crop_scr = crop_scr.resize(crop_ref.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(crop_ref, crop_scr)
    pct = sum(ImageStat.Stat(diff).mean) / 3.0 / 255.0 * 100.0
    print(f"  [{label}] vs ref @y={scroll_y}: diff={pct:.2f}%")


def _analyze_white_bands(img_path: Path, label: str) -> None:
    from PIL import Image

    im = Image.open(img_path).convert("RGB")
    w, h = im.size
    # полоса скролла в скрине: ниже шапки
    y0, y1 = Y_HEADER, h
    row_white = []
    for y in range(y0, y1, 8):
        row = [im.getpixel((x, y)) for x in range(17, w - 17, 40)]
        pure = sum(1 for c in row if c == (255, 255, 255)) / max(1, len(row))
        if pure > 0.85:
            row_white.append(y)
    if row_white:
        print(f"  [{label}] широкие белые полосы y={row_white[:6]}...")
    else:
        print(f"  [{label}] белых разрывов в зоне карточек не найдено")


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

    scroll = screen._scroll
    bar = scroll.verticalScrollBar()
    max_val = bar.maximum()
    steps = [0, max(max_val // 2, 0), max_val]
    names = ["top", "mid", "bottom"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[tuple[str, Path]] = []

    def run_step(idx: int = 0) -> None:
        if idx >= len(steps):
            content_h = screen._scroll_content.height()
            view_h = screen._scroll.viewport().height()
            print(
                f"scroll_max={max_val}px content={content_h} viewport={view_h}"
            )
            ok_scroll = max_val > 0
            print(f"scroll_enabled={ok_scroll}")
            for i, (name, path) in enumerate(results):
                _analyze_white_bands(path, name)
                _diff_scroll_vs_ref(path, steps[i], name)
            app.quit()
            return

        bar.setValue(steps[idx])
        app.processEvents()

        def grab() -> None:
            path = OUT_DIR / f"scroll_{names[idx]}.png"
            ok = screen.grab().save(str(path))
            results.append((names[idx], path))
            print(f"scroll={steps[idx]:4d} save={path.name} ok={ok}")
            QTimer.singleShot(200, lambda: run_step(idx + 1))

        QTimer.singleShot(150, grab)

    print("=== scroll verify ===")
    QTimer.singleShot(800, lambda: run_step(0))
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
