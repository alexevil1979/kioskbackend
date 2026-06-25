from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QPushButton, QVBoxLayout, QWidget

from src.core.config import Settings
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_cta import cta_palette
from src.ui.kolomna_tokens import CREAM, GREEN, INK_60, KolomnaMetrics, scale
from src.ui.screens.base_screen import BaseScreen


class KolomnaDoneScreen(BaseScreen):
    new_order = pyqtSignal()

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)

        self.setObjectName("KolomnaDoneScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner = QWidget()
        inner.setMaximumWidth(scale(860, w))
        lay = QVBoxLayout(inner)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(scale(24, w))

        self._check = QLabel("✓")
        self._check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._check.setFixedSize(scale(230, w), scale(230, w))
        self._check.setFont(kolomna_font(scale(140, w), QFont.Weight.Black))
        check_shadow = QGraphicsDropShadowEffect(self._check)
        check_shadow.setBlurRadius(scale(60, w))
        check_shadow.setOffset(0, scale(24, w))
        check_shadow.setColor(QColor(20, 56, 33, 102))
        self._check.setGraphicsEffect(check_shadow)

        self._title = QLabel(S.DONE_TITLE)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setFont(kolomna_font(self._m.fs_display, QFont.Weight.Black))
        self._title.setStyleSheet(
            f"color: {GREEN}; background: transparent; margin-top: {scale(6, w)}px;"
        )

        self._thanks = QLabel(S.DONE_THANKS)
        self._thanks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thanks.setFont(kolomna_font(self._m.fs_h3, QFont.Weight.Bold))
        self._thanks.setStyleSheet(f"color: {INK_60}; background: transparent;")

        order_box = QWidget()
        order_box.setStyleSheet(
            f"QWidget {{ background: {GREEN}; border-radius: {self._m.radius_lg}px; }}"
        )
        order_lay = QVBoxLayout(order_box)
        order_lay.setContentsMargins(scale(76, w), scale(34, w), scale(76, w), scale(34, w))
        order_lay.setSpacing(scale(8, w))
        self._order_lbl = QLabel(S.ORDER_NO)
        self._order_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._order_lbl.setFont(kolomna_font(scale(30, w), QFont.Weight.Bold))
        self._order_lbl.setStyleSheet(
            f"color: {CREAM}; background: transparent; opacity: 0.8; "
            f"letter-spacing: {scale(3, w)}px;"
        )
        self._order_no = QLabel()
        self._order_no.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._order_no.setFont(kolomna_font(scale(120, w), QFont.Weight.Black))
        self._order_no.setStyleSheet(f"color: {CREAM}; background: transparent;")
        order_lay.addWidget(self._order_lbl)
        order_lay.addWidget(self._order_no)

        self._collect = QLabel(S.COLLECT)
        self._collect.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._collect.setWordWrap(True)
        self._collect.setFont(kolomna_font(self._m.fs_h3, QFont.Weight.ExtraBold))
        self._collect.setStyleSheet(f"color: {GREEN}; background: transparent;")

        self._collect_sub = QLabel(S.COLLECT_SUB)
        self._collect_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._collect_sub.setWordWrap(True)
        self._collect_sub.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Medium))
        self._collect_sub.setStyleSheet(f"color: {INK_60}; background: transparent;")

        self._new_order_btn = QPushButton(S.NEW_ORDER)
        self._new_order_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._new_order_btn.setMinimumHeight(self._m.footbar_btn_h)
        self._new_order_btn.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Black))
        self._new_order_btn.clicked.connect(self.new_order.emit)
        self.refresh_cta()

        self._auto = QLabel()
        self._auto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._auto.setFont(kolomna_font(self._m.fs_label, QFont.Weight.Bold))
        self._auto.setStyleSheet(f"color: {INK_60}; background: transparent;")

        lay.addWidget(self._check, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._thanks, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(scale(16, w))
        lay.addWidget(order_box, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(scale(16, w))
        lay.addWidget(self._collect, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._collect_sub, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self._new_order_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(scale(16, w))
        lay.addWidget(self._auto, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._layout.addWidget(inner)

    def set_order_no(self, order_no: str) -> None:
        text = (order_no or "").strip() or "—"
        self._order_no.setText(f"№\u00a0{text}")

    def set_countdown_text(self, text: str) -> None:
        self._auto.setText(text)

    def refresh_cta(self) -> None:
        w = self._m.width
        pal = cta_palette()
        self._check.setStyleSheet(
            f"QLabel {{ background: {pal.bg}; color: {pal.fg}; border-radius: {scale(115, w)}px; }}"
        )
        self._new_order_btn.setStyleSheet(
            f"QPushButton {{ background: {pal.bg}; color: {pal.fg}; border: none; "
            f"border-radius: 999px; padding: 0 {scale(48, w)}px; }}"
        )

    def retranslate(self) -> None:
        self._title.setText(S.DONE_TITLE)
        self._thanks.setText(S.DONE_THANKS)
        self._order_lbl.setText(S.ORDER_NO)
        self._collect.setText(S.COLLECT)
        self._collect_sub.setText(S.COLLECT_SUB)
        self._new_order_btn.setText(S.NEW_ORDER)
