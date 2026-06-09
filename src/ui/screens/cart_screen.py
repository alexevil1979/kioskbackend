from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainterPath, QRegion

from src.ui.image_utils import load_pixmap, scale_pixmap_cover
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from src.core.cart import Cart, CartLine
from src.core.config import Settings
from src.ui.layout_metrics import LayoutMetrics
from src.ui.scroll_utils import enable_kinetic_scroll
from src.ui.screens.base_screen import BaseScreen
from src.ui.widgets.buttons import danger_button, outline_button, primary_button, secondary_button


class CartScreen(BaseScreen):
    continue_shopping = pyqtSignal()
    pay = pyqtSignal()

    def __init__(self, cart: Cart, settings: Settings | None = None) -> None:
        super().__init__()
        self._cart = cart
        metrics = LayoutMetrics.from_app_config(settings.app) if settings else None
        self._portrait = metrics.is_portrait if metrics else False
        card_w = metrics.product_image_size if metrics else 220
        catalog_photo = max(120, card_w - 24)
        inner_w = (metrics.width - 24) if metrics else 451
        # Эталон: фото ~половина карточки, как в каталоге по crop/радиусу.
        self._thumb_size = min(catalog_photo, max(148, (inner_w - 10) // 2))
        self._row_height = self._thumb_size + 24
        self.setObjectName("CartScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("QWidget#CartScreen { background:#F6EFD8; }")
        self._layout.setContentsMargins(12, 10, 12, 12)
        self._layout.setSpacing(10)

        title = QLabel("Ваш заказ")
        title.setObjectName("ScreenTitle")
        title.setStyleSheet(
            "font-family:'Montserrat',ui-sans-serif,system-ui,sans-serif;"
            "font-size:30px;font-weight:900;color:#1F4D2A;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter if self._portrait else Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setObjectName("CartScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea#CartScroll { border:none; background:transparent; }"
        )
        vp = scroll.viewport()
        vp.setStyleSheet("background:transparent;")
        vp.setAutoFillBackground(True)
        enable_kinetic_scroll(scroll)
        self._list_host = QWidget()
        self._list_host.setStyleSheet("background:transparent;")
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(10)
        scroll.setWidget(self._list_host)
        self._layout.addWidget(scroll, stretch=1)

        self._total_label = QLabel()
        self._total_label.setStyleSheet(
            "font-family:'Montserrat',ui-sans-serif,system-ui,sans-serif;"
            "font-size:24px;font-weight:900;color:#1F4D2A;"
        )
        self._total_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter if self._portrait else Qt.AlignmentFlag.AlignLeft
        )
        self._layout.addWidget(self._total_label)

        if self._portrait:
            self._btn_pay = primary_button("Перейти к оплате")
            self._btn_pay.setMinimumHeight(52)
            self._btn_pay.setStyleSheet(
                "QPushButton#PrimaryBtn{background:#1F4D2A;color:#F6EFD8;border:none;border-radius:999px;"
                "font-family:'Montserrat',ui-sans-serif,system-ui,sans-serif;font-size:14px;font-weight:800;}"
                "QPushButton#PrimaryBtn:pressed{background:#143821;}"
                "QPushButton#PrimaryBtn:disabled{background:#1F4D2A;color:#F6EFD8;opacity:0.45;}"
            )
            self._btn_pay.clicked.connect(self.pay.emit)
            self._layout.addWidget(self._btn_pay)
            btn_back = secondary_button("Добавить ещё")
            btn_back.setMinimumHeight(48)
            btn_back.setStyleSheet(
                "QPushButton#SecondaryBtn{background:#FFFFFF;color:#1F4D2A;border:2px solid #ECE0BC;border-radius:999px;"
                "font-family:'Montserrat',ui-sans-serif,system-ui,sans-serif;font-size:14px;font-weight:700;}"
            )
            btn_back.clicked.connect(self.continue_shopping.emit)
            self._layout.addWidget(btn_back)
        else:
            actions = QHBoxLayout()
            btn_back = secondary_button("Продолжить выбор")
            btn_back.clicked.connect(self.continue_shopping.emit)
            actions.addWidget(btn_back)
            self._btn_pay = primary_button("Оплатить")
            self._btn_pay.setMinimumWidth(280)
            self._btn_pay.clicked.connect(self.pay.emit)
            actions.addWidget(self._btn_pay)
            self._layout.addLayout(actions)

        cart.changed.connect(self._rebuild)

    def _rebuild(self) -> None:
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for line in self._cart.lines:
            self._list_layout.addWidget(self._row_widget(line))

        if not self._cart.lines:
            empty = QLabel("Корзина пуста")
            empty.setObjectName("Subtitle")
            empty.setStyleSheet("font-size:14px;color:#6B7280;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)

        self._total_label.setText(f"Итого: {self._cart.total_display()}")
        self._btn_pay.setEnabled(self._cart.positions_count > 0)

    def _row_widget(self, line: CartLine) -> QFrame:
        frame = QFrame()
        frame.setObjectName("CartRow")
        frame.setFixedHeight(self._row_height)
        frame.setStyleSheet("QFrame#CartRow{background:#FFFFFF;border:1px solid #E5E7EB;border-radius:18px;}")
        root = QHBoxLayout(frame)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        thumb_wrap = QFrame()
        thumb_wrap.setFixedSize(self._thumb_size, self._thumb_size)
        thumb_wrap.setStyleSheet("QFrame{background:transparent;border:none;border-radius:20px;}")
        thumb = QLabel(thumb_wrap)
        thumb.setObjectName("ProductImage")
        thumb.setFixedSize(self._thumb_size, self._thumb_size)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet("QLabel#ProductImage{background:#F0F1F3;border:none;border-radius:20px;}")
        if line.product.image_local:
            pix = load_pixmap(line.product.image_local)
            if not pix.isNull():
                thumb.setPixmap(
                    scale_pixmap_cover(pix, self._thumb_size, self._thumb_size)
                )
        clip_path = QPainterPath()
        clip_path.addRoundedRect(0, 0, self._thumb_size, self._thumb_size, 20, 20)
        thumb_wrap.setMask(QRegion(clip_path.toFillPolygon().toPolygon()))
        root.addWidget(thumb_wrap, alignment=Qt.AlignmentFlag.AlignVCenter)

        right = QWidget()
        right.setFixedHeight(self._thumb_size)
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(4)

        name = QLabel(line.product.name)
        name.setWordWrap(True)
        name.setMaximumHeight(44)
        name.setStyleSheet("font-size:14px;font-weight:700;color:#0F172A;line-height:1.2;")
        right_lay.addWidget(name)

        unit_price = QLabel(f"{line.product.price_display} / {line.product.unit}")
        unit_price.setStyleSheet("font-size:12px;color:#7B8596;font-weight:600;")
        right_lay.addWidget(unit_price)

        right_lay.addStretch(1)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(8)

        qty_row = QHBoxLayout()
        qty_row.setSpacing(6)
        btn_m = outline_button("−")
        btn_m.setFixedSize(34, 34)
        btn_m.setStyleSheet(
            "QPushButton#OutlineBtn{background:#FFFFFF;border:2px solid #35C46A;border-radius:11px;"
            "color:#13223A;font-size:18px;font-weight:700;}"
        )
        btn_m.clicked.connect(lambda: self._change_qty(line.product.id, line.quantity - 1))
        lbl = QLabel(str(line.quantity))
        lbl.setStyleSheet(
            "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;font-size:16px;font-weight:700;min-width:20px;"
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_p = outline_button("+")
        btn_p.setFixedSize(34, 34)
        btn_p.setStyleSheet(
            "QPushButton#OutlineBtn{background:#FFFFFF;border:2px solid #35C46A;border-radius:11px;"
            "color:#13223A;font-size:18px;font-weight:700;}"
        )
        btn_p.clicked.connect(lambda: self._change_qty(line.product.id, line.quantity + 1))
        qty_row.addWidget(btn_m)
        qty_row.addWidget(lbl)
        qty_row.addWidget(btn_p)
        controls.addLayout(qty_row)

        controls.addStretch(1)

        line_total = QLabel(
            f"{line.line_total:.0f} ₽"
            if line.line_total == int(line.line_total)
            else f"{line.line_total:.2f} ₽"
        )
        line_total.setStyleSheet(
            "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;font-size:14px;font-weight:700;color:#1F6D4A;"
        )
        line_total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        controls.addWidget(line_total)

        btn_del = danger_button("✕")
        btn_del.setFixedSize(32, 32)
        btn_del.setStyleSheet(
            "QPushButton#DangerBtn{background:#F3F4F6;color:#667085;border:1px solid #DDE1E6;border-radius:10px;font-size:14px;font-weight:700;}"
        )
        btn_del.clicked.connect(lambda: self._cart.remove(line.product.id))
        controls.addWidget(btn_del)

        right_lay.addLayout(controls)
        root.addWidget(right, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        return frame

    def _change_qty(self, product_id: str, qty: int) -> None:
        if qty <= 0:
            self._cart.remove(product_id)
        else:
            self._cart.set_quantity(product_id, qty)
