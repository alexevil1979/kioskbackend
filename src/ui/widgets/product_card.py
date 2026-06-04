from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics, QPainterPath, QPixmap, QRegion
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.models.product import Product
from src.ui.image_utils import load_pixmap, scale_pixmap_cover


class ProductCard(QFrame):
    card_clicked = pyqtSignal(str)
    like_toggled = pyqtSignal(str, bool)
    quantity_changed = pyqtSignal(str, int)

    def __init__(
        self,
        product: Product,
        qty: int = 0,
        *,
        image_size: int = 220,
        phone_layout: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ProductCard")
        self.setStyleSheet(
            "QFrame#ProductCard{background:#FFFFFF;border:1px solid #E5E7EB;border-radius:20px;}"
        )
        self._product = product
        self._qty = qty
        self._image_size = image_size
        self._photo_size = max(120, image_size - 24)
        self._phone_layout = phone_layout

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        self._photo_wrap = QFrame()
        self._photo_wrap.setObjectName("ProductPhotoWrap")
        self._photo_wrap.setFixedSize(self._photo_size, self._photo_size)
        self._photo_wrap.setStyleSheet("QFrame#ProductPhotoWrap{border:none;border-radius:20px;background:transparent;}")
        photo_grid = QGridLayout(self._photo_wrap)
        photo_grid.setContentsMargins(0, 0, 0, 0)

        self._photo = QLabel()
        self._photo.setObjectName("ProductImage")
        self._photo.setFixedSize(self._photo_size, self._photo_size)
        self._photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._photo.setStyleSheet("QLabel#ProductImage{background:#F0F1F3;border:none;border-radius:20px;}")
        self._load_image()
        photo_grid.addWidget(self._photo, 0, 0)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(10, 10, 10, 0)
        self._fav = QPushButton("♥")
        self._fav.setObjectName("ProductFavBtn")
        self._fav.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._fav.setCheckable(True)
        self._fav.setFixedSize(30, 30)
        self._fav.setStyleSheet(
            "QPushButton#ProductFavBtn{background:#F3F4F6;border:1px solid #DDE1E6;border-radius:15px;color:#C0C6CF;font-size:18px;font-weight:700;padding:0;}"
            "QPushButton#ProductFavBtn:checked{background:#FFFFFF;color:#FF4D5A;}"
        )
        self._fav.clicked.connect(
            lambda checked: self.like_toggled.emit(self._product.id, checked)
        )
        top_row.addWidget(self._fav)
        top_row.addStretch(1)
        photo_grid.addLayout(top_row, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 12)
        bottom_row.addStretch(1)
        self._soon = QLabel("СКОРО")
        self._soon.setObjectName("ProductSoonBadge")
        self._soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._soon.setFixedSize(84, 24)
        self._soon.setStyleSheet(
            "QLabel#ProductSoonBadge{background:#3CB85D;color:#FFFFFF;border-radius:12px;"
            "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;font-size:11px;font-weight:700;}"
        )
        bottom_row.addWidget(self._soon)
        bottom_row.addStretch(1)
        photo_grid.addLayout(bottom_row, 0, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        root.addWidget(self._photo_wrap)

        body = QWidget()
        body.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(8)

        self._name = QLabel(product.name)
        self._name.setObjectName("ProductName")
        self._name.setWordWrap(True)
        name_font = QFont("Inter", 14)
        name_font.setWeight(QFont.Weight.Bold)
        self._name.setFont(name_font)
        self._name.setFixedWidth(self._name_text_width())
        self._name.setStyleSheet(
            "QLabel#ProductName{font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
            "font-size:14px;font-weight:700;color:#0F172A;background:transparent;}"
        )
        body_lay.addWidget(self._name)

        price_row = QHBoxLayout()
        price_row.setContentsMargins(0, 0, 0, 0)
        price_row.setSpacing(6)
        price = QLabel(product.price_display)
        price.setObjectName("ProductPrice")
        unit = QLabel(f"/ {product.unit}")
        unit.setObjectName("ProductUnitInline")
        price.setStyleSheet(
            "QLabel#ProductPrice{font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;"
            "font-size:17px;font-weight:700;color:#4F5D73;background:transparent;}"
        )
        unit.setStyleSheet(
            "QLabel#ProductUnitInline{font-family:'Inter',ui-sans-serif,system-ui,sans-serif;"
            "font-size:12px;font-weight:700;color:#A2A9B5;background:transparent;}"
        )
        price_row.addWidget(price)
        price_row.addWidget(unit)
        price_row.addStretch(1)
        body_lay.addLayout(price_row)
        body_lay.addStretch(1)

        self._actions = QHBoxLayout()
        self._actions.setContentsMargins(0, 2, 0, 0)
        self._actions.setSpacing(8)

        self._add_btn = QPushButton("ДОБАВИТЬ")
        self._add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._add_btn.setFixedHeight(38)
        self._add_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        inner_w = max(80, image_size - 24)
        self._add_btn.setFixedWidth(inner_w)
        self._add_btn.setStyleSheet(
            "QPushButton{background:#35C46A;color:#051B0D;border:none;border-radius:14px;"
            "font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;font-size:12px;font-weight:700;padding:0 14px;}"
            "QPushButton:pressed{background:#2FB05E;}"
        )
        self._add_btn.clicked.connect(self._on_add_clicked)
        self._actions.addWidget(self._add_btn)

        self._qty_wrap = QWidget()
        qty_lay = QHBoxLayout(self._qty_wrap)
        qty_lay.setContentsMargins(0, 0, 0, 0)
        qty_lay.setSpacing(8)
        self._qty_minus = QPushButton("−")
        self._qty_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        self._qty_minus.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._qty_minus.setFixedSize(42, 38)
        self._qty_minus.setStyleSheet(
            "QPushButton{background:#FFFFFF;border:2px solid #35C46A;border-radius:12px;"
            "color:#13223A;font-size:22px;font-weight:700;}"
        )
        self._qty_minus.clicked.connect(lambda: self._change_qty(-1))
        self._qty_num = QLabel("0")
        self._qty_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_num.setMinimumWidth(30)
        self._qty_num.setStyleSheet(
            "QLabel{font-family:'Unbounded',ui-sans-serif,system-ui,sans-serif;"
            "font-size:18px;font-weight:700;color:#13223A;background:transparent;}"
        )
        self._qty_plus = QPushButton("+")
        self._qty_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        self._qty_plus.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._qty_plus.setFixedSize(42, 38)
        self._qty_plus.setStyleSheet(
            "QPushButton{background:#FFFFFF;border:2px solid #35C46A;border-radius:12px;"
            "color:#13223A;font-size:22px;font-weight:700;}"
        )
        self._qty_plus.clicked.connect(lambda: self._change_qty(1))
        qty_lay.addWidget(self._qty_minus)
        qty_lay.addWidget(self._qty_num)
        qty_lay.addWidget(self._qty_plus)
        self._actions.addWidget(self._qty_wrap)

        actions_host = QWidget()
        actions_host.setLayout(self._actions)
        actions_host.setFixedHeight(40)
        body_lay.addWidget(actions_host)

        root.addWidget(body, 1)
        self._sync_qty_ui()

    def _name_text_width(self) -> int:
        return max(40, self._image_size - 24)

    def _title_font(self) -> QFont:
        font = QFont(self._name.font())
        font.setFamily("Inter")
        font.setPointSize(14)
        font.setWeight(QFont.Weight.Bold)
        return font

    def measure_name_slot_height(self) -> int:
        """Высота блока названия с переносом (как после отрисовки в карточке)."""
        width = self._name_text_width()
        fm = QFontMetrics(self._title_font())
        line_h = max(1, fm.height())
        max_lines = 2 if self._phone_layout else 3
        max_h = line_h * max_lines
        rect = fm.boundingRect(
            0,
            0,
            width,
            max_h * 8,
            int(Qt.TextFlag.TextWordWrap),
            self._name.text(),
        )
        return max(line_h, min(max_h, rect.height()))

    @staticmethod
    def content_height_for(image_size: int, photo_size: int, name_slot_h: int) -> int:
        return 12 + photo_size + 10 + name_slot_h + 8 + 22 + 2 + 40 + 12

    def apply_row_layout(self, name_slot_h: int) -> int:
        """Одинаковый слот названия в ряду; кнопка прижата к низу. Возвращает высоту карточки."""
        self._name.setFixedWidth(self._name_text_width())
        self._name.setFixedHeight(name_slot_h)
        card_h = self.content_height_for(
            self._image_size, self._photo_size, name_slot_h
        )
        root = self.layout()
        if isinstance(root, QVBoxLayout):
            root.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setFixedSize(self._image_size, card_h)
        self.setMinimumSize(self._image_size, card_h)
        self.setMaximumSize(self._image_size, card_h)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        self.updateGeometry()
        return card_h

    @classmethod
    def card_height_for(cls, image_size: int, *, phone_layout: bool) -> int:
        """Оценка высоты ряда при двух строках названия."""
        photo = max(120, image_size - 24)
        name_h = 52 if phone_layout else 64
        return 12 + photo + 10 + name_h + 8 + 22 + 2 + 38 + 12

    def _load_image(self) -> None:
        path = self._product.image_local
        if not path:
            self._set_placeholder()
            return
        pix = load_pixmap(path)
        if pix.isNull():
            self._set_placeholder()
            return
        self._photo.setPixmap(
            scale_pixmap_cover(pix, self._photo_size, self._photo_size)
        )

    def _set_placeholder(self) -> None:
        self._photo.setPixmap(QPixmap())
        self._photo.setText("")

    def set_quantity(self, qty: int) -> None:
        self._qty = max(0, qty)
        self._sync_qty_ui()

    def _sync_qty_ui(self) -> None:
        self._qty_num.setText(str(max(0, self._qty)))
        has_qty = self._qty > 0
        self._add_btn.setVisible(not has_qty)
        self._qty_wrap.setVisible(has_qty)

    def _on_add_clicked(self) -> None:
        self._qty = 1
        self._sync_qty_ui()
        self.quantity_changed.emit(self._product.id, self._qty)

    def _change_qty(self, delta: int) -> None:
        next_qty = max(0, self._qty + delta)
        if self._product.stock > 0:
            next_qty = min(next_qty, self._product.stock)
        if next_qty == self._qty:
            return
        self._qty = next_qty
        self._sync_qty_ui()
        self.quantity_changed.emit(self._product.id, self._qty)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            local = event.position().toPoint()
            widget = self.childAt(local)
            while widget is not None:
                if widget in (
                    self._fav,
                    self._add_btn,
                    self._qty_minus,
                    self._qty_plus,
                ):
                    super().mouseReleaseEvent(event)
                    return
                widget = widget.parentWidget()
            self.card_clicked.emit(self._product.id)
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        path = QPainterPath()
        path.addRoundedRect(
            0,
            0,
            self._photo_wrap.width(),
            self._photo_wrap.height(),
            20,
            20,
        )
        self._photo_wrap.setMask(QRegion(path.toFillPolygon().toPolygon()))
