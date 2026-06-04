"""Токены экрана «КАТЕГОРИИ» — референс screen_katusha.png (499×913)."""
from __future__ import annotations

VIEWPORT_W = 499
VIEWPORT_H = 913

# Измерено по screen_katusha.png (карточки x=16…)
PAGE_PAD = 16
CARD_GAP = 12
HERO_W = 466
CARD_W = 227

# Шапка
LOGO_SIZE = 40
LOGO_RADIUS = 12
WORDMARK_SIZE = 18
TAGLINE_SIZE = 11
TAGLINE_LINE_HEIGHT = 16
SEARCH_HEIGHT = 52
SEARCH_RADIUS = 26
HEADER_TOP_RADIUS = 16
HEADER_TOP_BG = "#F3F4F6"
HEADER_PAD_TOP = 14
HEADER_ROW_GAP = 10
TAGLINE_TOP = 4
SEARCH_TOP = 10

TOGGLE_HEIGHT = 30
TOGGLE_BTN_HEIGHT = 26
TOGGLE_RADIUS = 15
TOGGLE_BTN_RADIUS = 13
TOGGLE_FONT = 9
TOGGLE_PAD_H = 11

SECTION_TITLE_SIZE = 15
LINK_ALL_SIZE = 11

CARD_RADIUS = 28
HERO_HEIGHT = 243
CARD_HEIGHT = 243
CARD_PAD = 12
GRADIENT_BOTTOM = 0.48

NAV_HEIGHT = 79
NAV_ICON = 22
NAV_LABEL_SIZE = 8

Y_HEADER = 182
Y_TITLE = 163
Y_HUB_END = 834
HUB_SCROLL_H = Y_HUB_END - Y_HEADER
HUB_SCROLL_VIEWPORT_H = 534
HUB_SCROLL_EXTRA = HUB_SCROLL_H - HUB_SCROLL_VIEWPORT_H
HUB_CONTENT_H = HUB_SCROLL_H + HUB_SCROLL_EXTRA

# Координаты карточек внутри categories_scroll (y относительно y=182)
Y_HERO_SCROLL = 29
Y_ROW1_SCROLL = 300
Y_ROW2_SCROLL = 568

# Слоты 1:1 с референсом (x, y, w, h)
SLOT_HERO = (PAGE_PAD, Y_HERO_SCROLL, HERO_W, HERO_HEIGHT)
SLOTS_HALF = (
    (PAGE_PAD, Y_ROW1_SCROLL, CARD_W, CARD_HEIGHT),
    (PAGE_PAD + CARD_W + CARD_GAP, Y_ROW1_SCROLL, CARD_W, CARD_HEIGHT),
    (PAGE_PAD, Y_ROW2_SCROLL, CARD_W, CARD_HEIGHT),
    (PAGE_PAD + CARD_W + CARD_GAP, Y_ROW2_SCROLL, CARD_W, CARD_HEIGHT),
)


def hub_content_height(num_summaries: int) -> int:
    """Высота контента скролла — до нижнего края последней карточки."""
    if num_summaries <= 0:
        return HUB_SCROLL_H
    rest = max(0, num_summaries - 1)
    if rest <= 0:
        return Y_HERO_SCROLL + HERO_HEIGHT + PAGE_PAD
    if rest <= 2:
        return Y_ROW1_SCROLL + CARD_HEIGHT + PAGE_PAD
    return Y_ROW2_SCROLL + CARD_HEIGHT + PAGE_PAD
