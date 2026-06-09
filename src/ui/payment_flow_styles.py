"""Стили экранов оплаты — палитра «Сады Коломны»."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.ui.kolomna_tokens import CREAM, FONT, GREEN, INK_60, STRAWBERRY

PAYMENT_SCREEN_ID = "PaymentScreen"
PAYMENT_CONTENT_ID = "PaymentContentBlock"

CONTENT_BLOCK_WIDTH = 420

SCREEN_BG = CREAM

TITLE_STYLE = (
    f"font-family:{FONT};"
    "font-size:22px;font-weight:900;color:#1F4D2A;background:transparent;"
)

ERROR_TITLE_STYLE = (
    f"font-family:{FONT};"
    f"font-size:22px;font-weight:900;color:{STRAWBERRY};background:transparent;"
)

AMOUNT_STYLE = (
    f"font-family:{FONT};"
    "font-size:20px;font-weight:900;color:#1F4D2A;background:transparent;"
)

SUBTITLE_STYLE = (
    f"font-family:{FONT};"
    f"font-size:14px;font-weight:500;color:{INK_60};background:transparent;"
)

TIMER_STYLE = (
    f"font-family:{FONT};"
    "font-size:16px;font-weight:700;color:#1F4D2A;background:transparent;"
)

HINT_STYLE = SUBTITLE_STYLE

ICON_OK_STYLE = (
    f"font-family:{FONT};"
    "font-size:72px;font-weight:900;color:#1F4D2A;background:transparent;"
)

ICON_ERROR_STYLE = (
    f"font-family:{FONT};"
    f"font-size:56px;font-weight:900;color:{STRAWBERRY};background:transparent;"
)

QR_CARD_STYLE = (
    "QFrame#PaymentQrCard {"
    "background:#FFFFFF;border:none;border-radius:20px;"
    "}"
)

QR_PLACEHOLDER_STYLE = (
    f"font-family:{FONT};"
    f"font-size:14px;font-weight:700;color:{STRAWBERRY};background:transparent;"
)

PRIMARY_BTN_STYLE = (
    "QPushButton#PrimaryBtn{background:#1F4D2A;color:#F6EFD8;border:none;border-radius:999px;"
    f"font-family:{FONT};font-size:14px;font-weight:800;"
    "padding:0 20px;min-height:52px;}"
    "QPushButton#PrimaryBtn:pressed{background:#143821;}"
    "QPushButton#PrimaryBtn:disabled{background:#1F4D2A;color:#F6EFD8;opacity:0.45;}"
)

SECONDARY_BTN_STYLE = (
    "QPushButton#SecondaryBtn{background:#FFFFFF;color:#1F4D2A;border:2px solid #ECE0BC;"
    f"border-radius:999px;font-family:{FONT};"
    "font-size:14px;font-weight:700;padding:0 20px;min-height:48px;}"
    "QPushButton#SecondaryBtn:pressed{background:#ECE0BC;}"
)

OUTLINE_BTN_STYLE = SECONDARY_BTN_STYLE
CANCEL_BTN_STYLE = OUTLINE_BTN_STYLE


def apply_payment_screen(widget: QWidget) -> None:
    widget.setObjectName(PAYMENT_SCREEN_ID)
    widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    widget.setStyleSheet(f"QWidget#{PAYMENT_SCREEN_ID} {{ background:{SCREEN_BG}; }}")
    widget.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding,
    )


def layout_margins() -> tuple[int, int, int, int]:
    return (16, 12, 16, 16)


def mount_centered_content(outer: QVBoxLayout, inner: QVBoxLayout) -> QWidget:
    inner.setContentsMargins(0, 0, 0, 0)
    inner.setSpacing(12)
    inner.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    host = QWidget()
    host.setObjectName(PAYMENT_CONTENT_ID)
    host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    host.setStyleSheet("background:transparent;")
    host.setLayout(inner)
    host.setFixedWidth(CONTENT_BLOCK_WIDTH)
    host.setSizePolicy(
        QSizePolicy.Policy.Fixed,
        QSizePolicy.Policy.Preferred,
    )

    h_row = QHBoxLayout()
    h_row.setContentsMargins(0, 0, 0, 0)
    h_row.setSpacing(0)
    h_row.addStretch(1)
    h_row.addWidget(host)
    h_row.addStretch(1)

    outer.addStretch(1)
    outer.addLayout(h_row)
    outer.addStretch(1)
    return host


def add_payment_row(layout: QVBoxLayout, widget: QWidget) -> None:
    widget.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Fixed,
    )
    layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignHCenter)


def style_title(label: QLabel, *, error: bool = False) -> None:
    label.setObjectName("ScreenTitle" if not error else "PaymentErrorTitle")
    label.setStyleSheet(ERROR_TITLE_STYLE if error else TITLE_STYLE)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)


def style_subtitle(label: QLabel) -> None:
    label.setObjectName("Subtitle")
    label.setStyleSheet(SUBTITLE_STYLE)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)


def style_amount(label: QLabel) -> None:
    label.setObjectName("PaymentAmount")
    label.setStyleSheet(AMOUNT_STYLE)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)


def style_timer(label: QLabel) -> None:
    label.setObjectName("PaymentTimer")
    label.setStyleSheet(TIMER_STYLE)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)


def style_icon(label: QLabel, *, ok: bool = False) -> None:
    label.setStyleSheet(ICON_OK_STYLE if ok else ICON_ERROR_STYLE)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)


def make_qr_card() -> QFrame:
    card = QFrame()
    card.setObjectName("PaymentQrCard")
    card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    card.setStyleSheet(QR_CARD_STYLE)
    return card


def style_primary_button(btn: QPushButton) -> None:
    btn.setMinimumHeight(52)
    btn.setStyleSheet(PRIMARY_BTN_STYLE)


def style_secondary_button(btn: QPushButton) -> None:
    btn.setMinimumHeight(48)
    btn.setStyleSheet(SECONDARY_BTN_STYLE)


def style_outline_button(btn: QPushButton) -> None:
    btn.setMinimumHeight(48)
    btn.setStyleSheet(OUTLINE_BTN_STYLE)


def style_cancel_button(btn: QPushButton) -> None:
    btn.setObjectName("OutlineBtn")
    btn.setMinimumHeight(48)
    btn.setStyleSheet(CANCEL_BTN_STYLE)
