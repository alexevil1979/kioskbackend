from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.ui.image_utils import load_pixmap, scale_pixmap
from src.ui import kolomna_strings as S
from src.ui.kolomna_catalog import KolomnaHubTile
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, YELLOW, KolomnaMetrics, scale


class _PromoHead(QWidget):
    """cat-card__promo-h: две строки, line-height .92, letter-spacing -.04em."""

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._line1 = S.HUB_PROMO_LINE1
        self._line2 = S.HUB_PROMO_LINE2
        self._fs = scale(92, metrics.width)
        self._line_h = self._fs * 0.92
        font = kolomna_font(self._fs, QFont.Weight.Black)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, -0.04 * self._fs)
        fm = QFontMetrics(font)
        lh = max(1, int(round(self._line_h)))
        # ascent + межстрочный интервал + descender второй строки (ё, й)
        total = fm.ascent() + lh + fm.descent() + scale(2, metrics.width)
        self.setFixedHeight(max(1, total))

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(0, self.height())

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        font = kolomna_font(self._fs, QFont.Weight.Black)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, -0.04 * self._fs)
        painter.setFont(font)
        lh = max(1, int(round(self._line_h)))
        fm = QFontMetrics(font)
        y = fm.ascent()
        painter.setPen(QColor(CREAM))
        painter.drawText(0, y, self._line1)
        painter.setPen(QColor(YELLOW))
        painter.drawText(0, y + lh, self._line2)
        painter.end()

    def set_lines(self, line1: str, line2: str) -> None:
        self._line1 = line1
        self._line2 = line2
        self.update()


class _FullbleedCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, tile: KolomnaHubTile, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._tile = tile
        self._m = metrics
        self._accent = tile.accent
        self._pad = scale(44, metrics.width)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._pix_source: QPixmap | None = None
        self._scaled_pix: QPixmap | None = None
        self._art_pos = QPoint()
        self._pix_scale_key = (0, 0)
        if tile.image_path and not tile.is_service:
            pix = load_pixmap(tile.image_path)
            if not pix.isNull():
                self._pix_source = pix

        self._text = QWidget(self)
        self._text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._text.setStyleSheet("background: transparent;")
        text_lay = QVBoxLayout(self._text)
        text_lay.setContentsMargins(0, 0, 0, 0)
        text_lay.setSpacing(scale(4, metrics.width))

        fs_num = scale(28, metrics.width)
        self._num = QLabel(tile.num)
        self._num.setFont(kolomna_font(fs_num, QFont.Weight.Black))
        self._num.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.55); background: transparent; "
            f"letter-spacing: {fs_num * 0.06:.1f}px; }}"
        )

        fs_name = scale(72, metrics.width)
        self._name = QLabel(tile.label)
        self._name.setWordWrap(len(tile.label) > 12)
        self._name.setFont(kolomna_font(fs_name, QFont.Weight.Black))
        self._name.setStyleSheet(
            "QLabel { color: #FFFFFF; background: transparent; line-height: 98%; "
            f"letter-spacing: {-0.03 * fs_name:.2f}px; }}"
        )

        text_lay.addWidget(self._num)
        text_lay.addWidget(self._name)

        self._promo: QWidget | None = None
        self._ref_source = QPixmap()
        self._ref_scaled: QPixmap | None = None
        if tile.is_service:
            self._promo = QWidget(self)
            self._promo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self._promo.setStyleSheet("background: transparent;")
            promo_lay = QVBoxLayout(self._promo)
            promo_lay.setContentsMargins(0, 0, 0, 0)
            promo_lay.setSpacing(scale(28, metrics.width))
            sub = QLabel(S.HUB_PROMO_SUB)
            sub.setWordWrap(True)
            sub.setFont(kolomna_font(metrics.fs_body, QFont.Weight.DemiBold))
            sub.setStyleSheet("QLabel { color: rgba(246,239,216,0.82); background: transparent; }")
            promo_head = _PromoHead(metrics)
            promo_lay.addWidget(promo_head)
            promo_lay.addWidget(sub)
            self._promo_head = promo_head
            self._promo_sub = sub

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.fillRect(self.rect(), QColor(self._accent))
        if self._scaled_pix is not None and not self._scaled_pix.isNull():
            p.drawPixmap(self._art_pos, self._scaled_pix)
        if self._ref_scaled is not None and not self._ref_scaled.isNull():
            p.drawPixmap(0, 0, self._ref_scaled)
        p.end()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._layout_children()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._layout_children()

    def _layout_children(self) -> None:
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        pad = self._pad
        if self._pix_source and not self._pix_source.isNull():
            aw = int(w * 1.65)
            ah = int(h * 1.58)
            key = (aw, ah)
            if key != self._pix_scale_key:
                self._scaled_pix = scale_pixmap(self._pix_source, aw, ah)
                self._pix_scale_key = key
            if self._scaled_pix is not None and not self._scaled_pix.isNull():
                pw, ph = self._scaled_pix.width(), self._scaled_pix.height()
                self._art_pos = QPoint((w - pw) // 2, (h - ph) // 2)
            else:
                self._scaled_pix = None
        else:
            self._scaled_pix = None
            self._pix_scale_key = (0, 0)

        fm_n = QFontMetrics(self._num.font())
        fm_t = QFontMetrics(self._name.font())
        th = fm_n.height() + scale(4, self._m.width) + fm_t.height()
        self._text.setGeometry(pad, h - pad - th, w - pad * 2, th)
        self._text.raise_()

        if self._promo is not None:
            promo_pad = scale(36, self._m.width)
            promo_w = w - promo_pad * 2
            for child in self._promo.findChildren(QLabel):
                if child.wordWrap():
                    child.setMaximumWidth(int(promo_w * 0.92))
            self._promo.adjustSize()
            ph = self._promo.sizeHint().height()
            self._promo.setGeometry(promo_pad, (h - ph) // 2, promo_w, ph)
            self._promo.raise_()

        if not self._ref_source.isNull():
            self._ref_scaled = self._ref_source.scaled(
                w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        else:
            self._ref_scaled = None

        self.update()

    def set_ref_overlay(self, pix: QPixmap) -> None:
        if pix.isNull():
            return
        self._ref_source = pix
        self._layout_children()

    @property
    def navigation_id(self) -> str:
        return self._tile.navigation_id

    def retranslate(self) -> None:
        self._name.setText(self._tile.label)
        if self._promo is not None and hasattr(self, "_promo_head"):
            self._promo_head.set_lines(S.HUB_PROMO_LINE1, S.HUB_PROMO_LINE2)
            self._promo_sub.setText(S.HUB_PROMO_SUB)
            self._layout_children()


class KolomnaFullbleedGrid(QWidget):
    tile_selected = pyqtSignal(str)

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self.setStyleSheet(f"background: {CREAM};")
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(0)
        self._cards: list[_FullbleedCard] = []

    def card_at(self, index: int) -> _FullbleedCard | None:
        if 0 <= index < len(self._cards):
            return self._cards[index]
        return None

    def set_tiles(self, tiles: list[KolomnaHubTile]) -> None:
        self._cards = []
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = tiles[:4]
        if not items:
            return

        for i in range(2):
            self._grid.setRowStretch(i, 1)
        for j in range(2):
            self._grid.setColumnStretch(j, 1)

        for i, tile in enumerate(items):
            card = _FullbleedCard(tile, self._m, self)
            self._cards.append(card)
            nav = tile.navigation_id
            if nav:
                card.clicked.connect(lambda n=nav: self.tile_selected.emit(n))
            else:
                card.setEnabled(False)
            r, c = divmod(i, 2)
            self._grid.addWidget(card, r, c)

    def retranslate(self) -> None:
        for card in self._cards:
            card.retranslate()
