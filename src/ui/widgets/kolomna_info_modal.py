from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.ui import kolomna_strings as S
from src.ui.kolomna_fonts import kolomna_font
from src.ui.kolomna_tokens import CREAM, CREAM_DEEP, GREEN, INK_60, KolomnaMetrics, scale
from src.ui.widgets.kolomna_qr_label import KolomnaQrTile


def _transparent(parent=None) -> QWidget:
    w = QWidget(parent)
    w.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    w.setStyleSheet("background: transparent;")
    return w


class KolomnaInfoModal(QWidget):
    """info-modal — о ферме, контакты, QR (как в offline-референсе)."""

    def __init__(self, metrics: KolomnaMetrics, hours: str, parent=None) -> None:
        super().__init__(parent)
        self._m = metrics
        self._hours = hours
        self.setVisible(False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: rgba(20, 56, 33, 0.55);")

        self._outer_pad = scale(80, metrics.width)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(self._outer_pad, self._outer_pad, self._outer_pad, self._outer_pad)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        avail_w = max(1, metrics.width - 2 * self._outer_pad)
        box_w = min(scale(880, metrics.width), avail_w)

        self._box = QWidget()
        self._box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._box.setStyleSheet(
            f"QWidget#KolomnaInfoBox {{ background: {CREAM}; "
            f"border-radius: {metrics.radius_lg}px; }}"
        )
        self._box.setObjectName("KolomnaInfoBox")
        self._box.setFixedWidth(box_w)
        self._box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        box_shadow = QGraphicsDropShadowEffect(self._box)
        box_shadow.setBlurRadius(scale(60, metrics.width))
        box_shadow.setOffset(0, scale(24, metrics.width))
        box_shadow.setColor(QColor(20, 56, 33, 102))
        self._box.setGraphicsEffect(box_shadow)

        box_lay = QVBoxLayout(self._box)
        pad64 = scale(64, metrics.width)
        box_lay.setContentsMargins(pad64, pad64, pad64, pad64)
        box_lay.setSpacing(scale(26, metrics.width))
        box_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._close = QPushButton("×", self._box)
        sz = scale(84, metrics.width)
        self._close.setFixedSize(sz, sz)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.setFont(kolomna_font(scale(52, metrics.width), QFont.Weight.Normal))
        self._close.setStyleSheet(
            f"QPushButton {{ background: {CREAM_DEEP}; color: {GREEN}; border: none; "
            f"border-radius: {sz // 2}px; }}"
            f"QPushButton:pressed {{ background: rgba(31,77,42,0.22); }}"
        )
        self._close.clicked.connect(self.hide)
        self._close.raise_()
        self._box.installEventFilter(self)

        self._title = QLabel(S.INFO_TITLE)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setFont(kolomna_font(metrics.fs_h1, QFont.Weight.Black))
        self._title.setStyleSheet(
            f"color: {GREEN}; background: transparent; margin-top: {scale(6, metrics.width)}px;"
        )
        box_lay.addWidget(self._title)

        contacts = _transparent()
        contacts_lay = QVBoxLayout(contacts)
        contacts_lay.setContentsMargins(0, 0, 0, 0)
        contacts_lay.setSpacing(scale(16, metrics.width))
        contacts_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._hours_label = QLabel(hours)
        self._contact_keys: list[QLabel] = []
        self._contact_vals: list[QLabel] = []
        for label, value in (
            (S.INFO_HOURS_LABEL, self._hours_label),
            (S.INFO_PHONE_LABEL, QLabel(S.INFO_PHONE)),
            (S.INFO_SITE_LABEL, QLabel(S.INFO_SITE)),
        ):
            if value is not self._hours_label:
                value.setFont(kolomna_font(metrics.fs_body, QFont.Weight.ExtraBold))
                value.setStyleSheet(f"color: {GREEN}; background: transparent;")
            else:
                value.setFont(kolomna_font(metrics.fs_body, QFont.Weight.ExtraBold))
                value.setStyleSheet(f"color: {GREEN}; background: transparent;")
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setAlignment(Qt.AlignmentFlag.AlignBottom)
            row.setSpacing(scale(18, metrics.width))
            k = QLabel(f"{label}:")
            k.setFont(kolomna_font(metrics.fs_label, QFont.Weight.Bold))
            k.setStyleSheet(f"color: {INK_60}; background: transparent;")
            row.addWidget(k)
            row.addWidget(value)
            contacts_lay.addLayout(row)
            self._contact_keys.append(k)
            self._contact_vals.append(value)

        box_lay.addWidget(contacts)

        qr_grid = _transparent()
        qr_lay = QGridLayout(qr_grid)
        qr_lay.setContentsMargins(0, scale(4, metrics.width), 0, 0)
        qr_lay.setHorizontalSpacing(scale(56, metrics.width))
        qr_lay.setVerticalSpacing(scale(40, metrics.width))
        qrs = [
            ("https://sadkolomna.ru/", "site", S.QR_SITE),
            ("https://t.me/sadkolomna", "tg", S.QR_TG),
            ("https://vk.com/sadkolomna1", "vk", S.QR_VK),
            ("https://clck.ru/3TAxXz", "max", S.QR_MAX),
        ]
        self._qr_tiles: list[KolomnaQrTile] = []
        for i, (url, logo, cap) in enumerate(qrs):
            tile = KolomnaQrTile(url, cap, metrics, logo=logo)
            self._qr_tiles.append(tile)
            qr_lay.addWidget(tile, i // 2, i % 2, Qt.AlignmentFlag.AlignCenter)
        box_lay.addWidget(qr_grid, alignment=Qt.AlignmentFlag.AlignHCenter)

        dev = QFrame()
        dev.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        dev.setStyleSheet(
            f"QFrame {{ border: none; border-top: 1px solid {CREAM_DEEP}; "
            f"background: transparent; margin-top: {scale(18, metrics.width)}px; "
            f"padding-top: {scale(28, metrics.width)}px; "
            f"margin-bottom: {scale(12, metrics.width)}px; }}"
        )
        dev_lay = QHBoxLayout(dev)
        dev_lay.setContentsMargins(0, 0, 0, 0)
        dev_lay.setSpacing(scale(7, metrics.width))
        dev_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dev_muted = "rgba(31,77,42,0.5)"
        self._dev_lead = QLabel(S.DEV_TITLE)
        self._dev_lead.setFont(kolomna_font(scale(18, metrics.width), QFont.Weight.Normal))
        self._dev_lead.setStyleSheet(f"color: {dev_muted}; background: transparent;")

        b = QLabel("B")
        b.setFont(kolomna_font(scale(15, metrics.width), QFont.Weight.Normal))
        b.setStyleSheet(
            f"color: {dev_muted}; background: transparent; letter-spacing: -0.26px;"
        )
        word = QLabel("üro")
        word.setFont(kolomna_font(scale(18, metrics.width), QFont.Weight.Normal))
        word.setStyleSheet(
            f"color: {dev_muted}; background: transparent; letter-spacing: -0.26px;"
        )
        num = QLabel("901")
        num.setFont(kolomna_font(scale(18, metrics.width), QFont.Weight.Normal))
        num.setStyleSheet(
            f"color: {dev_muted}; background: transparent; letter-spacing: -0.18px; "
            f"margin-left: {scale(3, metrics.width)}px;"
        )

        self._dev_meta = QLabel(f"· {S.DEV_PHONE} · {S.DEV_SITE}")
        self._dev_meta.setFont(kolomna_font(scale(18, metrics.width), QFont.Weight.Normal))
        self._dev_meta.setStyleSheet(f"color: {dev_muted}; background: transparent;")
        dev_lay.addWidget(self._dev_lead)
        dev_lay.addWidget(b)
        dev_lay.addWidget(word)
        dev_lay.addWidget(num)
        dev_lay.addWidget(self._dev_meta)
        box_lay.addWidget(dev)

        outer.addWidget(self._box, alignment=Qt.AlignmentFlag.AlignCenter)
        self._qr_caps = (S.QR_SITE, S.QR_TG, S.QR_VK, S.QR_MAX)

    def retranslate(self) -> None:
        self._title.setText(S.INFO_TITLE)
        labels = (S.INFO_HOURS_LABEL, S.INFO_PHONE_LABEL, S.INFO_SITE_LABEL)
        values = (self._hours, S.INFO_PHONE, S.INFO_SITE)
        for key_lbl, label, val_lbl, val in zip(
            self._contact_keys, labels, self._contact_vals, values, strict=True
        ):
            key_lbl.setText(f"{label}:")
            if val_lbl is self._hours_label:
                val_lbl.setText(self._hours)
            else:
                val_lbl.setText(val)
        self._qr_caps = (S.QR_SITE, S.QR_TG, S.QR_VK, S.QR_MAX)
        for tile, cap in zip(self._qr_tiles, self._qr_caps, strict=True):
            tile.set_label(cap)
        self._dev_lead.setText(S.DEV_TITLE)
        self._dev_meta.setText(f"· {S.DEV_PHONE} · {S.DEV_SITE}")

    def set_qr_pixmaps(self, pixmaps) -> None:
        for tile, pix in zip(self._qr_tiles, pixmaps):
            tile.set_qr_pixmap(pix)

    def set_hours(self, hours: str) -> None:
        self._hours = hours
        self._hours_label.setText(hours)

    def _position_close(self) -> None:
        top = scale(32, self._m.width)
        right = scale(32, self._m.width)
        sz = self._close.width()
        self._close.move(max(0, self._box.width() - right - sz), top)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if obj is self._box and event.type() == QEvent.Type.Resize:
            self._position_close()
        return super().eventFilter(obj, event)

    def show_modal(self) -> None:
        self.setGeometry(0, 0, self.parentWidget().width(), self.parentWidget().height())
        self._position_close()
        self.raise_()
        self.show()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            top_left = self._box.mapTo(self, self._box.rect().topLeft())
            box_rect = self._box.rect()
            box_rect.moveTopLeft(top_left)
            if not box_rect.contains(pos):
                self.hide()
        super().mouseReleaseEvent(event)
