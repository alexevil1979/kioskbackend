"""Строки UI киоска Kolomna — динамически по текущему языку (RU/EN)."""
from __future__ import annotations

from src.ui.kolomna_i18n import (
    get_lang,
    hub_label_for_slot,
    locale,
    locale_changed,
    n_items_label,
    set_lang,
    strings,
)

__all__ = [
    "get_lang",
    "set_lang",
    "locale",
    "locale_changed",
    "hub_label_for_slot",
    "n_items_label",
]


def __getattr__(name: str):
    bundle = strings()
    if name in bundle:
        return bundle[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
