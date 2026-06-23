from __future__ import annotations

from PyQt6.QtGui import QGuiApplication, QScreen

from src.core.config import AppConfig


def _screens_left_to_right(app: QGuiApplication) -> list[QScreen]:
    return sorted(app.screens(), key=lambda s: s.geometry().left())


def resolve_kiosk_screen(app: QGuiApplication, app_cfg: AppConfig) -> QScreen | None:
    """Экран для киоска: primary (по умолчанию), left, right или индекс слева направо."""
    screens = app.screens()
    if not screens:
        return app.primaryScreen()

    pos = (app_cfg.screen_position or "primary").strip().lower()
    ordered = _screens_left_to_right(app)

    if pos == "left":
        return ordered[0]
    if pos == "right":
        return ordered[-1]
    if pos == "primary":
        return app.primaryScreen() or ordered[0]

    if pos.isdigit():
        idx = int(pos)
        if 0 <= idx < len(ordered):
            return ordered[idx]

    if app_cfg.screen_index is not None:
        idx = app_cfg.screen_index
        if 0 <= idx < len(ordered):
            return ordered[idx]

    return app.primaryScreen() or ordered[0]
