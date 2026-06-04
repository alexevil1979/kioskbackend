from __future__ import annotations

from dataclasses import dataclass

from src.core.config import AppConfig


@dataclass(frozen=True)
class LayoutMetrics:
    is_portrait: bool
    phone_layout: bool
    width: int
    height: int
    product_grid_columns: int
    page_padding: int
    grid_gap: int
    header_height: int
    categories_strip_height: int
    bottom_bar_height: int
    product_image_size: int
    title_font_px: int

    @classmethod
    def from_app_config(cls, app: AppConfig) -> LayoutMetrics:
        if app.phone_layout:
            return cls._phone(app)
        portrait = app.orientation == "portrait" or app.screen_height > app.screen_width
        if portrait:
            return cls._kiosk_portrait(app)
        return cls._landscape(app)

    @classmethod
    def _phone(cls, app: AppConfig) -> LayoutMetrics:
        w = app.content_width
        h = app.content_height
        pad = 16
        gap = 12
        cols = 2
        card_w = (w - pad * 2 - gap) // cols
        return cls(
            is_portrait=True,
            phone_layout=True,
            width=w,
            height=h,
            product_grid_columns=cols,
            page_padding=pad,
            grid_gap=gap,
            header_height=110,
            categories_strip_height=52,
            bottom_bar_height=72,
            product_image_size=card_w,
            title_font_px=28,
        )

    @classmethod
    def _kiosk_portrait(cls, app: AppConfig) -> LayoutMetrics:
        pad = 24
        gap = 16
        cols = 2
        w = app.content_width
        inner_w = w - pad * 2
        card_w = (inner_w - gap) // cols
        return cls(
            is_portrait=True,
            phone_layout=False,
            width=w,
            height=app.content_height,
            product_grid_columns=cols,
            page_padding=pad,
            grid_gap=gap,
            header_height=140,
            categories_strip_height=72,
            bottom_bar_height=100,
            product_image_size=card_w,
            title_font_px=42,
        )

    @classmethod
    def _landscape(cls, app: AppConfig) -> LayoutMetrics:
        pad = 24
        gap = 20
        cols = 4
        w = app.content_width
        inner_w = w - pad * 2
        card_w = (inner_w - gap * (cols - 1)) // cols
        return cls(
            is_portrait=False,
            phone_layout=False,
            width=w,
            height=app.content_height,
            product_grid_columns=cols,
            page_padding=pad,
            grid_gap=gap,
            header_height=120,
            categories_strip_height=64,
            bottom_bar_height=88,
            product_image_size=min(card_w, 220),
            title_font_px=36,
        )
