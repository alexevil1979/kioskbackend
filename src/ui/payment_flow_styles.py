"""Стили экранов оплаты — в одном ключе с корзиной и каталогом Катюша."""

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

PAYMENT_SCREEN_ID = "PaymentScreen"
PAYMENT_CONTENT_ID = "PaymentContentBlock"

# Ширина центрального блока (viewport dev 499 − поля)
CONTENT_BLOCK_WIDTH = 420

SCREEN_BG = "#F4F4F5"

TITLE_STYLE = (
    "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;"
    "font-size:22px;font-weight:700;color:#111827;background:transparent;"
)

ERROR_TITLE_STYLE = (
    "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;"
    "font-size:22px;font-weight:700;color:#DC2626;background:transparent;"
)

AMOUNT_STYLE = (
    "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;"
    "font-size:20px;font-weight:700;color:#1F6D4A;background:transparent;"
)

SUBTITLE_STYLE = (
    "font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
    "font-size:14px;font-weight:400;color:#6B7280;background:transparent;"
)

TIMER_STYLE = (
    "font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
    "font-size:16px;font-weight:600;color:#1F6D4A;background:transparent;"
)

HINT_STYLE = SUBTITLE_STYLE

ICON_OK_STYLE = (
    "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;"
    "font-size:72px;font-weight:700;color:#35C46A;background:transparent;"
)

ICON_ERROR_STYLE = (
    "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;"
    "font-size:56px;font-weight:700;color:#DC2626;background:transparent;"
)

QR_CARD_STYLE = (
    "QFrame#PaymentQrCard {"
    "background:#FFFFFF;border:1px solid #E5E7EB;border-radius:20px;"
    "}"
)

QR_PLACEHOLDER_STYLE = (
    "font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
    "font-size:14px;font-weight:600;color:#DC2626;background:transparent;"
)

PRIMARY_BTN_STYLE = (
    "QPushButton#PrimaryBtn{background:#35C46A;color:#051B0D;border:none;border-radius:14px;"
    "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;font-size:12px;font-weight:700;"
    "text-transform:uppercase;padding:0 20px;min-height:52px;}"
    "QPushButton#PrimaryBtn:pressed{background:#2FB05E;}"
    "QPushButton#PrimaryBtn:disabled{background:#35C46A;color:#051B0D;opacity:0.45;}"
)

SECONDARY_BTN_STYLE = (
    "QPushButton#SecondaryBtn{background:#FFFFFF;color:#111827;border:1px solid #D8DEE6;"
    "border-radius:14px;font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
    "font-size:14px;font-weight:600;padding:0 20px;min-height:48px;}"
    "QPushButton#SecondaryBtn:pressed{background:#F4F4F5;}"
)

OUTLINE_BTN_STYLE = (
    "QPushButton#OutlineBtn{background:#FFFFFF;color:#111827;border:1px solid #D8DEE6;"
    "border-radius:14px;font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
    "font-size:14px;font-weight:600;padding:0 20px;min-height:48px;}"
    "QPushButton#OutlineBtn:pressed{background:#F4F4F5;}"
)

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
    """Блок по центру экрана (вертикаль и горизонталь)."""
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
    """Строка на всю ширину центрального блока."""
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
    """Отмена — outline, не оранжевый DangerBtn."""
    btn.setObjectName("OutlineBtn")
    btn.setMinimumHeight(48)
    btn.setStyleSheet(CANCEL_BTN_STYLE)
