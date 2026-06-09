from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.core.cart import Cart
from src.core.config import Settings
from src.models.product import Product
from src.services.catalog_sync import CatalogStore
from src.ui import kolomna_strings as S
from src.ui.kolomna_catalog import resolve_tour_product
from src.ui.kolomna_i18n import hub_label_for_slot
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_product_meta import fmt_price
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, RASPBERRY, STRAWBERRY, YELLOW, scale
from src.ui.screens.base_screen import BaseScreen
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.widgets.kolomna_footbar import KolomnaFootBar
from src.ui.widgets.kolomna_qty_control import KolomnaQtyControl
from src.ui.widgets.kolomna_toast import KolomnaAddedToast
from src.ui.widgets.kolomna_topbar import KolomnaTopBar

class _CouponTear(QWidget):
    """coupon__tear — пунктир на стыке head/body + cream-полукруги по краям."""

    def __init__(self, width: int, parent=None) -> None:
        super().__init__(parent)
        self._vw = width
        self._notch = scale(48, width)
        self._dash = max(1, scale(4, width))
        self.setFixedHeight(self._notch)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        y = self._dash // 2
        r = self._notch
        half = r // 2
        pen = QPen(QColor(31, 77, 42, 128), self._dash, Qt.PenStyle.DashLine)
        p.setPen(pen)
        p.drawLine(half, y, self.width() - half, y)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(CREAM))
        p.drawEllipse(-half, y - half, r, r)
        p.drawEllipse(self.width() - half, y - half, r, r)


class _TourAddButton(QWidget):
    """btn btn--yellow btn--lg btn--block — pill с тенью (Qt не скругляет QPushButton с layout)."""

    clicked = pyqtSignal()

    def __init__(self, metrics: KolomnaMetrics, label: str, parent=None) -> None:
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
        self._lbl = QLabel(label)
        self._lbl.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.Black))
        self._lbl.setStyleSheet(f"color: {GREEN}; background: transparent;")
        self._sum = QLabel()
        self._sum.setFont(kolomna_font(metrics.fs_h3, QFont.Weight.Black))
        self._sum.setStyleSheet(f"color: {GREEN}; background: transparent;")
        lay.addWidget(self._lbl)
        lay.addStretch(1)
        lay.addWidget(self._sum)

    def set_sum(self, text: str) -> None:
        self._sum.setText(text)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = rect.height() / 2.0
        w = self._m.width
        if not self._pressed:
            sr = rect.translated(0, scale(12, w))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(244, 201, 10, 128))
            p.drawRoundedRect(sr, r, r)
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


class _TourGiftIcon(QWidget):
    def __init__(self, width: int, parent=None) -> None:
        super().__init__(parent)
        s = scale(72, width)
        self.setFixedSize(s, s)

    def paintEvent(self, event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        sx = w / 72.0
        p.setBrush(QColor(STRAWBERRY))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(4 * sx), int(h - 46 * sx), int(64 * sx), int(46 * sx), int(8 * sx), int(8 * sx))
        p.setBrush(QColor(RASPBERRY))
        p.drawRoundedRect(0, int(24 * sx), int(72 * sx), int(16 * sx), int(6 * sx), int(6 * sx))
        p.setBrush(QColor(YELLOW))
        p.drawRect(int(31 * sx), int(h - 46 * sx), int(10 * sx), int(46 * sx))
        bow_y = int(10 * sx)
        p.drawEllipse(int(50 * sx - 22 * sx), bow_y, int(22 * sx), int(16 * sx))
        p.drawEllipse(int(50 * sx), bow_y, int(22 * sx), int(16 * sx))


class KolomnaToursScreen(BaseScreen):
    go_cart = pyqtSignal()
    back_to_categories = pyqtSignal()

    def __init__(self, catalog: CatalogStore, cart: Cart, settings: Settings) -> None:
        super().__init__()
        self._catalog = catalog
        self._cart = cart
        w = settings.app.content_width
        h = settings.app.content_height
        self._m = KolomnaMetrics.from_viewport(w, h)
        self._product: Product | None = None
        self._adults = KolomnaQtyControl(self._m)
        self._kids = KolomnaQtyControl(self._m, min_value=0)
        self._toast = KolomnaAddedToast(self._m, parent=self)

        self.setStyleSheet(f"background: {CREAM};")
        self.setFixedSize(w, h)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top = KolomnaTopBar(self._m, show_back=True, show_lang=True)
        self._top.set_title(hub_label_for_slot(3), accent=GREEN)
        self._top.back_clicked.connect(self.back_to_categories.emit)
        self._top.cart_clicked.connect(self.go_cart.emit)
        self._layout.addWidget(self._top)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {CREAM}; }}")
        enable_kinetic_scroll(self._scroll)

        self._scroll_host = QWidget()
        lay = QVBoxLayout(self._scroll_host)
        lay.setContentsMargins(scale(24, w), scale(24, w), scale(24, w), self._m.pad)
        lay.setSpacing(scale(30, w))

        self._coupon_widget = self._build_coupon()
        self._steps_widget = self._build_steps()
        lay.addWidget(self._coupon_widget)
        lay.addWidget(self._steps_widget)
        lay.addStretch(1)
        self._scroll.setWidget(self._scroll_host)
        self._layout.addWidget(self._scroll, stretch=1)

        self._footbar = KolomnaFootBar(self._m)
        self._footbar.hide()
        self._footbar.primary_clicked.connect(self.go_cart.emit)
        self._layout.addWidget(self._footbar)

        catalog.updated.connect(self._reload_product)
        cart.changed.connect(self._refresh_cart)
        self._adults.value_changed.connect(lambda _: self._update_add_btn())
        self._reload_product()
        self._refresh_cart()

    def _reload_product(self) -> None:
        self._product = resolve_tour_product(self._catalog.categories, self._catalog.products)
        self._update_add_btn()

    def _build_coupon(self) -> QWidget:
        m = self._m
        w = m.width
        coupon = QFrame()
        coupon.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        coupon.setStyleSheet(
            f"QFrame {{ background: transparent; border-radius: {m.radius_lg}px; }}"
        )

        root = QVBoxLayout(coupon)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        head = QFrame()
        head.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        head.setStyleSheet(
            f"QFrame {{ background: {GREEN}; border-radius: {m.radius_lg}px {m.radius_lg}px 0 0; }}"
        )
        head_lay = QVBoxLayout(head)
        head_lay.setContentsMargins(scale(52, w), scale(48, w), scale(52, w), scale(52, w))
        head_lay.setSpacing(scale(26, w))

        dlabel = QLabel(S.TOUR_DATES_TITLE.upper())
        dlabel.setFont(kolomna_font(scale(22, w), QFont.Weight.ExtraBold))
        dlabel.setStyleSheet(
            f"color: {YELLOW}; background: transparent; letter-spacing: {scale(3, w)}px;"
        )
        head_lay.addWidget(dlabel)

        cal_wrap = QWidget()
        cal_wrap.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        cal_wrap.setStyleSheet("background: transparent;")
        cal_lay = QHBoxLayout(cal_wrap)
        cal_lay.setContentsMargins(0, 0, 0, 0)
        cal_lay.setSpacing(scale(16, w))
        for month, days in S.TOUR_DATES:
            for day in days:
                cal_lay.addWidget(self._cal_item(month, day), stretch=1)
        head_lay.addWidget(cal_wrap)
        root.addWidget(head)
        root.addWidget(_CouponTear(w))

        body = QFrame()
        body.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        body.setStyleSheet(
            f"QFrame {{ background: #FFFFFF; border-radius: 0 0 {m.radius_lg}px {m.radius_lg}px; }}"
        )
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(scale(56, w), scale(50, w), scale(56, w), scale(56, w))
        body_lay.setSpacing(scale(28, w))

        guests = QHBoxLayout()
        guests.setSpacing(scale(20, w))
        adult_box, self._guest_price = self._guest_box(S.TOUR_GUEST_ADULTS, True, self._adults)
        kids_box, _ = self._guest_box(S.TOUR_GUEST_KIDS, False, self._kids)
        guests.addWidget(adult_box, stretch=1)
        guests.addWidget(kids_box, stretch=1)
        body_lay.addLayout(guests)

        self._add_btn = _TourAddButton(m, S.ADD_TO_CART)
        self._add_btn.clicked.connect(self._add_to_cart)
        body_lay.addWidget(self._add_btn)

        root.addWidget(body)
        return coupon

    def _cal_item(self, month: int, day: int) -> QWidget:
        w = self._m.width
        card_r = scale(20, w)
        box = QFrame()
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        box.setStyleSheet(f"QFrame {{ background: {CREAM}; border-radius: {card_r}px; }}")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(scale(8, w), scale(18, w), scale(8, w), scale(20, w))
        bl.setSpacing(0)
        mo = QLabel(S.MONTHS_NOM.get(month, "").upper())
        mo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mo.setFont(kolomna_font(scale(21, w), QFont.Weight.ExtraBold))
        mo.setStyleSheet(
            f"color: {STRAWBERRY}; background: transparent; letter-spacing: {max(1, scale(2, w))}px;"
        )
        d = QLabel(str(day))
        d.setAlignment(Qt.AlignmentFlag.AlignCenter)
        d.setFont(kolomna_font(scale(54, w), QFont.Weight.Black))
        d.setStyleSheet(
            f"color: {GREEN}; background: transparent; margin-top: {scale(4, w)}px;"
        )
        bl.addWidget(mo)
        bl.addWidget(d)
        return box

    def _guest_box(
        self, title: str, priced: bool, qty: KolomnaQtyControl
    ) -> tuple[QWidget, QLabel | None]:
        w = self._m.width
        box = QFrame()
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        box.setStyleSheet(
            f"QFrame {{ background: {CREAM}; border-radius: {self._m.radius}px; }}"
        )
        lay = QVBoxLayout(box)
        lay.setContentsMargins(scale(30, w), scale(26, w), scale(30, w), scale(26, w))
        lay.setSpacing(scale(18, w))
        t = QLabel(title)
        t.setFont(kolomna_font(scale(34, w), QFont.Weight.ExtraBold))
        t.setStyleSheet(f"color: {GREEN}; background: transparent;")
        lay.addWidget(t)
        price_lbl: QLabel | None = None
        if priced:
            price_lbl = QLabel()
            price_lbl.setFont(kolomna_font(scale(24, w), QFont.Weight.Bold))
            price_lbl.setStyleSheet(f"color: {INK_60}; background: transparent;")
            lay.addWidget(price_lbl)
        else:
            free = QLabel(S.TOUR_GUEST_FREE)
            free.setFont(kolomna_font(scale(24, w), QFont.Weight.Bold))
            free.setStyleSheet(f"color: {GREEN}; background: transparent;")
            lay.addWidget(free)
        lay.addWidget(qty, alignment=Qt.AlignmentFlag.AlignLeft)
        return box, price_lbl

    def _build_steps(self) -> QWidget:
        w = self._m.width
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(scale(56, w), 0, scale(56, w), 0)
        lay.setSpacing(scale(16, w))
        title = QLabel(S.TOUR_STEPS_TITLE)
        title.setFont(kolomna_font(scale(44, w), QFont.Weight.Black))
        title.setStyleSheet(
            f"color: {GREEN}; background: transparent; margin: {scale(4, w)}px 0 {scale(6, w)}px;"
        )
        lay.addWidget(title)
        for i, (t, d) in enumerate(S.TOUR_STEPS, start=1):
            lay.addLayout(self._tour_step_row(w, str(i), t, d))
        gift = QFrame()
        gift.setStyleSheet(
            f"QFrame {{ background: {CREAM_DEEP}; border-radius: {self._m.radius}px; }}"
        )
        gift_lay = QHBoxLayout(gift)
        gift_lay.setContentsMargins(scale(28, w), scale(22, w), scale(28, w), scale(22, w))
        gift_lay.setSpacing(scale(24, w))
        gift_lay.addWidget(_TourGiftIcon(w), alignment=Qt.AlignmentFlag.AlignVCenter)
        gcol = QVBoxLayout()
        gt = QLabel(S.TOUR_GIFT_TITLE)
        gt.setFont(kolomna_font(scale(30, w), QFont.Weight.ExtraBold))
        gt.setStyleSheet(f"color: {GREEN}; background: transparent; margin-bottom: {scale(4, w)}px;")
        gd = QLabel(S.TOUR_GIFT_DESC)
        gd.setWordWrap(True)
        gd.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Medium))
        gd.setStyleSheet(f"color: {INK_60}; background: transparent; line-height: 145%;")
        gcol.addWidget(gt)
        gcol.addWidget(gd)
        gift_lay.addLayout(gcol, stretch=1)
        lay.addSpacing(scale(6, w))
        lay.addWidget(gift)
        return box

    def _tour_step_row(self, w: int, num: str, title: str, desc: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(scale(22, w))
        n = QLabel(num)
        n.setFixedSize(scale(58, w), scale(58, w))
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        n.setFont(kolomna_font(scale(28, w), QFont.Weight.Black))
        n.setStyleSheet(
            f"QLabel {{ background: {GREEN}; color: {CREAM}; border-radius: {scale(29, w)}px; }}"
        )
        col = QVBoxLayout()
        col.setSpacing(scale(4, w))
        tt = QLabel(title)
        tt.setFont(kolomna_font(scale(30, w), QFont.Weight.ExtraBold))
        tt.setStyleSheet(f"color: {GREEN}; background: transparent;")
        dd = QLabel(desc)
        dd.setWordWrap(True)
        dd.setFont(kolomna_font(self._m.fs_body, QFont.Weight.Medium))
        dd.setStyleSheet(f"color: {INK_60}; background: transparent; line-height: 145%;")
        col.addWidget(tt)
        col.addWidget(dd)
        row.addWidget(n, alignment=Qt.AlignmentFlag.AlignTop)
        row.addLayout(col)
        return row

    def _update_add_btn(self) -> None:
        if not self._product:
            return
        total = self._product.price_rub * self._adults.value()
        self._add_btn.set_sum(f"{fmt_price(total)}\u00a0{S.CUR}")
        if self._guest_price is not None:
            self._guest_price.setText(
                f"{fmt_price(self._product.price_rub)}\u00a0{S.CUR} · {S.PER_PERSON}"
            )

    def _add_to_cart(self) -> None:
        if not self._product:
            return
        self._cart.add(self._product, self._adults.value())
        self._flash_toast(S.ADDED_TOAST)

    def _flash_toast(self, text: str) -> None:
        above = self._footbar if self._footbar.isVisible() else None
        bump = self._footbar._primary if above is not None else None
        self._toast.flash(text, bump_btn=bump, above=above)

    def _refresh_cart(self) -> None:
        count = self._cart.positions_count
        total = self._cart.total_display()
        self._top.update_cart(count, total)
        if count > 0:
            self._footbar.set_primary(f"{S.CART} · {count}", sum_text=total)
            self._footbar.show()
        else:
            self._footbar.hide()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._scroll_to_top()
        QTimer.singleShot(80, self._scroll_to_top)

    def _scroll_to_top(self) -> None:
        self._scroll.verticalScrollBar().setValue(0)

    def retranslate(self) -> None:
        self._top.set_title(hub_label_for_slot(3), accent=GREEN)
        self._top.retranslate()
        lay = self._scroll_host.layout()
        lay.removeWidget(self._coupon_widget)
        self._coupon_widget.deleteLater()
        lay.removeWidget(self._steps_widget)
        self._steps_widget.deleteLater()
        self._coupon_widget = self._build_coupon()
        self._steps_widget = self._build_steps()
        lay.insertWidget(0, self._coupon_widget)
        lay.insertWidget(1, self._steps_widget)
        self._refresh_cart()
        self._update_add_btn()
