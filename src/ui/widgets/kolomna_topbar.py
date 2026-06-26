from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_chrome import chrome_pill_height, chrome_row_height, chrome_top_pad
from src.ui.kolomna_shadow import draw_shadow_soft_pill, shadow_soft_bleed
from src.ui.kolomna_tokens import CREAM, GREEN, KolomnaMetrics, YELLOW, scale
from src.ui.widgets.kolomna_api_status_dot import KolomnaApiStatusDot
from src.ui.widgets.kolomna_lang_toggle import KolomnaLangToggle

# Смещение ‹ относительно baseline «Назад» (px при ширине 1080; + вниз, − вверх).
BACK_CHEVRON_Y_OFFSET = 5


class _BackRowContent(QWidget):
    """topbar__back: ‹ + «Назад» на одной базовой линии (как align-items: center в ref)."""

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._text = S.BACK
        self._gap = scale(8, metrics.width)
        self._body_font = kolomna_font(metrics.fs_body, QFont.Weight.ExtraBold)
        self._icon_font = kolomna_font(scale(52, metrics.width), QFont.Weight.ExtraBold)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._sync_size()

    def _sync_size(self) -> None:
        fm_b = QFontMetrics(self._body_font)
        fm_i = QFontMetrics(self._icon_font)
        w = fm_i.horizontalAdvance("‹") + self._gap + fm_b.horizontalAdvance(self._text)
        self.setFixedSize(max(scale(28, self._m.width), w), fm_b.height())

    def set_text(self, text: str) -> None:
        self._text = text
        self._sync_size()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        fm_b = QFontMetrics(self._body_font)
        baseline = (self.height() + fm_b.ascent() - fm_b.descent()) // 2
        chevron_y = baseline + scale(BACK_CHEVRON_Y_OFFSET, self._m.width)
        p.setPen(QColor(GREEN))
        p.setFont(self._icon_font)
        p.drawText(0, int(chevron_y), "‹")
        p.setFont(self._body_font)
        p.drawText(QFontMetrics(self._icon_font).horizontalAdvance("‹") + self._gap, baseline, self._text)
        p.end()


class _CartPillButton(QWidget):
    """cart-pill: align-items: center — жёлтый круг + сумма на одной оси."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._pressed = False
        self._count_val = 0
        self._sum_text = ""
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        w = metrics.width
        self._pad_l = scale(12, w)
        self._pad_r = scale(24, w)
        self._gap = scale(16, w)
        self._count_sz = scale(50, w)
        self._btn_h = max(metrics.tap_min, self._count_sz + scale(24, w))
        self._radius = self._btn_h // 2
        self._count_font = kolomna_font(scale(26, w), QFont.Weight.Black)
        self._sum_font = kolomna_font(metrics.fs_h3, QFont.Weight.Black)
        self.setFixedHeight(self._btn_h)

    @staticmethod
    def _vcenter_baseline(fm: QFontMetrics, top: float, height: float) -> float:
        cy = top + height / 2.0
        return cy + (fm.ascent() - fm.descent()) / 2.0

    def set_cart(self, count: int, total: str) -> None:
        self._count_val = count
        self._sum_text = total
        fm = QFontMetrics(self._sum_font)
        inner_w = self._count_sz + self._gap + fm.horizontalAdvance(total)
        self.setFixedSize(inner_w + self._pad_l + self._pad_r, self._btn_h)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect())
        r = float(self._radius)
        bg = QColor("#143821" if self._pressed else GREEN)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, r, r)

        cy = self.height() / 2.0
        cr = self._count_sz / 2.0
        cx_c = self._pad_l + cr
        p.setBrush(QColor(YELLOW))
        p.drawEllipse(QRectF(cx_c - cr, cy - cr, self._count_sz, self._count_sz))

        count_str = str(self._count_val)
        fm_c = QFontMetrics(self._count_font)
        p.setFont(self._count_font)
        p.setPen(QColor(GREEN))
        bc = self._vcenter_baseline(fm_c, cy - cr, self._count_sz)
        p.drawText(int(cx_c - fm_c.horizontalAdvance(count_str) / 2), int(bc), count_str)

        fm_s = QFontMetrics(self._sum_font)
        p.setFont(self._sum_font)
        p.setPen(QColor(CREAM))
        bs = self._vcenter_baseline(fm_s, 0, self.height())
        x_sum = self._pad_l + self._count_sz + self._gap
        p.drawText(int(x_sum), int(bs), self._sum_text)
        p.end()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class _BackPill(QWidget):
    """Белый pill topbar__back (фон)."""

    def __init__(self, radius: int, parent=None) -> None:
        super().__init__(parent)
        self._radius = radius
        self._pressed = False

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = float(self._radius)
        draw_shadow_soft_pill(p, rect, r, max(1, self.width()))
        bg = QColor(CREAM if self._pressed else "#FFFFFF")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, self._radius, self._radius)
        p.end()


class _TopBarBackButton(QWidget):
    """topbar__back — pill + box-shadow: var(--shadow-soft)."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        w = metrics.width
        pad_l = scale(20, w)
        pad_r = scale(30, w)

        self._content = _BackRowContent(metrics)
        pill_w = pad_l + self._content.width() + pad_r
        pill_h = chrome_pill_height(w)
        radius = pill_h // 2

        bleed_l, bleed_t, bleed_r, bleed_b = shadow_soft_bleed(w)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(bleed_l, bleed_t, bleed_r, bleed_b)
        outer.setSpacing(0)

        self._pill = _BackPill(radius)
        self._pill.setFixedSize(pill_w, pill_h)

        lay = QHBoxLayout(self._pill)
        lay.setContentsMargins(pad_l, 0, pad_r, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(self._content, alignment=Qt.AlignmentFlag.AlignVCenter)

        outer.addWidget(self._pill)
        self.setFixedSize(pill_w + bleed_l + bleed_r, chrome_row_height(w))
        self._metrics = metrics

    def retranslate(self) -> None:
        self._content.set_text(S.BACK)
        w = self._metrics.width
        pad_l = scale(20, w)
        pad_r = scale(30, w)
        pill_w = pad_l + self._content.width() + pad_r
        pill_h = chrome_pill_height(w)
        self._pill.setFixedSize(pill_w, pill_h)
        bleed_l, bleed_t, bleed_r, bleed_b = shadow_soft_bleed(w)
        self.setFixedSize(pill_w + bleed_l + bleed_r, chrome_row_height(w))

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._pill.geometry().contains(
            event.position().toPoint()
        ):
            self._pill._pressed = True
            self._pill.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pill._pressed = False
            self._pill.update()
            if self._pill.geometry().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)


class KolomnaTopBar(QWidget):
    """topbar: «Назад» + lang-toggle; строка заголовка + cart-pill."""

    back_clicked = pyqtSignal()
    cart_clicked = pyqtSignal()
    lang_changed = pyqtSignal(str)

    def __init__(
        self,
        metrics: KolomnaMetrics,
        *,
        show_back: bool = False,
        show_lang: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._m = metrics

        root = QVBoxLayout(self)
        root.setContentsMargins(
            chrome_top_pad(metrics), chrome_top_pad(metrics), metrics.pad, scale(8, metrics.width)
        )
        root.setSpacing(scale(30, metrics.width))

        chrome_row = QWidget()
        chrome_row.setFixedHeight(chrome_row_height(metrics.width))
        row = QHBoxLayout(chrome_row)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(scale(24, metrics.width))

        self._back = _TopBarBackButton(metrics)
        self._back.clicked.connect(self.back_clicked.emit)
        self._back.setVisible(show_back)
        row.addWidget(self._back, alignment=Qt.AlignmentFlag.AlignVCenter)

        row.addStretch(1)

        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(scale(8, metrics.width))
        self._api_dot = KolomnaApiStatusDot(metrics.width)
        right_lay.addWidget(
            self._api_dot,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
        )

        self._lang: KolomnaLangToggle | None = None
        if show_lang:
            self._lang = KolomnaLangToggle(metrics.width)
            self._lang.lang_changed.connect(self.lang_changed.emit)
            right_lay.addWidget(
                self._lang,
                alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
            )

        row.addWidget(right, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        root.addWidget(chrome_row)

        title_row = QHBoxLayout()
        title_row.setSpacing(scale(22, metrics.width))

        self._dot = QLabel()
        self._dot.setFixedSize(scale(26, metrics.width), scale(26, metrics.width))
        self._dot.hide()
        self._title = QLabel()
        self._title.hide()
        title_row.addWidget(self._dot, alignment=Qt.AlignmentFlag.AlignVCenter)
        title_row.addWidget(self._title, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._cart_pill = _CartPillButton(metrics)
        self._cart_pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cart_pill.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._cart_pill.hide()
        self._cart_pill.clicked.connect(self.cart_clicked.emit)
        title_row.addWidget(self._cart_pill, alignment=Qt.AlignmentFlag.AlignVCenter)

        root.addLayout(title_row)

    def set_show_back(self, visible: bool) -> None:
        self._back.setVisible(visible)

    def set_title(self, text: str, *, accent: str | None = None) -> None:
        if text:
            self._title.setText(text)
            self._title.setFont(kolomna_font(self._m.fs_h1, QFont.Weight.Black))
            self._title.setStyleSheet(f"color: {GREEN}; background: transparent;")
            self._title.show()
            if accent:
                r = scale(26, self._m.width)
                self._dot.setStyleSheet(
                    f"QLabel {{ background: {accent}; border-radius: {r // 2}px; }}"
                )
                self._dot.show()
            else:
                self._dot.hide()
        else:
            self._title.hide()
            self._dot.hide()

    def update_cart(self, count: int, total: str) -> None:
        if count > 0:
            self._cart_pill.set_cart(count, total)
            self._cart_pill.show()
        else:
            self._cart_pill.hide()

    def set_lang(self, lang: str) -> None:
        if self._lang is not None:
            self._lang.set_lang(lang)

    def set_api_online(self, online: bool) -> None:
        self._api_dot.set_online(online)

    def retranslate(self) -> None:
        self._back.retranslate()
        if self._lang is not None:
            from src.ui.kolomna_i18n import get_lang

            self._lang.set_lang(get_lang())
