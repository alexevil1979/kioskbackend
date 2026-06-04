from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QWidget

from src.core.config import ROOT
from src.ui.image_utils import load_pixmap
from src.ui.katusha_hub_tokens import NAV_HEIGHT, VIEWPORT_W

_NAV_REF = ROOT / "assets" / "reference" / "nav_strip.png"
_TAB_W = VIEWPORT_W // 5
_NAV_TOP_CROP = 10

_TABS: tuple[tuple[str, str], ...] = (
    ("orders", "ЗАКАЗЫ"),
    ("feed", "ЛЕНТА"),
    ("catalog", "КАТАЛОГ"),
    ("cart", "КОРЗИНА"),
    ("profile", "ПРОФИЛЬ"),
)


class BottomNavBar(QFrame):
    """Нижнее меню 1:1 — вырезка из screen_katusha.png."""

    catalog_clicked = pyqtSignal()
    cart_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BottomNavBar")
        self.setFixedHeight(NAV_HEIGHT)

        art = QLabel(self)
        art.setObjectName("BottomNavArt")
        art.setGeometry(0, 0, VIEWPORT_W, NAV_HEIGHT)
        if _NAV_REF.is_file():
            pix = load_pixmap(_NAV_REF)
            if not pix.isNull():
                art.setPixmap(_fit_nav(pix, VIEWPORT_W, NAV_HEIGHT))

        for i, (kind, _label) in enumerate(_TABS):
            btn = QPushButton(self)
            btn.setObjectName(f"NavHit_{kind}")
            btn.setGeometry(i * _TAB_W, 0, _TAB_W, NAV_HEIGHT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setStyleSheet("background: transparent; border: none;")
            if kind == "catalog":
                btn.clicked.connect(self.catalog_clicked.emit)
            elif kind == "cart":
                btn.clicked.connect(self.cart_clicked.emit)

    def set_active(self, tab: str) -> None:
        pass


def _fit_nav(pix: QPixmap, w: int, h: int) -> QPixmap:
    # В референсном nav_strip сверху может оставаться шумная полоска от контента.
    # Срезаем верхние пиксели и масштабируем оставшуюся область.
    if pix.height() > _NAV_TOP_CROP + 10:
        pix = pix.copy(0, _NAV_TOP_CROP, pix.width(), pix.height() - _NAV_TOP_CROP)
    if pix.width() == w and pix.height() == h:
        return pix
    return pix.scaled(
        w,
        h,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
