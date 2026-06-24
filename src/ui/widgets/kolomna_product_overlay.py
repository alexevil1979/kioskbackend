from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QRegion
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from src.models.product import Product
from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import (
    fmt_price,
    product_description,
    product_pack_label,
    product_per_word,
    product_title,
    product_unit_word,
)
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, YELLOW, scale
from src.ui.widgets.kolomna_berry_art import KolomnaBerryArt
from src.ui.widgets.kolomna_prod_row import _PackChip
from src.ui.widgets.kolomna_qty_control import KolomnaQtyControl
from src.ui.widgets.kolomna_topbar import KolomnaTopBar


class _ProductAddBtn(QWidget):
    """btn btn--yellow btn--lg btn--block: pill, «Добавить» слева, сумма справа."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        w = metrics.width
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(scale(104, w))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._pressed = False

        pad_x = scale(56, w)
        pad_y = scale(28, w)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(pad_x, pad_y, pad_x, pad_y)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self._lbl = QLabel(S.ADD_TO_CART)
        self._lbl.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.Black))
        self._lbl.setStyleSheet(f"color: {GREEN}; background: transparent;")
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._sum = QLabel()
        self._sum.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.Black))
        self._sum.setStyleSheet(f"color: {GREEN}; background: transparent;")
        self._sum.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        lay.addWidget(self._lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        lay.addStretch(1)
        lay.addWidget(self._sum, alignment=Qt.AlignmentFlag.AlignVCenter)

    def set_sum(self, text: str) -> None:
        self._sum.setText(text)

    def set_label(self, text: str) -> None:
        self._lbl.setText(text)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = rect.height() / 2.0
        bg = QColor("#E6B800" if self._pressed else YELLOW)
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, r, r)
        p.end()
        super().paintEvent(event)

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


class KolomnaProductOverlay(QWidget):
    """Экран товара: количество + «Добавить» закреплены внизу (как product__buy в референсе)."""

    closed = pyqtSignal()
    confirmed = pyqtSignal(str, int)

    def __init__(self, metrics: KolomnaMetrics, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._product: Product | None = None
        self._category_title = ""
        self._accent = GREEN
        self._berry_art: KolomnaBerryArt | None = None
        self.setVisible(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background: {CREAM};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._top = KolomnaTopBar(metrics, show_back=True)
        self._top.back_clicked.connect(self.hide)
        root.addWidget(self._top)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {CREAM}; }}")

        inner = QWidget()
        inner.setStyleSheet(f"background: {CREAM};")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(
            metrics.pad, scale(24, metrics.width), metrics.pad, scale(24, metrics.width)
        )
        inner_lay.setSpacing(scale(34, metrics.width))

        self._media_host = QWidget()
        self._media_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._media_r = metrics.radius_lg
        self._media_host.setStyleSheet(
            f"background: {CREAM_DEEP}; border-radius: {self._media_r}px;"
        )
        self._media_lay = QVBoxLayout(self._media_host)
        self._media_lay.setContentsMargins(0, 0, 0, 0)
        inner_lay.addWidget(self._media_host)

        info = QWidget()
        info.setStyleSheet("background: transparent;")
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(0, 0, 0, 0)
        info_lay.setSpacing(scale(14, metrics.width))

        self._eyebrow = QLabel()
        self._eyebrow.hide()
        self._eyebrow.setFont(kolomna_font(metrics.fs_label, QFont.Weight.ExtraBold))
        info_lay.addWidget(self._eyebrow)

        self._title = QLabel()
        self._title.setWordWrap(True)
        self._title.setFont(kolomna_font(metrics.fs_h1, QFont.Weight.Black))
        self._title.setStyleSheet(f"color: {GREEN}; background: transparent;")
        info_lay.addWidget(self._title)

        self._desc = QLabel()
        self._desc.setWordWrap(True)
        self._desc.setFont(kolomna_font(metrics.fs_lead, QFont.Weight.Medium))
        self._desc.setStyleSheet(f"color: {INK_60}; background: transparent; line-height: 135%;")
        info_lay.addWidget(self._desc)

        self._meta_host = QWidget()
        self._meta_host.setStyleSheet("background: transparent;")
        self._meta_lay = QHBoxLayout(self._meta_host)
        self._meta_lay.setContentsMargins(0, scale(8, metrics.width), 0, 0)
        self._meta_lay.setSpacing(scale(12, metrics.width))
        info_lay.addWidget(self._meta_host)

        inner_lay.addWidget(info)
        inner_lay.addStretch(1)
        self._scroll.setWidget(inner)
        root.addWidget(self._scroll, stretch=1)

        r = metrics.radius_lg
        self._footer = QFrame()
        self._footer.setObjectName("ProductFooter")
        self._footer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._footer.setAutoFillBackground(True)
        self._footer.setStyleSheet(
            f"QFrame#ProductFooter {{ background: #FFFFFF; border: none; "
            f"border-top-left-radius: {r}px; border-top-right-radius: {r}px; }}"
        )

        buy_lay = QVBoxLayout(self._footer)
        buy_lay.setContentsMargins(
            scale(40, metrics.width),
            scale(40, metrics.width),
            scale(40, metrics.width),
            scale(40, metrics.width),
        )
        buy_lay.setSpacing(scale(26, metrics.width))

        qty_row = QHBoxLayout()
        qty_row.setSpacing(scale(20, metrics.width))
        self._qty_lbl = QLabel(S.QTY_LABEL)
        self._qty_lbl.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.ExtraBold))
        self._qty_lbl.setStyleSheet(f"color: {GREEN}; background: transparent;")
        self._qty = KolomnaQtyControl(metrics)
        self._qty_word = QLabel(S.PACKS_WORD)
        self._qty_word.setFont(kolomna_font(metrics.fs_lead, QFont.Weight.Bold))
        self._qty_word.setStyleSheet(f"color: {INK_60}; background: transparent;")
        qty_row.addWidget(self._qty_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        qty_row.addStretch(1)
        qty_row.addWidget(self._qty, alignment=Qt.AlignmentFlag.AlignVCenter)
        qty_row.addStretch(1)
        qty_row.addWidget(self._qty_word, alignment=Qt.AlignmentFlag.AlignVCenter)
        buy_lay.addLayout(qty_row)

        self._add_btn = _ProductAddBtn(metrics)
        self._add_btn.clicked.connect(self._confirm)
        self._qty.value_changed.connect(lambda _: self._update_add_btn())
        buy_lay.addWidget(self._add_btn)

        root.addWidget(self._footer, stretch=0)

    def _apply_media_clip(self) -> None:
        w, h = self._media_host.width(), self._media_host.height()
        if w < 2 or h < 2:
            return
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), self._media_r, self._media_r)
        self._media_host.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def _viewport_size(self) -> tuple[int, int]:
        parent = self.parentWidget()
        w = self._m.width
        h = self._m.height
        if parent is not None:
            if parent.width() > 0:
                w = parent.width()
            if parent.height() > 0:
                h = parent.height()
        return w, h

    def _refresh_media_layout(self) -> None:
        self._apply_media_clip()
        if self._berry_art is not None:
            w, _ = self._viewport_size()
            media_w = max(1, w - self._m.pad * 2)
            self._berry_art.setFixedWidth(media_w)
            self._berry_art.refresh_image()

    def open_product(self, product: Product, *, category_title: str, accent: str) -> None:
        self._product = product
        self._category_title = category_title
        self._accent = accent
        self._qty.set_value(1)
        self._top.set_title("")

        w, h = self._viewport_size()
        self.setGeometry(0, 0, w, h)

        if category_title:
            self._eyebrow.setText(category_title.upper())
            self._eyebrow.setStyleSheet(
                f"color: {accent}; background: transparent; "
                f"letter-spacing: {scale(3, w)}px;"
            )
            self._eyebrow.show()
        else:
            self._eyebrow.hide()

        while self._media_lay.count():
            item = self._media_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        mh = scale(600, self._m.width)
        self._media_host.setMinimumHeight(mh)
        self._media_host.setMaximumHeight(mh)
        media_w = max(1, w - self._m.pad * 2)
        self._berry_art = KolomnaBerryArt(
            product,
            media_w,
            mh,
            radius=self._media_r,
            bg=CREAM_DEEP,
            fit="cover",
        )
        self._media_lay.addWidget(self._berry_art)

        self._title.setText(product_title(product))
        desc = product_description(product)
        self._desc.setText(desc)
        self._desc.setVisible(bool(desc))

        while self._meta_lay.count():
            item = self._meta_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        chip = _PackChip(product_pack_label(product), self._m, large=True)
        per_prefix = QLabel(f"{product_per_word(product)} · ")
        per_prefix.setFont(kolomna_font(self._m.fs_lead, QFont.Weight.Bold))
        per_prefix.setStyleSheet(f"color: {INK_60}; background: transparent;")
        per_price = QLabel(f"{fmt_price(product.price_rub)}\u00a0{S.CUR}")
        per_price.setFont(kolomna_font(self._m.fs_h3, QFont.Weight.Black))
        per_price.setStyleSheet(f"color: {GREEN}; background: transparent;")
        self._meta_lay.addWidget(chip, alignment=Qt.AlignmentFlag.AlignVCenter)
        self._meta_lay.addWidget(per_prefix, alignment=Qt.AlignmentFlag.AlignVCenter)
        self._meta_lay.addWidget(per_price, alignment=Qt.AlignmentFlag.AlignVCenter)
        self._meta_lay.addStretch(1)

        self._qty_word.setText(product_unit_word(product))

        self._scroll.verticalScrollBar().setValue(0)
        self._update_add_btn()
        self.raise_()
        self.show()
        QTimer.singleShot(0, self._refresh_media_layout)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        QTimer.singleShot(0, self._refresh_media_layout)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._refresh_media_layout()

    def _update_add_btn(self) -> None:
        if not self._product:
            return
        total = self._product.price_rub * self._qty.value()
        self._add_btn.set_sum(f"{fmt_price(total)}\u00a0{S.CUR}")

    def fly_source(self) -> QWidget | None:
        return self._media_host if self._berry_art is not None else None

    def _confirm(self) -> None:
        if self._product:
            self.confirmed.emit(self._product.id, self._qty.value())

    def hide(self) -> None:  # noqa: A003
        super().hide()
        self.closed.emit()

    def retranslate(self) -> None:
        if not self._product or not self.isVisible():
            return
        qty = self._qty.value()
        self.open_product(
            self._product,
            category_title=self._category_title,
            accent=self._accent,
        )
        self._qty.set_value(qty)
        self._qty_lbl.setText(S.QTY_LABEL)
        self._add_btn.set_label(S.ADD_TO_CART)
        self._top.retranslate()
