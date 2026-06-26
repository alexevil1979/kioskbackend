from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.core.config import Settings
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_chrome import chrome_top_pad
from src.ui.kolomna_tokens import CREAM, INK_60, KolomnaMetrics, scale
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.attract_cta import AttractCtaBlock
from src.ui.widgets.attract_tagline import AttractTagline
from src.ui.widgets.kolomna_api_status_dot import KolomnaApiStatusDot
from src.ui.widgets.kolomna_lang_toggle import KolomnaLangToggle
from src.ui.widgets.kolomna_logo import AttractLogo


class StartScreen(BaseScreen):
    """AttractScreen (classic) — 1:1 с offline-референсом."""

    tapped = pyqtSignal()

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__()
        app = settings.app if settings else None
        w = app.content_width if app else 499
        h = app.content_height if app else 913

        self.setObjectName("StartScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"QWidget#StartScreen {{ background: {CREAM}; }}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if app:
            self.setFixedSize(w, h)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._lang = KolomnaLangToggle(w, parent=self)
        self._lang.setCursor(Qt.CursorShape.ArrowCursor)

        self._api_dot = KolomnaApiStatusDot(w, parent=self)
        self._api_dot.setCursor(Qt.CursorShape.ArrowCursor)
        self._place_top_chrome()

        # attract__inner — вертикальный центр как flex center в референсе
        inner = QWidget()
        inner.setCursor(Qt.CursorShape.PointingHandCursor)
        inner_lay = QVBoxLayout(inner)
        inner_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        inner_lay.setSpacing(0)
        inner_lay.setContentsMargins(scale(90, w), 0, scale(90, w), 0)

        gap = scale(38, w)
        inner_lay.addWidget(AttractLogo(w), alignment=Qt.AlignmentFlag.AlignHCenter)
        inner_lay.addSpacing(gap)

        self._tagline = AttractTagline(S.ATTRACT_TAGLINE, w)
        inner_lay.addWidget(self._tagline, alignment=Qt.AlignmentFlag.AlignHCenter)
        inner_lay.addSpacing(gap)

        self._cta_block = AttractCtaBlock(S.ATTRACT_CTA, w)
        inner_lay.addWidget(self._cta_block, alignment=Qt.AlignmentFlag.AlignHCenter)
        inner_lay.addSpacing(gap)

        self._foot = QLabel(S.ATTRACT_FOOT)
        self._foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._foot.setWordWrap(True)
        self._foot.setFont(kolomna_font(scale(25, w), QFont.Weight.DemiBold))
        self._foot.setStyleSheet(f"color: {INK_60}; background: transparent;")
        inner_lay.addWidget(self._foot)

        self._layout.addStretch(1)
        self._layout.addWidget(inner, stretch=0)
        self._layout.addStretch(1)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._cta_block.start_animations()

    def hideEvent(self, event) -> None:  # noqa: N802
        self._cta_block.stop_animations()
        super().hideEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if hasattr(self, "_lang"):
            self._place_top_chrome()

    def _place_top_chrome(self) -> None:
        m = KolomnaMetrics.from_viewport(self.width(), self.height())
        top = chrome_top_pad(m)
        gap = scale(12, self.width())
        lang_x = self.width() - top - self._lang.width()
        self._lang.move(lang_x, top)
        self._api_dot.move(lang_x - gap - self._api_dot.width(), top + (self._lang.height() - self._api_dot.height()) // 2)
        self._lang.raise_()
        self._api_dot.raise_()

    def set_api_online(self, online: bool) -> None:
        self._api_dot.set_online(online)

    def _hits_lang_toggle(self, pos) -> bool:
        if not hasattr(self, "_lang"):
            return False
        return self._lang.geometry().contains(pos) or self._api_dot.geometry().contains(pos)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and not self._hits_lang_toggle(
            event.position().toPoint()
        ):
            self.tapped.emit()
        super().mouseReleaseEvent(event)

    def retranslate(self) -> None:
        from src.ui.kolomna_i18n import get_lang

        self._tagline.set_text(S.ATTRACT_TAGLINE)
        self._cta_block.set_text(S.ATTRACT_CTA)
        self._foot.setText(S.ATTRACT_FOOT)
        self._lang.set_lang(get_lang())
