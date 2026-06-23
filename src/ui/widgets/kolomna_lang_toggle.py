from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_chrome import chrome_row_height
from src.ui.kolomna_shadow import draw_shadow_soft_pill, shadow_soft_bleed
from src.ui.kolomna_tokens import CREAM, GREEN, INK_60, scale


class _LangPillBtn(QPushButton):
    """lang-toggle__btn: pill 78×64, font-weight 800."""

    def __init__(self, label: str, width: int, height: int, font_px: int, parent=None) -> None:
        super().__init__(label, parent)
        self.setFixedSize(width, height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._font_px = font_px
        self._font = kolomna_font(font_px, QFont.Weight.ExtraBold)
        self.setFont(self._font)
        self._radius = height // 2
        self._active = False
        self._apply()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply()

    def _apply(self) -> None:
        self.setFont(self._font)
        base = (
            f"border: none; border-radius: {self._radius}px; "
            f"font-size: {self._font_px}px; font-weight: 800;"
        )
        if self._active:
            self.setStyleSheet(
                f"QPushButton {{ background: {GREEN}; color: {CREAM}; {base} }}"
            )
        else:
            self.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {INK_60}; {base} }}"
            )


class _LangTogglePill(QWidget):
    """Белая pill-капсула lang-toggle."""

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = rect.height() / 2.0
        draw_shadow_soft_pill(painter, rect, r, max(1, self.width()))
        path = QPainterPath()
        path.addRoundedRect(rect, r, r)
        painter.fillPath(path, QColor("#FFFFFF"))
        painter.end()


class KolomnaLangToggle(QWidget):
    """lang-toggle: два pill 78×64, активный — зелёный овал."""

    lang_changed = pyqtSignal(str)

    def __init__(self, viewport_width: int, *, lang: str = "ru", parent=None) -> None:
        super().__init__(parent)
        self._lang = lang
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        btn_w = scale(78, viewport_width)
        btn_h = scale(64, viewport_width)
        pad = scale(6, viewport_width)
        fs = scale(22, viewport_width)

        pill_w = pad * 2 + btn_w * 2
        pill_h = pad * 2 + btn_h

        bleed_l, bleed_t, bleed_r, bleed_b = shadow_soft_bleed(viewport_width)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(bleed_l, bleed_t, bleed_r, bleed_b)
        outer.setSpacing(0)

        self._pill = _LangTogglePill()
        self._pill.setFixedSize(pill_w, pill_h)

        self._ru = _LangPillBtn("RU", btn_w, btn_h, fs, self._pill)
        self._ru.move(pad, pad)
        self._ru.clicked.connect(lambda: self._set_lang("ru"))

        self._en = _LangPillBtn("EN", btn_w, btn_h, fs, self._pill)
        self._en.move(pad + btn_w, pad)
        self._en.clicked.connect(lambda: self._set_lang("en"))

        outer.addWidget(self._pill)
        self.setFixedSize(pill_w + bleed_l + bleed_r, chrome_row_height(viewport_width))
        self._sync()

    def _set_lang(self, lang: str) -> None:
        self._lang = lang
        self._sync()
        self.lang_changed.emit(lang)

    def set_lang(self, lang: str) -> None:
        lang = "en" if lang == "en" else "ru"
        if lang == self._lang:
            return
        self._lang = lang
        self._sync()

    def _sync(self) -> None:
        self._ru.set_active(self._lang == "ru")
        self._en.set_active(self._lang == "en")
