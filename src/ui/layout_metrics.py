from __future__ import annotations

from dataclasses import dataclass

from src.core.config import AppConfig


@dataclass(frozen=True)
class LayoutMetrics:
    is_portrait: bool
    width: int
    height: int
    product_grid_columns: int
    category_bar_height: int
    bottom_bar_height: int
    product_image_height: int
    title_font_px: int

    @classmethod
    def from_app_config(cls, app: AppConfig) -> LayoutMetrics:
        portrait = app.orientation == "portrait" or app.screen_height > app.screen_width
        if portrait:
            return cls(
                is_portrait=True,
                width=app.screen_width,
                height=app.screen_height,
                product_grid_columns=2,
                category_bar_height=100,
                bottom_bar_height=168,
                product_image_height=220,
                title_font_px=42,
            )
        return cls(
            is_portrait=False,
            width=app.screen_width,
            height=app.screen_height,
            product_grid_columns=4,
            category_bar_height=72,
            bottom_bar_height=100,
            product_image_height=140,
            title_font_px=36,
        )
