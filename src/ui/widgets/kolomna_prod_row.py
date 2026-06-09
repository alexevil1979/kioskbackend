from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QRegion
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.models.product import Product
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import (
    fmt_price,
    product_description,
    product_pack_label,
    product_per_word,
    product_title,
)
from src.ui.kolomna_tokens import CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, YELLOW, scale
from src.ui.widgets.kolomna_berry_art import KolomnaBerryArt


def _paint_card_shadow(p: QPainter, card_rect: QRectF, radius: float, metrics: KolomnaMetrics) -> None:
    w = metrics.width
    shrink = scale(24, w)
    for y_off, alpha in (
        (scale(18, w), 14),
        (scale(24, w), 28),
        (scale(30, w), 16),
    ):
        sr = QRectF(
            shrink / 2,
            y_off,
            card_rect.width() - shrink,
            card_rect.height() - shrink / 2,
        )
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(20, 56, 33, alpha))
        p.drawRoundedRect(sr, radius, radius)


def _clamp_wrapped_text(
    text: str,
    font: QFont,
    width: int,
    *,
    max_lines: int = 2,
    line_height: float = 1.35,
) -> tuple[str, int]:
    """Не более max_lines строк; лишнее — «…» в конце последней строки."""
    text = text.strip()
    if not text or width <= 0:
        return "", 0
    fm = QFontMetrics(font)
    line_h = max(1, round(fm.height() * line_height))
    words = text.split()
    lines: list[str] = []
    idx = 0
    while idx < len(words) and len(lines) < max_lines:
        line = ""
        while idx < len(words):
            trial = f"{line} {words[idx]}".strip()
            if fm.horizontalAdvance(trial) <= width:
                line = trial
                idx += 1
            else:
                if not line:
                    line = fm.elidedText(words[idx], Qt.TextElideMode.ElideRight, width)
                    idx += 1
                break
        if line:
            lines.append(line)
    if idx < len(words) and lines:
        ell = "…"
        last = lines[-1]
        while last and fm.horizontalAdvance(f"{last}{ell}") > width:
            last = last[:-1].rstrip()
        lines[-1] = f"{last}{ell}" if last else ell
    return "\n".join(lines), line_h * max(len(lines), 1)


class _PackChip(QWidget):
    """chip / chip--lg — cream pill (border-radius: 999px в референсе)."""

    def __init__(
        self,
        text: str,
        metrics: KolomnaMetrics,
        *,
        large: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        w = metrics.width
        fs = scale(26, w) if large else scale(22, w)
        pad_v = scale(14, w) if large else scale(10, w)
        pad_h = scale(28, w) if large else scale(22, w)
        self._chip_text = text
        self._font = kolomna_font(fs, QFont.Weight.ExtraBold)
        fm = QFontMetrics(self._font)
        self.setFixedSize(
            fm.horizontalAdvance(text) + pad_h * 2,
            fm.height() + pad_v * 2,
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = rect.height() / 2.0
        pill = QPainterPath()
        pill.addRoundedRect(rect, r, r)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(CREAM_DEEP))
        p.fillPath(pill, QColor(CREAM_DEEP))
        p.setFont(self._font)
        p.setPen(QColor(GREEN))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._chip_text)
        p.end()


class _ProdAddBtn(QWidget):
    """btn btn--yellow в prod-row__foot."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._pressed = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        w = metrics.width
        text = f"+ {S.ADD_SHORT}"
        self._label = text
        self._font = kolomna_font(metrics.fs_body, QFont.Weight.Black)
        pad_v = scale(18, w)
        pad_h = scale(32, w)
        fm = QFontMetrics(self._font)
        btn_w = fm.horizontalAdvance(text) + pad_h * 2
        btn_h = max(scale(56, w), fm.height() + pad_v * 2)
        self.setFixedSize(btn_w, btn_h)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = rect.height() / 2.0
        vw = self._m.width
        if not self._pressed:
            sr = rect.translated(0, scale(8, vw))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(244, 201, 10, 100))
            p.drawRoundedRect(sr, r, r)
        bg = QColor("#E0B800" if self._pressed else YELLOW)
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, r, r)
        p.setFont(self._font)
        p.setPen(QColor(GREEN))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._label)
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


class KolomnaProdRow(QWidget):
    """prod-row: белая карточка, фото слева, текст и «+ В корзину»."""

    clicked = pyqtSignal(str)
    add_clicked = pyqtSignal(str)

    def __init__(self, product: Product, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._product = product
        self._m = metrics
        self._radius = metrics.radius
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        media_w = scale(400, metrics.width)
        # prod-row на референсе ≈ scale(400) по высоте (400×400 @ 1080)
        self._card_h = scale(400, metrics.width)
        self._media_h = self._card_h

        self._card = QFrame(self)
        self._card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._card.setStyleSheet("QFrame { background: transparent; border: none; }")

        root = QHBoxLayout(self._card)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(scale(28, metrics.width))

        media = KolomnaBerryArt(
            product,
            media_w,
            self._media_h,
            radius=0,
            bg=CREAM_DEEP,
        )
        media.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._media = media
        root.addWidget(media)

        self._body_host = QWidget()
        self._body_host.setMinimumWidth(0)
        self._body_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._body_host.setStyleSheet("background: transparent;")
        self._body_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        body = QVBoxLayout(self._body_host)
        body.setContentsMargins(0, scale(34, metrics.width), scale(36, metrics.width), scale(30, metrics.width))
        body.setSpacing(scale(14, metrics.width))

        title = QLabel(product_title(product))
        title.setWordWrap(True)
        title.setFont(kolomna_font(metrics.fs_h2, QFont.Weight.Black))
        title.setStyleSheet(f"color: {GREEN}; background: transparent;")
        body.addWidget(title)

        desc_raw = product_description(product)
        if desc_raw:
            desc_font = kolomna_font(metrics.fs_lead, QFont.Weight.Medium)
            body_w = max(
                40,
                metrics.width - 2 * metrics.gap - media_w - scale(28, metrics.width) - scale(36, metrics.width),
            )
            desc_text, desc_h = _clamp_wrapped_text(desc_raw, desc_font, body_w, max_lines=2)
            d = QLabel(desc_text)
            d.setWordWrap(True)
            d.setMinimumWidth(0)
            d.setFixedHeight(desc_h)
            d.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            d.setFont(desc_font)
            d.setStyleSheet(f"color: {INK_60}; background: transparent; line-height: 135%;")
            body.addWidget(d)

        meta = QHBoxLayout()
        meta.setSpacing(scale(18, metrics.width))
        chip = _PackChip(product_pack_label(product), metrics)
        per = QLabel(product_per_word(product))
        per.setFont(kolomna_font(metrics.fs_label, QFont.Weight.Bold))
        per.setStyleSheet(f"color: {INK_60}; background: transparent;")
        meta.addWidget(chip, alignment=Qt.AlignmentFlag.AlignVCenter)
        meta.addWidget(per, alignment=Qt.AlignmentFlag.AlignVCenter)
        meta.addStretch(1)
        body.addLayout(meta)

        body.addStretch(1)

        foot = QHBoxLayout()
        foot.setSpacing(scale(20, metrics.width))
        price = QLabel(f"{fmt_price(product.price_rub)}\u00a0{S.CUR}")
        price.setFont(kolomna_font(metrics.fs_h2, QFont.Weight.Black))
        price.setStyleSheet(f"color: {GREEN}; background: transparent;")
        foot.addWidget(price, alignment=Qt.AlignmentFlag.AlignVCenter)

        foot.addStretch(1)

        add = _ProdAddBtn(metrics)
        add.clicked.connect(self._on_add)
        self._add_btn = add
        foot.addWidget(add, alignment=Qt.AlignmentFlag.AlignVCenter)

        foot_wrap = QWidget()
        foot_wrap.setStyleSheet("background: transparent;")
        foot_outer = QVBoxLayout(foot_wrap)
        foot_outer.setContentsMargins(0, scale(16, metrics.width), 0, 0)
        foot_outer.addLayout(foot)
        body.addWidget(foot_wrap)

        root.addWidget(self._body_host, stretch=1)

        self._card.setMinimumHeight(self._card_h)
        self._sync_geometry()

    def _shadow_bleed(self) -> int:
        return scale(36, self._m.width)

    def _apply_round_clip(self) -> None:
        w = max(1, self._card.width())
        h = max(1, self._card.height())
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), self._radius, self._radius)
        self._card.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def _sync_geometry(self) -> None:
        w = max(1, self.width())
        h = self._card_h
        self._card.setGeometry(0, 0, w, h)
        self._apply_round_clip()
        self.setFixedHeight(h + self._shadow_bleed())

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(1, self.width())
        h = self._card_h
        r = float(self._radius)
        card_rect = QRectF(0, 0, w, h)
        _paint_card_shadow(p, card_rect, r, self._m)
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(card_rect, r, r)
        p.end()
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_geometry()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._sync_geometry()

    def media_widget(self) -> QWidget:
        return self._media

    @property
    def product_id(self) -> str:
        return self._product.id

    def _on_add(self) -> None:
        self.add_clicked.emit(self._product.id)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            add_pos = self._add_btn.mapFrom(self, pos)
            if self._add_btn.rect().contains(add_pos):
                super().mouseReleaseEvent(event)
                return
            self.clicked.emit(self._product.id)
        super().mouseReleaseEvent(event)
