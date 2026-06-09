"""Дизайн-токены «Сады Коломны» (референс 1080×1920, масштаб под viewport)."""

from __future__ import annotations

from dataclasses import dataclass

# Палитра (design-system.css)
CREAM = "#F6EFD8"
CREAM_DEEP = "#ECE0BC"
GREEN = "#1F4D2A"
GREEN_DEEP = "#143821"
STRAWBERRY = "#D9143A"
STRAWBERRY_EDGE = "#143821"
RASPBERRY = "#A8123E"
RASPBERRY_EDGE = "#143821"
BLUEBERRY = "#3F5E96"
BLUEBERRY_EDGE = "#22324F"
YELLOW = "#F4C90A"
INK_60 = "rgba(31,77,42,0.65)"
INK_30 = "rgba(31,77,42,0.22)"

FONT = "'Montserrat', ui-sans-serif, system-ui, sans-serif"

KIOSK_W = 1080

BERRY_ACCENTS: list[tuple[str, str]] = [
    (STRAWBERRY, STRAWBERRY_EDGE),
    (BLUEBERRY, BLUEBERRY_EDGE),
    (RASPBERRY, RASPBERRY_EDGE),
    (GREEN, GREEN_DEEP),
]


def scale(px: int, width: int) -> int:
    return max(1, round(px * width / KIOSK_W))


@dataclass(frozen=True)
class KolomnaMetrics:
    width: int
    height: int
    pad: int
    gap: int
    tap_min: int
    radius: int
    radius_lg: int
    fs_display: int
    fs_h1: int
    fs_h2: int
    fs_h3: int
    fs_body: int
    fs_label: int
    fs_lead: int
    footbar_btn_h: int

    @classmethod
    def from_viewport(cls, width: int, height: int) -> KolomnaMetrics:
        return cls(
            width=width,
            height=height,
            pad=scale(56, width),
            gap=scale(24, width),
            tap_min=scale(72, width),
            radius=scale(24, width),
            radius_lg=scale(32, width),
            fs_display=scale(120, width),
            fs_h1=scale(72, width),
            fs_h2=scale(52, width),
            fs_h3=scale(38, width),
            fs_body=scale(26, width),
            fs_label=scale(20, width),
            fs_lead=scale(30, width),
            footbar_btn_h=scale(70, width),
        )

    def accent_for_index(self, index: int) -> tuple[str, str]:
        return BERRY_ACCENTS[index % len(BERRY_ACCENTS)]
