from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QRegion
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from src.core.cart import CartLine
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import (
    fmt_price,
    full_product_name,
    product_pack_label,
    product_per_word,
)
from src.ui.kolomna_tokens import GREEN, INK_60, KolomnaMetrics, RASPBERRY, scale
from src.ui.widgets.kolomna_berry_art import KolomnaBerryArt
from src.ui.widgets.kolomna_prod_row import _PackChip, _clamp_wrapped_text, _paint_card_shadow
from src.ui.widgets.kolomna_qty_control import KolomnaQtyControl


class _CartSumBadge(QWidget):
    """cart-row__sum — сумма строки справа."""

    def __init__(self, text: str, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(scale(190, metrics.width))
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.Black))
        lbl.setStyleSheet(f"color: {GREEN}; background: transparent;")
        lay.addWidget(lbl)


class KolomnaCartRow(QWidget):
    quantity_changed = pyqtSignal(str, int)
    remove_clicked = pyqtSignal(str)

    def __init__(self, line: CartLine, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._radius = metrics.radius
        pid = line.product.id

        media_sz = scale(184, metrics.width)
        self._row_h = media_sz + scale(48, metrics.width)

        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._card = QFrame(self)
        self._card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._card.setStyleSheet("QFrame { background: transparent; border: none; }")

        root = QHBoxLayout(self._card)
        pad_v = scale(24, metrics.width)
        pad_h = scale(32, metrics.width)
        root.setContentsMargins(pad_h, pad_v, pad_h, pad_v)
        root.setSpacing(scale(28, metrics.width))
        root.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        media = QFrame()
        media.setFixedSize(media_sz, media_sz)
        media.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        media_r = scale(18, metrics.width)
        media.setStyleSheet(f"QFrame {{ background: #FFFFFF; border-radius: {media_r}px; }}")
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, media_sz, media_sz), media_r, media_r)
        media.setMask(QRegion(clip.toFillPolygon().toPolygon()))
        media_lay = QVBoxLayout(media)
        media_lay.setContentsMargins(0, 0, 0, 0)
        art = KolomnaBerryArt(
            line.product,
            media_sz,
            media_sz,
            radius=media_r,
            bg="#FFFFFF",
        )
        media_lay.addWidget(art)
        root.addWidget(media, alignment=Qt.AlignmentFlag.AlignVCenter)

        body_host = QWidget()
        body_host.setMinimumWidth(0)
        body_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        body_host.setStyleSheet("background: transparent;")

        body = QVBoxLayout(body_host)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(scale(12, metrics.width))

        sum_w = scale(190, metrics.width)
        name_font = kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold)
        body_w = max(
            40,
            metrics.width
            - 2 * metrics.pad
            - 2 * pad_h
            - media_sz
            - 2 * scale(28, metrics.width)
            - sum_w,
        )
        name_text, name_h = _clamp_wrapped_text(
            full_product_name(line.product),
            name_font,
            body_w,
            max_lines=2,
        )
        name = QLabel(name_text)
        name.setWordWrap(True)
        name.setMinimumWidth(0)
        name.setFixedHeight(name_h)
        name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        name.setFont(name_font)
        name.setStyleSheet(f"color: {GREEN}; background: transparent;")
        body.addWidget(name)

        sub = QHBoxLayout()
        sub.setSpacing(scale(16, metrics.width))
        pack_chip = _PackChip(product_pack_label(line.product), metrics)
        sub.addWidget(pack_chip, alignment=Qt.AlignmentFlag.AlignVCenter)
        unit = QLabel(
            f"{fmt_price(line.product.price_rub)}\u00a0{S.CUR} · {product_per_word(line.product)}"
        )
        unit.setFont(kolomna_font(metrics.fs_label, QFont.Weight.DemiBold))
        unit.setStyleSheet(f"color: {INK_60}; background: transparent;")
        sub.addWidget(unit)
        sub.addStretch(1)
        body.addLayout(sub)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, scale(6, metrics.width), 0, 0)
        controls.setSpacing(scale(22, metrics.width))
        qty = KolomnaQtyControl(metrics, compact=True)
        qty.set_value(line.quantity)
        qty.at_min.connect(lambda p=pid: self.remove_clicked.emit(p))
        qty.value_changed.connect(lambda v, p=pid: self.quantity_changed.emit(p, v))
        controls.addWidget(qty)

        remove = QPushButton(S.REMOVE)
        remove.setCursor(Qt.CursorShape.PointingHandCursor)
        remove.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        remove.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        remove.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {RASPBERRY}; border: none; "
            f"padding: {scale(14, metrics.width)}px {scale(18, metrics.width)}px; "
            f"min-height: {metrics.tap_min}px; }}"
            f"QPushButton:pressed {{ opacity: 0.6; }}"
        )
        remove.clicked.connect(lambda: self.remove_clicked.emit(pid))
        controls.addWidget(remove)
        controls.addStretch(1)
        body.addLayout(controls)

        root.addWidget(body_host, stretch=1)

        sum_w = _CartSumBadge(f"{fmt_price(line.line_total)}\u00a0{S.CUR}", metrics)
        root.addWidget(sum_w, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._card.setMinimumHeight(media_sz)
        self._sync_geometry()

    def _shadow_bleed(self) -> int:
        return scale(20, self._m.width)

    def _apply_round_clip(self) -> None:
        w = max(1, self._card.width())
        h = max(1, self._card.height())
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), self._radius, self._radius)
        self._card.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def _sync_geometry(self) -> None:
        w = max(1, self.width())
        h = max(self._card.sizeHint().height(), scale(184, self._m.width) + scale(48, self._m.width))
        h = max(h, self._card.minimumHeight())
        self._card.setGeometry(0, 0, w, h)
        self._apply_round_clip()
        self.setFixedHeight(h + self._shadow_bleed())

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = max(1, self.width())
        h = self._card.height()
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
